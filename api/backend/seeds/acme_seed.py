import json
import os
import sys
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django  # noqa: E402

django.setup()

from django.db import connection, transaction  # noqa: E402


TARGET_SCHEMA = "acme"
ROWS_PER_TABLE = 3
REPORT_PATH = os.path.join(os.path.dirname(__file__), "acme_schema_report.json")
RUN_SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "acme_seed_run_summary.json")
MAX_TABLES = int(os.getenv("ACME_SEED_MAX_TABLES", "0"))


@dataclass
class ColumnMeta:
    table: str
    name: str
    data_type: str
    udt_name: str
    is_nullable: bool
    default: Any
    ordinal: int
    char_len: int | None
    num_precision: int | None
    num_scale: int | None
    is_identity: bool


def qident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def clip_text(value: str, max_len: int | None) -> str:
    if max_len and len(value) > max_len:
        return value[:max_len]
    return value


def fetch_all(sql: str, params: list[Any] | tuple[Any, ...] | None = None):
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_tables() -> list[str]:
    rows = fetch_all(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type='BASE TABLE'
        ORDER BY table_name
        """,
        [TARGET_SCHEMA],
    )
    return [r["table_name"] for r in rows]


def get_columns(table: str) -> list[ColumnMeta]:
    rows = fetch_all(
        """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.udt_name,
            c.is_nullable,
            c.column_default,
            c.ordinal_position,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.is_identity
        FROM information_schema.columns c
        WHERE c.table_schema = %s AND c.table_name = %s
        ORDER BY c.ordinal_position
        """,
        [TARGET_SCHEMA, table],
    )
    return [
        ColumnMeta(
            table=r["table_name"],
            name=r["column_name"],
            data_type=r["data_type"],
            udt_name=r["udt_name"],
            is_nullable=(r["is_nullable"] == "YES"),
            default=r["column_default"],
            ordinal=r["ordinal_position"],
            char_len=r["character_maximum_length"],
            num_precision=r["numeric_precision"],
            num_scale=r["numeric_scale"],
            is_identity=(r["is_identity"] == "YES"),
        )
        for r in rows
    ]


def get_pk_columns(table: str) -> list[str]:
    rows = fetch_all(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s
          AND tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """,
        [TARGET_SCHEMA, table],
    )
    return [r["column_name"] for r in rows]


def get_unique_columns(table: str) -> set[str]:
    rows = fetch_all(
        """
        SELECT DISTINCT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s
          AND tc.table_name = %s
          AND tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
        """,
        [TARGET_SCHEMA, table],
    )
    return {r["column_name"] for r in rows}


def get_foreign_keys():
    rows = fetch_all(
        """
        SELECT
            tc.table_name AS table_name,
            kcu.column_name AS column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = %s
          AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name
        """,
        [TARGET_SCHEMA],
    )
    by_table = defaultdict(list)
    for r in rows:
        by_table[r["table_name"]].append(
            {
                "column": r["column_name"],
                "ref_table": r["foreign_table_name"],
                "ref_column": r["foreign_column_name"],
            }
        )
    return by_table


def get_enums() -> dict[str, list[str]]:
    rows = fetch_all(
        """
        SELECT t.typname AS enum_name, e.enumlabel AS enum_label
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = %s
        ORDER BY t.typname, e.enumsortorder
        """,
        [TARGET_SCHEMA],
    )
    out: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        out[r["enum_name"]].append(r["enum_label"])
    return out


def topological_sort(tables: list[str], fks: dict[str, list[dict[str, str]]]) -> list[str]:
    deps = {t: set() for t in tables}
    rev = {t: set() for t in tables}
    for t, refs in fks.items():
        for fk in refs:
            rt = fk["ref_table"]
            if rt in deps and rt != t:
                deps[t].add(rt)
                rev[rt].add(t)
    queue = deque([t for t in tables if not deps[t]])
    ordered: list[str] = []
    while queue:
        t = queue.popleft()
        ordered.append(t)
        for nxt in rev[t]:
            deps[nxt].discard(t)
            if not deps[nxt]:
                queue.append(nxt)
    for t in tables:
        if t not in ordered:
            ordered.append(t)
    return ordered


def value_for_column(
    table: str,
    col: ColumnMeta,
    i: int,
    uniques: set[str],
    fk_lookup: dict[tuple[str, str], list[Any]],
    fk_meta: dict[str, list[dict[str, str]]],
    enums: dict[str, list[str]],
):
    if col.is_identity:
        return None, True

    fk = next((x for x in fk_meta.get(table, []) if x["column"] == col.name), None)
    if fk:
        ref_vals = fk_lookup.get((fk["ref_table"], fk["ref_column"]), [])
        if ref_vals:
            return ref_vals[i % len(ref_vals)], False
        return None, col.default is not None or col.is_nullable

    lname = col.name.lower()
    dtype = col.data_type.lower()
    udt = col.udt_name.lower()
    unique = col.name in uniques
    suffix = f"{i+1}"

    if udt in enums and enums[udt]:
        return enums[udt][i % len(enums[udt])], False

    if dtype == "uuid":
        return str(uuid.uuid4()), False
    if dtype in ("character varying", "character", "text"):
        if "email" in lname:
            return clip_text(f"employee{suffix}.{table}@acme.com", col.char_len), False
        if "phone" in lname or "mobile" in lname:
            return clip_text(f"+91-98{(10000000 + i):08d}", col.char_len), False
        if "code" in lname:
            return (
                clip_text(
                    f"{table[:4].upper()}-{1000+i}" if unique else f"{table[:4].upper()}-{i+1}",
                    col.char_len,
                )
            ), False
        if "slug" in lname:
            return clip_text(f"{table}-{suffix}-{uuid.uuid4().hex[:6]}", col.char_len), False
        if "name" in lname:
            return clip_text(f"Acme {table.replace('_', ' ').title()} {suffix}", col.char_len), False
        if "address" in lname:
            return clip_text(f"{100+i} Innovation Park, Pune, Maharashtra", col.char_len), False
        if "city" in lname:
            return clip_text("Pune", col.char_len), False
        if "state" in lname:
            return clip_text("Maharashtra", col.char_len), False
        if "country" in lname:
            return clip_text("IN" if (col.char_len and col.char_len <= 2) else "India", col.char_len), False
        if "remarks" in lname or "description" in lname:
            return clip_text(f"Auto-seeded record {suffix} for {table}", col.char_len), False
        return clip_text(f"{table}_{col.name}_{suffix}", col.char_len), False
    if dtype in ("integer", "smallint", "bigint"):
        return i + 1, False
    if dtype in ("numeric", "decimal"):
        scale = col.num_scale or 0
        return Decimal(f"{10 + i}.{('1'*scale) if scale else '0'}"), False
    if dtype in ("real", "double precision"):
        return float(10 + i) + 0.5, False
    if dtype == "boolean":
        return (i % 2 == 0), False
    if dtype == "date":
        return date.today() - timedelta(days=(30 - i)), False
    if dtype in ("timestamp without time zone", "timestamp with time zone"):
        return datetime.utcnow() - timedelta(hours=i), False
    if dtype == "time without time zone":
        return time(9 + i, 0, 0), False
    if dtype == "jsonb" or dtype == "json":
        return json.dumps({"seeded": True, "table": table, "index": i + 1}), False
    if dtype == "ARRAY".lower() or udt.startswith("_"):
        return "{}", False
    if dtype == "bytea":
        return b"acme-seed", False

    return None, col.default is not None or col.is_nullable


def fetch_fk_reference_values(table: str, column: str) -> list[Any]:
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT {qident(column)} FROM {qident(TARGET_SCHEMA)}.{qident(table)} WHERE {qident(column)} IS NOT NULL LIMIT 100"
        )
        return [row[0] for row in cur.fetchall()]


def table_count(table: str) -> int:
    with connection.cursor() as cur:
        cur.execute(f"SELECT count(1) FROM {qident(TARGET_SCHEMA)}.{qident(table)}")
        return int(cur.fetchone()[0])


def insert_rows(
    table: str,
    columns: list[ColumnMeta],
    unique_cols: set[str],
    fk_meta: dict[str, list[dict[str, str]]],
    fk_lookup: dict[tuple[str, str], list[Any]],
    enums: dict[str, list[str]],
):
    inserted = 0
    for i in range(ROWS_PER_TABLE):
        payload: dict[str, Any] = {}
        for col in columns:
            value, skip = value_for_column(table, col, i, unique_cols, fk_lookup, fk_meta, enums)
            if skip:
                continue
            payload[col.name] = value
        if not payload:
            continue
        col_names = list(payload.keys())
        vals = [payload[c] for c in col_names]
        placeholders = ", ".join(["%s"] * len(col_names))
        sql = (
            f"INSERT INTO {qident(TARGET_SCHEMA)}.{qident(table)} "
            f"({', '.join(qident(c) for c in col_names)}) VALUES ({placeholders})"
        )
        with connection.cursor() as cur:
            cur.execute(sql, vals)
        inserted += 1
    return inserted


def clone_rows_to_three(table: str, columns: list[ColumnMeta], unique_cols: set[str]) -> int:
    current = table_count(table)
    if current >= ROWS_PER_TABLE or current == 0:
        return 0
    pk_cols = set(get_pk_columns(table))
    cloneable = [c for c in columns if not c.is_identity]
    inserted = 0
    while current + inserted < ROWS_PER_TABLE:
        with connection.cursor() as cur:
            cur.execute(f"SELECT * FROM {qident(TARGET_SCHEMA)}.{qident(table)} LIMIT 1")
            row = cur.fetchone()
            if not row:
                break
            col_names = [d[0] for d in cur.description]
        payload: dict[str, Any] = {}
        for c in cloneable:
            if c.name not in col_names:
                continue
            idx = col_names.index(c.name)
            val = row[idx]
            if c.name in pk_cols and c.data_type.lower() == "uuid":
                val = str(uuid.uuid4())
            elif c.name in unique_cols and isinstance(val, str):
                base = val.split("@")[0]
                if "@" in val:
                    domain = val.split("@", 1)[1]
                    val = clip_text(f"{base}.{uuid.uuid4().hex[:6]}@{domain}", c.char_len)
                else:
                    val = clip_text(f"{val}-{uuid.uuid4().hex[:6]}", c.char_len)
            elif isinstance(val, datetime):
                val = datetime.utcnow()
            elif isinstance(val, date):
                val = date.today()
            payload[c.name] = val
        if not payload:
            break
        col_list = list(payload.keys())
        vals = [payload[k] for k in col_list]
        sql = (
            f"INSERT INTO {qident(TARGET_SCHEMA)}.{qident(table)} "
            f"({', '.join(qident(c) for c in col_list)}) VALUES ({', '.join(['%s'] * len(col_list))})"
        )
        try:
            with connection.cursor() as cur:
                cur.execute(sql, vals)
            inserted += 1
        except Exception:
            break
    return inserted


def build_report(tables: list[str], fk_meta: dict[str, list[dict[str, str]]], enums: dict[str, list[str]]):
    report = {"schema": TARGET_SCHEMA, "tables": []}
    for table in tables:
        cols = get_columns(table)
        pks = get_pk_columns(table)
        uniques = sorted(get_unique_columns(table))
        report["tables"].append(
            {
                "table": table,
                "columns": [
                    {
                        "name": c.name,
                        "data_type": c.data_type,
                        "udt_name": c.udt_name,
                        "nullable": c.is_nullable,
                        "default": c.default,
                        "identity": c.is_identity,
                    }
                    for c in cols
                ],
                "primary_key": pks,
                "unique_columns": uniques,
                "foreign_keys": fk_meta.get(table, []),
            }
        )
    report["enums"] = enums
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)


def main():
    tables = get_tables()
    fk_meta = get_foreign_keys()
    enums = get_enums()
    build_report(tables, fk_meta, enums)

    ordered = topological_sort(tables, fk_meta)
    if MAX_TABLES > 0:
        ordered = ordered[:MAX_TABLES]

    print(f"Schema: {TARGET_SCHEMA}")
    print(f"Tables discovered: {len(tables)}")
    print(f"Seeding order: {len(ordered)} tables")

    fk_lookup: dict[tuple[str, str], list[Any]] = {}
    run_errors: list[dict[str, str]] = []
    run_counts: dict[str, int] = {}
    for table in ordered:
        cols = get_columns(table)
        pks = get_pk_columns(table)
        unique_cols = get_unique_columns(table)
        before = table_count(table)

        try:
            with transaction.atomic():
                inserted = insert_rows(table, cols, unique_cols, fk_meta, fk_lookup, enums)
        except Exception as exc:
            print(f"[ERROR] {table}: {exc}")
            print(traceback.format_exc())
            run_errors.append({"table": table, "error": str(exc)})
            run_counts[table] = table_count(table)
            continue

        after = table_count(table)
        cloned = clone_rows_to_three(table, cols, unique_cols)
        after = table_count(table)
        print(f"[OK] {table}: before={before}, inserted={inserted}, cloned={cloned}, after={after}")
        run_counts[table] = after

        candidate_cols = set(pks)
        for fk in fk_meta.get(table, []):
            candidate_cols.add(fk["column"])
        for col_name in candidate_cols:
            fk_lookup[(table, col_name)] = fetch_fk_reference_values(table, col_name)

    print(f"Schema report written: {REPORT_PATH}")

    print("Verification counts:")
    for t in ordered:
        cnt = table_count(t)
        run_counts[t] = cnt
        print(f" - {t}: {cnt}")

    under_three = [{"table": t, "count": c} for t, c in run_counts.items() if c < ROWS_PER_TABLE]
    run_summary = {
        "schema": TARGET_SCHEMA,
        "rows_per_table_target": ROWS_PER_TABLE,
        "tables_total": len(tables),
        "tables_processed": len(ordered),
        "errors_count": len(run_errors),
        "errors": run_errors,
        "tables_under_target_count": len(under_three),
        "tables_under_target": under_three,
    }
    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(run_summary, f, indent=2)
    print(f"Run summary written: {RUN_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
