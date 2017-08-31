import itertools

from collections import defaultdict

from django.db import connections, models
from django.db.models.sql import UpdateQuery

from .utils import grouper, flatten


def _get_db_type(field, connection):
    if isinstance(field, (models.PositiveSmallIntegerField,
                          models.PositiveIntegerField)):
        # integer CHECK ("points" >= 0)'
        return field.db_type(connection).split(' ', 1)[0]

    return field.db_type(connection)


def _as_sql(obj, field, query, compiler, connection):
    value = getattr(obj, field.attname)

    if hasattr(value, 'resolve_expression'):
        value = value.resolve_expression(query, allow_joins=False,
                                         for_save=True)
    else:
        value = field.get_db_prep_save(value, connection=connection)

    if hasattr(value, 'as_sql'):
        placeholder, value = compiler.compile(value)
        if isinstance(value, list):
            value = tuple(value)
    else:
        placeholder = '%s'

    return value, placeholder


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


def get_sql_template(vendor):
    # The case clause template; db-dependent
    # Apparently, mysql's castable types are very limited and have
    # nothing to do with the column types. Still, it handles the uncast
    # types well enough... hopefully.
    # http://dev.mysql.com/doc/refman/5.5/en/cast-functions.html#function_cast
    #
    # Sqlite also gives some trouble with cast, at least for datetime,
    # but is also permissive for uncast values
    template = '"{column}" = CAST(' \
        'CASE "{pk_column}" {cases}ELSE "{column}" END AS {type})'
    if 'mysql' in vendor or 'sqlite' in vendor:
        template = '"{column}" = (' \
            'CASE "{pk_column}" {cases}ELSE "{column}" END)'

    return template


def get_pk_field(pk_field, meta):
    if pk_field == 'pk':
        pk_field = meta.get_field(meta.pk.name)
    else:
        pk_field = meta.get_field(pk_field)

    return pk_field


def bulk_update(objs, batch_size=None, update_fields=None, exclude_fields=None,
                using='default', pk_field='pk'):
    assert batch_size is None or batch_size > 0
    assert update_fields is None or len(update_fields) > 0

    lenpks = 0
    connection = connections[using]
    for i, chunk in enumerate(grouper(objs, batch_size)):
        pks = []
        parameters = defaultdict(list)
        placeholders = defaultdict(list)
        for j, obj in enumerate(chunk):
            if i == 0 and j == 0:
                meta = obj._meta
                fields = get_fields(update_fields, exclude_fields, meta, obj)
                pk_field = get_pk_field(pk_field, meta)

                query = UpdateQuery(meta.model)
                compiler = query.get_compiler(connection=connection)

                template = get_sql_template(connection.vendor)
                case_template = "WHEN %s THEN {} "

            pk_value, _ = _as_sql(obj, pk_field, query, compiler, connection)
            pks.append(pk_value)

            for field in fields:
                value, placeholder = _as_sql(obj, field, query,
                                             compiler, connection)
                parameters[field].extend(flatten([pk_value, value],
                                                 types=tuple))
                placeholders[field].append(placeholder)

        values = ', '.join(
            template.format(
                column=field.column,
                pk_column=pk_field.column,
                cases=(case_template*len(placeholders[field])).format(*placeholders[field]),  # NOQA
                type=_get_db_type(field, connection=connection),
            )
            for field in parameters.keys()
        )

        parameters = flatten(parameters.values(), types=list)
        parameters.extend(pks)

        n_pks = (j + 1)
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
        if 'mysql' in connection.vendor:
            sql = sql.replace('"', '`')

        lenpks += n_pks

        connection.cursor().execute(sql, parameters)

    return lenpks
