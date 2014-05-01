from django.db import models
from .helper import bulk_update


class BulkUpdateManager(models.Manager):
    def bulk_update(self, objs, update_fields=None, exclude_fields=None):
        bulk_update(objs, update_fields=update_fields,
                    exclude_fields=exclude_fields, using=self.db)


def _batched_update(objs, fields, connection, batch_size):
    pks = []
    paramaters = []
    case_clauses = defaultdict(str)
    for obj in objs[:batch_size]:
        pks.append(obj.pk)
        for field in fields:
            _default = SimpleLazyObject(
                lambda: '{column} = (CASE {pkcolumn} {{when}}'.format(
                    column=field.column, pkcolumn=meta.pk.column))

            _tail = case_clauses.setdefault(field.column, _default)
            case_clauses[field.column] = _tail.format(
                when="WHEN %s THEN %s {when}")
            paramaters.extend([obj.pk, getattr(obj, field.attname)])

    values = ', '.join(
        map(lambda v: v.format(when=' END)'), case_clauses.values()))
    del case_clauses

    pkcolumn = meta.pk.column
    dbtable = meta.db_table
    paramaters.extend([tuple(pks)])

    sql = 'UPDATE {dbtable} SET {values} WHERE {pkcolumn} in %s'.format(
        dbtable=dbtable, values=values, pkcolumn=pkcolumn)
    del values, pks

    connection.cursor().execute(sql, paramaters)
