import sqlalchemy as sa
from aiopg.sa import create_engine
from datetime import datetime
from sqlalchemy.schema import CreateTable
from psycopg2.errors import DuplicateTable
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.MetaData()
dsn = "postgres://postgres:postgres@127.0.0.1/web_dev"

companies = sa.Table(
    "companies",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("symbol", sa.String(50)),
    sa.Column("name", sa.String(50)),
    sa.Column("main_url", sa.String(100)),
    sa.Column("ibovespa", sa.Boolean),
    sa.Column("segment", sa.String(200)),
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


async def save_companies(index_members):
    """ Save companies list. """
    async with create_engine(dsn) as engine:
        await prepare_tables(engine)

        async with engine.acquire() as conn:
            for member_symbol, member_data in index_members.items():
                await conn.execute(
                    companies.insert().values(
                        symbol=member_symbol,
                        name=member_data.get("name"),
                        segment=member_data.get("type"),
                        ibovespa=True,
                    )
                )
                print(member_symbol, member_data)


async def fetch_all_companies():
    async with create_engine(dsn) as engine:
        async with engine.acquire() as conn:
            async for row in conn.execute(companies.select()):
                yield row
