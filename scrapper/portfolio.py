import requests

from bs4 import BeautifulSoup
from db import save_companies

index_url = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?Indice=IBOV&idioma=pt-br"


async def fetch_portfolio(loop):
    """ Fetch portfolio on BMF bovespa website """

    # Async web request
    response = await loop.run_in_executor(None, requests.get, index_url)
    index_members = fetch_portfolio_composition(response.text)

    # Save companies in the database
    await save_companies(index_members)


def fetch_portfolio_composition(content):
    """ Fetch IBOVESPA portfolio index composition, basic data from main page. """
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
