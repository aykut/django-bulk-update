# coding: utf8
"""
Main module with the bulk_update function.
"""

import itertools

from django.db import connections, models
from django.db.models.query import QuerySet
"""adding the following to allow Bulk_update to be ran with scripts that are standalone 
(aka not being triggered by webserver or django-admin.py)
See: https://docs.djangoproject.com/en/1.8/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
"""
import django
from django.utils.version import get_version
## need Version check - if Django version >= 1.8 then we need the following code due to 1.8 changes.
if django.VERSION[1] > 6:
    #call django.setup() to properly assign models. Prevents the 'Models are not loaded' error
    django.setup()
    
    
def _get_db_type(field, connection):
    if isinstance(field, (models.PositiveSmallIntegerField,
                          models.PositiveIntegerField)):
        # integer CHECK ("points" >= 0)'
        return field.db_type(connection).split(' ', 1)[0]

    res = field.db_type(connection)
    return res


def grouper(iterable, size):
    # http://stackoverflow.com/a/8991553
    it = iter(iterable)
    if size <= 0:
        yield it
        return
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


def bulk_update(objs, meta=None, update_fields=None, exclude_fields=None,
                using='default', batch_size=None, pk_field='pk'):
    assert batch_size is None or batch_size > 0

    # if we have a QuerySet, avoid loading objects into memory
    if isinstance(objs, QuerySet):
        batch_size = batch_size or objs.count()
    else:
        batch_size = batch_size or len(objs)

    connection = connections[using]
    if meta is None:
        # TODO: account for iterables
        meta = objs[0]._meta

    if pk_field == 'pk':
        pk_field = meta.pk.name

    exclude_fields = exclude_fields or []
    update_fields = update_fields or meta.get_all_field_names()
    fields = [
        f for f in meta.fields
        if ((not isinstance(f, models.AutoField))
            and (f.attname in update_fields))]
    fields = [
        f for f in fields
        if f.attname not in exclude_fields]

    # The case clause template; db-dependent
    # Apparently, mysql's castable types are very limited and have
    # nothing to do with the column types. Still, it handles the uncast
    # types well enough... hopefully.
    # http://dev.mysql.com/doc/refman/5.5/en/cast-functions.html#function_cast
    #
    # Sqlite also gives some trouble with cast, at least for datetime,
    # but is also permissive for uncast values
    vendor = connection.vendor
    use_cast = 'mysql' not in vendor and 'sqlite' not in connection.vendor
    if use_cast:
        case_clause_template = '"{column}" = CAST(CASE "{pkcolumn}" {{when}}'
        tail_end_template = 'END AS {type})'
    else:
        case_clause_template = '"{column}" = (CASE "{pkcolumn}" {{when}}'
        tail_end_template = 'END)'

    # String escaping in ANSI SQL is done by using double quotes (").
    # Unfortunately, this escaping method is not portable to MySQL, unless it
    # is set in ANSI compatibility mode.
    quote_mark = '"' if 'mysql' not in vendor else '`'
    case_clause_template = case_clause_template.replace('"', quote_mark)

    for objs_batch in grouper(objs, batch_size):
        pks = []
        case_clauses = {}
        for obj in objs_batch:
            pks.append(getattr(obj, pk_field))
            for field in fields:
                column = field.column

                # Synopsis: make sure the column-specific 'case'
                # exists and then append the obj-specific values to
                # it in a tricky way (leaving ' {when}' at the end).
                # TODO?: For speed, use a list to be ''-joined later,
                # instead? Or a bytearray.
                # TODO: optimise (getitem+setitem vs. get + setitem)
                try:
                    case_clause = case_clauses[column]
                except KeyError:
                    case_clause = {
                        'sql': case_clause_template.format(
                            column=column, pkcolumn=meta.get_field(pk_field).column),
                        'params': [],
                        'type': _get_db_type(field, connection=connection),
                    }
                    case_clauses[column] = case_clause

                case_clause['sql'] = (
                    case_clause['sql'].format(when="WHEN %s THEN %s {when}")
                )

                case_clause['params'].extend(
                    [getattr(obj, pk_field),
                     field.get_db_prep_value(
                         getattr(obj, field.attname), connection)])

        if pks:
            values = ', '.join(
                v['sql'].format(when=tail_end_template.format(type=v['type']))
                for v in case_clauses.values())
            parameters = [
                param
                for clause in case_clauses.values()
                for param in clause['params']]

            del case_clauses  # ... memory

            pkcolumn = meta.get_field(pk_field).column
            dbtable = '{0}{1}{0}'.format(quote_mark, meta.db_table)
            # Storytime: apparently (at least for mysql and sqlite), if a
            # non-simple parameter is added (e.g. a tuple), it is
            # processed with force_text and, accidentally, manages to
            # be a valid syntax... unless there's only one element.
            # So, to fix this, expand the ' in %s' with the parameters' string
            in_clause_sql = '({})'.format(
                ', '.join(itertools.repeat('%s', len(pks))))
            parameters.extend(pks)

            sql = (
                'UPDATE {dbtable} SET {values} WHERE {pkcolumn} '
                'in {in_clause_sql}'
                .format(
                    dbtable=dbtable, values=values, pkcolumn=pkcolumn,
                    in_clause_sql=in_clause_sql))
            del values, pks

            connection.cursor().execute(sql, parameters)
