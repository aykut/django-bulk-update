from collections import defaultdict

from django.db import connections
from django.db.models.fields import AutoField
from django.utils.functional import SimpleLazyObject


def bulk_update(objs, update_fields=None, exclude_fields=None,
                using='default', batch_size=None):
    assert batch_size is None or batch_size > 0
    if not objs:
        return

    batch_size = batch_size or len(objs)

    ref_obj = objs[0]
    meta = ref_obj._meta
    exclude_fields = exclude_fields or []
    update_fields = update_fields or meta.get_all_field_names()
    fields = filter(
        lambda f: not isinstance(f, AutoField) and f.attname in update_fields,
        meta.fields)
    fields = filter(lambda f: not f.attname in exclude_fields, fields)

    pks = []
    paramaters = []
    connection = connections[using]
    case_clauses = defaultdict(str)
    for obj in objs:
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
