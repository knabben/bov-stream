from django.core.management.base import BaseCommand

from bovespa.helpers import (
    fetch_portfolio_composition, fetch_company_link, fetch_report_page,
    fetch_company_segments)


class Command(BaseCommand):
    help = 'Extracts BOVESPA data and populates database'

    def handle(self, *args, **options):
        print("Fetching portfolio IBOVESPA indexes")
        fetch_portfolio_composition()

        print("Fetching indexes links for main page")
        fetch_company_link()

        print("Fetching company segments")
        fetch_company_segments()
