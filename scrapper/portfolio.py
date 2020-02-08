import requests

from bs4 import BeautifulSoup
from datetime import datetime
from aiopg.sa import create_engine


from tables import companies, metadata
from tables import prepare_tables

index_url = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?Indice=IBOV&idioma=pt-br"
dsn = "postgres://postgres:postgres@127.0.0.1/web_dev"


async def fetch_portfolio(loop):
    """ Fetch portfolio on """

    response = await loop.run_in_executor(None, requests.get, index_url)
    index_members = fetch_portfolio_composition(response.text)

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
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                )
                print(member_symbol, member_data)


def fetch_portfolio_composition(content):
    """
    Fetch IBOVESPA portfolio index composition, basic data from main page
    """
    index_members = {}
    data = BeautifulSoup(content, "lxml")

    for tr in data.find_all("tr"):
        try:
            col_vle = [member.text.strip() for member in tr.find_all("span")]
            col_desc = ["name", "type", "qty", "part"]
            symbol = col_vle.pop(0)

            for i, (value, desc) in enumerate(zip(col_vle, col_desc)):
                if i == 0:
                    if not symbol.startswith("Quantidade"):
                        index_members[symbol] = {}

                index_members[symbol][desc] = value
        except (KeyError, ValueError, IndexError) as e:
            print("WARN: could not be able to parse data {}".format(e))
            continue

    return index_members
