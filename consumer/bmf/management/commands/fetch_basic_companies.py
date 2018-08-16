from django.core.management.base import BaseCommand

from bmf.helpers import fetch_portfolio_composition


class Command(BaseCommand):
    help = 'Extracts BOVESPA data and populates database'

    def handle(self, *args, **options):
        print("Fetching portfolio IBOVESPA indexes")
        fetch_portfolio_composition()
