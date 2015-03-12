from collections import defaultdict

from django.db import connections, models
from django.utils.functional import SimpleLazyObject


def bulk_update(objs, update_fields=None, exclude_fields=None,
                using='default', batch_size=None):
    assert batch_size is None or batch_size > 0

    batch_size = batch_size or len(objs)
    connection = connections[using]
    ref_obj = objs[0]
    meta = ref_obj._meta
    exclude_fields = exclude_fields or []
    update_fields = update_fields or meta.get_all_field_names()
    fields = list(filter(
        lambda f: (not isinstance(f, models.AutoField)) and
                  (f.attname in update_fields),
        meta.fields))
    fields = list(filter(lambda f: not f.attname in exclude_fields, fields))
	
    def _batched_update(objs, fields, batch_size, connection):
        def _get_db_type(field):
            if isinstance(field, (models.PositiveSmallIntegerField,
                                  models.PositiveIntegerField)):
                return field.db_type(connection).split(' ', 1)[0]
            elif isinstance(field, (models.DateTimeField, models.DateField)) and connection.vendor == 'sqlite':
                return 'text' # otherwise it turns 2015-03-10 to 2015
            return field.db_type(connection)

        pks = []
        case_clauses = defaultdict(dict)
        for obj in objs[:batch_size]:
            pks.append(obj.pk)
            for field in fields:
                column = field.column
                _default = SimpleLazyObject(
                    lambda: '{column} = CAST(CASE {pkcolumn} {{when}}'.format(
                        column=column, pkcolumn=meta.pk.column))

                case_clauses.setdefault(
                    column, {
                        'sql': _default,
                        'params': [],
                        'type': _get_db_type(field)
                    }
                )

                case_clauses[column]['sql'] = case_clauses[column]['sql']\
                    .format(when="WHEN %s THEN %s {when}")

                case_clauses[column]['params'].extend(
                    [obj.pk, field.get_db_prep_value(
                        getattr(obj, field.attname), connection)])

        if pks:
            values = ', '.join(
                map(lambda v: v['sql'].format(when=' END AS %s)' % v['type']),
                    case_clauses.values()))
            parameters = [item for v in case_clauses.values()
                          for item in v['params']]
            del case_clauses

            pkcolumn = meta.pk.column
            dbtable = meta.db_table
            parameters.extend(pks)

            sql = 'UPDATE {dbtable} SET {values} WHERE {pkcolumn} in ({inclause})'\
                .format(dbtable=dbtable, values=values, pkcolumn=pkcolumn, inclause=','.join([' %s'] * len(pks) ))
            del values, pks

            connection.cursor().execute(sql, parameters)

            _batched_update(objs[batch_size:], fields, batch_size, connection)

    _batched_update(objs, fields, batch_size, connection)
