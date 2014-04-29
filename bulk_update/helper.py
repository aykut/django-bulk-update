from collections import defaultdict

from django.db import connections
from django.db.models.fields import AutoField


def bulk_update(objs, update_fields=None, exclude_fields=None,
                using='default'):
    if not objs:
        return

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
            default = case_clauses.setdefault(
                field.column, '{column} = (CASE {pkcolumn} {{when}}'.format(
                    column=field.column, pkcolumn=meta.pk.column))
            case_clauses[field.column] = default.format(
                when="WHEN %s THEN %s {when}")
            paramaters.extend([obj.pk, getattr(obj, field.attname)])

    values = ', '.join(
        map(lambda x: x.format(when=' END)'), case_clauses.values()))

    pkcolumn = meta.pk.column
    dbtable = meta.db_table
    paramaters.extend([tuple(pks)])

    sql = "UPDATE %(dbtable)s SET %(values)s WHERE %(pkcolumn)s" % {
        'dbtable': dbtable, 'values': values, 'pkcolumn': pkcolumn}
    sql += " in %s"

    connection.cursor().execute(sql, paramaters)
