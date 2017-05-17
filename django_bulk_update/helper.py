# coding: utf8
"""
Main module with the bulk_update function.
"""

import itertools

from collections import defaultdict

from django.db import connections, models
from django.db.models.query import QuerySet


def _get_db_type(field, connection):
    if isinstance(field, (models.PositiveSmallIntegerField,
                          models.PositiveIntegerField)):
        # integer CHECK ("points" >= 0)'
        return field.db_type(connection).split(' ', 1)[0]

    return field.db_type(connection)


def _get_db_prep_value(obj, field, connection):
    return field.get_db_prep_value(getattr(obj, field.attname), connection)


def flatten(l):
    """
    Flat nested list of lists into a single list.
    """
    return [item for sublist in l for item in sublist]


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


def validate_fields(meta, fields):
    meta_fields = [f.attname for f in meta.fields]
    meta_fields += [f[:-3] for f in meta_fields if f.endswith('_id')]
    invalid_fields = []
    for field in fields or []:
        if field not in meta_fields:
            invalid_fields.append(field)
    if invalid_fields:
        raise TypeError(u'These fields are not present in '
                        'current meta: {}'.format(', '.join(invalid_fields)))


def bulk_update(objs, meta=None, update_fields=None, exclude_fields=None,
                using='default', batch_size=None, pk_field='pk'):
    assert batch_size is None or batch_size > 0

    # if we have a QuerySet, avoid loading objects into memory
    if isinstance(objs, QuerySet):
        if not objs.exists():
            return
        batch_size = batch_size or objs.count()
    else:
        if not objs:
            return
        batch_size = batch_size or len(objs)

    connection = connections[using]
    if meta is None:
        # TODO: account for iterables
        meta = objs[0]._meta

    if pk_field == 'pk':
        pk_field = meta.get_field(meta.pk.name)
    else:
        pk_field = meta.get_field(pk_field)

    exclude_fields = exclude_fields or []
    update_fields = update_fields or [f.attname for f in meta.fields]
    validate_fields(meta, update_fields + exclude_fields)
    fields = [
        f for f in meta.fields
        if ((not isinstance(f, models.AutoField))
            and ((f.attname in update_fields) or
                 (f.attname.endswith('_id') and
                  f.attname[:-3] in update_fields)))]
    fields = [
        f for f in fields
        if ((f.attname not in exclude_fields) or
            (f.attname.endswith('_id') and
             f.attname[:-3] not in exclude_fields))]

    # The case clause template; db-dependent
    # Apparently, mysql's castable types are very limited and have
    # nothing to do with the column types. Still, it handles the uncast
    # types well enough... hopefully.
    # http://dev.mysql.com/doc/refman/5.5/en/cast-functions.html#function_cast
    #
    # Sqlite also gives some trouble with cast, at least for datetime,
    # but is also permissive for uncast values
    vendor = connection.vendor
    use_cast = 'mysql' not in vendor and 'sqlite' not in vendor
    if use_cast:
        template = '"{column}" = CAST(CASE "{pk_column}" {cases}END AS {type})'
    else:
        template = '"{column}" = (CASE "{pk_column}" {cases}END)'

    case_template = "WHEN %s THEN %s "

    lenpks = 0
    for objs_batch in grouper(objs, batch_size):

        pks = []
        parameters = defaultdict(list)

        for obj in objs_batch:

            pk_value = _get_db_prep_value(obj, pk_field, connection)
            pks.append(pk_value)

            for field in fields:
                value = _get_db_prep_value(obj, field, connection)
                parameters[field].extend([pk_value, value])

        if pks:

            n_pks = len(pks)

            values = ', '.join(
                template.format(
                    column=field.column,
                    pk_column=pk_field.column,
                    cases=case_template*n_pks,
                    type=_get_db_type(field, connection=connection),
                )
                for field in parameters.keys()
            )

            parameters = flatten(parameters.values())
            parameters.extend(pks)
            del pks

            dbtable = '"{}"'.format(meta.db_table)

            in_clause = '"{pk_column}" in ({pks})'.format(
                pk_column=pk_field.column,
                pks=', '.join(itertools.repeat('%s', n_pks)),
            )

            sql = 'UPDATE {dbtable} SET {values} WHERE {in_clause}'.format(
                dbtable=dbtable,
                values=values,
                in_clause=in_clause,
            )
            del values

            # String escaping in ANSI SQL is done by using double quotes (").
            # Unfortunately, this escaping method is not portable to MySQL, unless it
            # is set in ANSI compatibility mode.
            if 'mysql' in vendor:
                sql = sql.replace('"', '`')

            lenpks += n_pks

            connection.cursor().execute(sql, parameters)

    return lenpks
