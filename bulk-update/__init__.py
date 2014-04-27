from collections import defaultdict

from django.db import connections
from django.db.models.fields import AutoField


def bulk_update(objs, update_fields=None, exclude_fields=None,
                using='default'):
    if not objs:
        return

    ref_obj = objs[0]
    meta = ref_obj._meta
    update_fields = update_fields or meta.get_all_field_names()
    fields = filter(
        lambda f: not isinstance(f, AutoField) and f.attname in update_fields,
        meta.fields)
    fields = filter(lambda f: not f.attname in exclude_fields, fields)

    def _construct_case_sql(update_clauses, pkcolumn):
        sql = ""
        paramaters = []
        for field_column, cases in update_clauses.items():
            sql += "%s = (CASE %s" % (field_column, pkcolumn)
            for pk, value in cases.items():
                sql += " WHEN %s THEN %s"
                paramaters.append(pk)
                paramaters.append(value)
            sql += " END), "
        return sql.rstrip(', '), paramaters

    pks = []
    connection = connections[using]
    update_clauses = defaultdict(dict)
    for obj in objs:
        pk = obj.pk
        pks.append(pk)
        for field in fields:
            field_value = getattr(obj, field.attname)
            update_clauses[field.column].update({pk: field_value})

    pkcolumn = meta.pk.column
    dbtable = meta.db_table
    values, paramaters = _construct_case_sql(update_clauses, pkcolumn)

    sql = "UPDATE %s SET " % dbtable + values + " WHERE %s" % pkcolumn
    sql += " in %s"

    connection.cursor().execute(sql, paramaters + [tuple(pks)])
