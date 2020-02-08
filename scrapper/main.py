import click
import asyncio
from portfolio import fetch_portfolio
from db import fetch_all_companies
from stream import stream_via_socket


@click.group()
def cmd():
    pass


@cmd.command()
def fetch_price_tickers():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream_via_socket(loop))


@cmd.command()
def fetch_companies():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_portfolio(loop))


if __name__ == "__main__":
    cmd()
