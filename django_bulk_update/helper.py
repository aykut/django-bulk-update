# coding: utf8
"""
Main module with the bulk_update function.
"""
import itertools

from collections import defaultdict

from django.db import connections, models
from django.db.models.query import QuerySet
from django.db.models.sql import UpdateQuery
from django.db.models.sql import InsertQuery


def _get_db_type(field, connection):
    if isinstance(field, (models.PositiveSmallIntegerField,
                          models.PositiveIntegerField)):
        # integer CHECK ("points" >= 0)'
        return field.db_type(connection).split(' ', 1)[0]

    return field.db_type(connection)


def _as_sql(obj, field, query, compiler, connection):
    value = getattr(obj, field.attname)

    if hasattr(value, 'resolve_expression'):
        value = value.resolve_expression(query, allow_joins=False, for_save=True)
    else:
        value = field.get_db_prep_save(value, connection=connection)

    if hasattr(value, 'as_sql'):
        placeholder, value = compiler.compile(value)
        if isinstance(value, list):
            value = tuple(value)
    else:
        placeholder = '%s'

    return value, placeholder


def flatten(l, types=(list, float)):
    """
    Flat nested list of lists into a single list.
    """
    l = [item if isinstance(item, types) else [item] for item in l]
    return [item for sublist in l for item in sublist]


def grouper(iterable, size):
    # http://stackoverflow.com/a/8991553
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


def validate_fields(meta, fields):

    fields = frozenset(fields)
    field_names = set()

    for field in meta.fields:
        if not field.primary_key:
            field_names.add(field.name)

            if field.name != field.attname:
                field_names.add(field.attname)

    non_model_fields = fields.difference(field_names)

    if non_model_fields:
        raise TypeError(
            "These fields are not present in "
            "current meta: {}".format(', '.join(non_model_fields))
        )


def get_fields(update_fields, exclude_fields, meta, obj=None):

    deferred_fields = set()

    if update_fields is not None:
        validate_fields(meta, update_fields)
    elif obj:
        deferred_fields = obj.get_deferred_fields()

    if exclude_fields is None:
        exclude_fields = set()
    else:
        exclude_fields = set(exclude_fields)
        validate_fields(meta, exclude_fields)

    exclude_fields |= deferred_fields

    fields = [
        field
        for field in meta.concrete_fields
        if (
            not field.primary_key and
            field.attname not in deferred_fields and
            field.attname not in exclude_fields and
            field.name not in exclude_fields and
            (
                update_fields is None or
                field.attname in update_fields or
                field.name in update_fields
            )
        )
    ]
    return fields


def get_unique_together(meta):
    unique_together = meta.unique_together
    if len(unique_together) > 1:
        raise NotImplementedError('Only one unique together supported')
    elif len(unique_together) == 0:
        # TODO don't assume that id is primary_key
        unique_together = (('id'),)
    uniques = unique_together[0]
    all_fields = meta.fields
    unique_columns = []
    for field in all_fields:
        if field.name in uniques:
            unique_columns.append(field.column)
    return unique_columns


def bulk_update_or_create(objs, meta=None, update_fields=None, exclude_fields=None,
                          using='default', batch_size=None, pk_field='pk'):
    assert batch_size is None or batch_size > 0

    # force to retrieve objs from the DB at the beginning,
    # to avoid multiple subsequent queries
    objs = list(objs)
    if not objs:
        return
    batch_size = batch_size or len(objs)

    if meta:
        fields = get_fields(update_fields, exclude_fields, meta)
    else:
        meta = objs[0]._meta
        if update_fields is not None:
            fields = get_fields(update_fields, exclude_fields, meta, objs[0])
        else:
            fields = None

    if fields is not None:
        fields = get_fields(update_fields, exclude_fields, meta, objs[0])
    else:
        fields = None

    if fields is not None and len(fields) == 0:
        return

    if pk_field == 'pk':
        pk_field = meta.get_field(meta.pk.name)
    else:
        pk_field = meta.get_field(pk_field)

    connection = connections[using]
    query = InsertQuery(meta.model)
    compiler = query.get_compiler(connection=connection)
    vendor = connection.vendor

    unique_column_names = get_unique_together(meta)

    if vendor != 'postgresql':
        raise NotImplementedError('Only postgresql supported atm.')

    for objs_batch in grouper(objs, batch_size):
        parameters = []
        pks = []

        for obj in objs_batch:
            pk_value, _ = _as_sql(obj, pk_field, query, compiler, connection)
            if pk_value is not None:
                pks.append(pk_value)

        _model = meta.concrete_model
        objs_for_update = _model.objects.filter(pk__in=pks)
        updated_pks = {obj.pk for obj in objs_for_update}
        update_objs_has_values = [obj for obj in objs_batch if obj.pk in updated_pks]

        bulk_update(update_objs_has_values,
                    meta=meta,
                    update_fields=update_fields,
                    exclude_fields=exclude_fields,
                    batch_size=batch_size)

        objs_to_insert = [obj for obj in objs_batch if obj.pk not in updated_pks]
        if len(objs_to_insert) == 0:
            # no inserts needed
            return

        for obj in objs_to_insert:
            object_row = []
            for field in meta.concrete_fields:
                if field.column == 'id':
                    # TODO don't assume that id is primary_key
                    if field.db_type(connection) == 'serial':
                        # for the insert we want to make sure we have a new pk field.
                        object_row.append('DEFAULT')
                    else:
                        # assuming that it will an uuid function
                        object_row.append(field.default())
                    continue

                value, _ = _as_sql(obj, field, query, compiler, connection)

                if value is None:
                    value = 'NULL'
                object_row.append(value)
            parameters.append(tuple(object_row))

        # new templates
        unique_columns = ', '.join(['"{}"'.format(field) for field in unique_column_names])

        dbtable = '"{}"'.format(meta.db_table)
        excluded = '{field}=EXCLUDED.{field}'
        unique_templ = '{dbtable}.' + excluded
        unique_constraint = ' AND '.join([unique_templ.format(field=field, dbtable=meta.db_table)
                                          for field in unique_column_names])
        update_fields = ', '.join([excluded.format(field=field.column)
                                  for field in fields])

        def format_for_sql(tup):
            params = ', '.join(["'{}'".format(p) for p in tup])
            return '({})'.format(params)

        values = ', '.join([format_for_sql(p) for p in parameters])
        # default should be treated as a keyword, not a string
        values = values.replace("'DEFAULT'", 'DEFAULT')
        values = values.replace("'NULL'", 'NULL')
        all_fields = ', '.join(['"{}"'.format(field.column) for field in meta.concrete_fields])

        sql_insert = '''
            INSERT INTO {dbtable} ({all_fields}) VALUES {all_values}
            ON CONFLICT ({unique_fields}) DO UPDATE
            SET {update_fields} -- need to fix excluded
            WHERE {unique_constraint}
        '''.format(
            dbtable=dbtable,
            all_fields=all_fields,
            all_values=values,
            unique_fields=unique_columns,
            update_fields=update_fields,
            unique_constraint=unique_constraint
        )

        del values

        with connection.cursor() as cursor:
            cursor.execute(sql_insert)


def bulk_update(objs, meta=None, update_fields=None, exclude_fields=None,
                using='default', batch_size=None, pk_field='pk'):
    assert batch_size is None or batch_size > 0

    # force to retrieve objs from the DB at the beginning,
    # to avoid multiple subsequent queries
    objs = list(objs)
    if not objs:
        return
    batch_size = batch_size or len(objs)

    if meta:
        fields = get_fields(update_fields, exclude_fields, meta)
    else:
        meta = objs[0]._meta
        if update_fields is not None:
            fields = get_fields(update_fields, exclude_fields, meta, objs[0])
        else:
            fields = None

    if fields is not None and len(fields) == 0:
        return

    if pk_field == 'pk':
        pk_field = meta.get_field(meta.pk.name)
    else:
        pk_field = meta.get_field(pk_field)

    connection = connections[using]
    query = UpdateQuery(meta.model)
    compiler = query.get_compiler(connection=connection)

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
        template = '"{column}" = CAST(CASE "{pk_column}" {cases}ELSE "{column}" END AS {type})'
    else:
        template = '"{column}" = (CASE "{pk_column}" {cases}ELSE "{column}" END)'

    case_template = "WHEN %s THEN {} "

    lenpks = 0
    for objs_batch in grouper(objs, batch_size):

        pks = []
        parameters = defaultdict(list)
        placeholders = defaultdict(list)

        for obj in objs_batch:

            pk_value, _ = _as_sql(obj, pk_field, query, compiler, connection)
            pks.append(pk_value)

            loaded_fields = fields or get_fields(update_fields, exclude_fields, meta, obj)

            for field in loaded_fields:
                value, placeholder = _as_sql(obj, field, query, compiler, connection)
                parameters[field].extend(flatten([pk_value, value], types=tuple))
                placeholders[field].append(placeholder)

        values = ', '.join(
            template.format(
                column=field.column,
                pk_column=pk_field.column,
                cases=(case_template*len(placeholders[field])).format(*placeholders[field]),
                type=_get_db_type(field, connection=connection),
            )
            for field in parameters.keys()
        )

        parameters = flatten(parameters.values(), types=list)
        parameters.extend(pks)

        n_pks = len(pks)
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
        # Unfortunately, this escaping method is not portable to MySQL,
        # unless it is set in ANSI compatibility mode.
        if 'mysql' in vendor:
            sql = sql.replace('"', '`')

        lenpks += n_pks

        connection.cursor().execute(sql, parameters)

    return lenpks
