import click
import asyncio
from portfolio import fetch_portfolio


@click.group()
def cmd():
    pass


@cmd.command()
def fetch_price_tickers():
    # stream_through_websocket()
    return


@cmd.command()
def fetch_companies():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_portfolio(loop))


if __name__ == "__main__":
    cmd()
