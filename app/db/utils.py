import re
import typing

import sqlalchemy as sa
from sqlalchemy import ClauseElement, Executable, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.selectable import Select

from app.models.base import BaseModel

"""
Inspired by:
    - Fast SQLAlchemy query results exact count
        - https://gist.github.com/hest/8798884
        - https://datawookie.dev/blog/2021/01/sqlalchemy-efficient-counting/
    - Fast SqlAlchemy query approx results count
        - https://gist.github.com/jmcarp/384310cb3925eaa3b3ca
    - Fast & safe SQL approx table row count
        - https://stackoverflow.com/a/7945274/19517403
"""


class ResultCount(typing.NamedTuple):
    """Result of counting operation."""

    count: int
    is_exact: bool


class SQLExplain(Executable, ClauseElement):
    """Explain query execution plan."""

    def __init__(self, stmt: Select, analyze: bool = False):
        self.statement = stmt
        self.analyze = analyze


@compiles(SQLExplain, "postgresql")
def pg_explain(element: SQLExplain, compiler: SQLCompiler, **kw):
    """Compile SQLExplain to SQL."""
    text = "EXPLAIN "
    if element.analyze:
        text += "ANALYZE "
    text += compiler.process(element.statement, **kw)
    return text


def extract_count_from_explain(rows: typing.Sequence) -> int:
    """
    Extract count from Explain output.
    Returns -1 if count cannot be extracted.
    """
    count_pattern = re.compile(r"rows=(\d+)")
    for row in rows:
        match = count_pattern.search(row[0])
        if match:
            return int(match.groups()[0])
    return -1


async def query_results_exact_count(db: AsyncSession, query: Select) -> int:
    """Get exact count of results from a query."""
    counter = query.with_only_columns(func.count(), maintain_column_froms=True)
    res = await db.execute(counter)
    return res.scalar_one()


async def query_results_approx_count(db: AsyncSession, query: Select) -> int:
    """Get approximate count of results from a query."""
    rows = await db.execute(SQLExplain(query))
    rows = rows.all()
    count = extract_count_from_explain(rows)
    return count


async def query_results_count(
    db: AsyncSession,
    query: Select,
    *,
    threshold: int = 10000,
    exact: bool = False,
) -> ResultCount:
    """
    Get count of results from a query.
    If exact is True, exact count is returned.
    If count is less than threshold, exact count is returned.
    """
    if exact:
        count = await query_results_exact_count(db, query)
    else:
        count = await query_results_approx_count(db, query)
        if count < threshold:
            exact = True
            count = await query_results_exact_count(db, query)
    return ResultCount(count, exact)


async def table_approx_count(db: AsyncSession, *, model: type[BaseModel]) -> int:
    """
    Get approximate count of records.

    Reference:
        - https://stackoverflow.com/a/7945274/19517403
    """
    query = sa.text(
        """
        SELECT (
            CASE
                WHEN c.reltuples < 0 THEN 0       -- never vacuumed
                WHEN c.relpages = 0 THEN float8 '0'  -- empty table
                ELSE c.reltuples / c.relpages
            END * (
                pg_catalog.pg_relation_size(c.oid)
                / pg_catalog.current_setting('block_size')::int
            )
        )::bigint
        FROM   pg_catalog.pg_class c
        WHERE  c.oid = :table_name ::regclass;      -- schema-qualified table here
        """
    ).bindparams(table_name=model.table_name())
    result = await db.execute(query)
    return result.scalar_one()


async def table_exact_count(db: AsyncSession, *, model: type[BaseModel]) -> int:
    """Get exact count of records."""
    query = sa.select(sa.func.count(model.id))
    result = await db.execute(query)
    return result.scalar_one()


async def table_count(
    db: AsyncSession,
    *,
    model: type[BaseModel],
    threshold: int = 10000,
) -> ResultCount:
    """
    Get exact or approximate count of records.

    If the approximate count < threshold, the exact count is returned.
    """
    count, is_exact = await table_approx_count(db, model=model), False
    if count < threshold:
        is_exact = True
        count = await table_exact_count(db, model=model)
    return ResultCount(count, is_exact)
