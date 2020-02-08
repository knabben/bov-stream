import sqlalchemy as sa
from sqlalchemy.schema import CreateTable
from psycopg2.errors import DuplicateTable
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.MetaData()

companies = sa.Table(
    "companies",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("symbol", sa.String(50)),
    sa.Column("name", sa.String(50)),
    sa.Column("main_url", sa.String(100)),
    sa.Column("ibovespa", sa.Boolean),
    sa.Column("segment", sa.String(200)),
    sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
    sa.Column("updated_at", sa.TIMESTAMP(timezone=True)),
    sa.Column("deleted_at", sa.TIMESTAMP(timezone=True)),
)

async def prepare_tables(pg):
    """ Create the table if does not exists. """
    tables = [companies]
    async with pg.acquire() as conn:
        for table in tables:
            try:
                create_expr = CreateTable(table)
                await conn.execute(create_expr)
            except DuplicateTable:
                return

