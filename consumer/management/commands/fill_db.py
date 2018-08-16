from datetime import datetime

from django.core.management.base import BaseCommand

from bovespa.helpers import fetch_report_page, _extract_table, session
from bovespa.models import Company, FinancialReport, Date, ValueFact, Account


class Command(BaseCommand):
    help = 'Extracts BOVESPA data and populates database'

    def handle(self, *args, **options):
        # Big cost running it, if we have on database the main report
        # links we should move to extract data from tables
        # use the flag to enable.
        print("Fetching financial pages report")
        fetch_report_page()

        for member in Company.objects.filter(ibovespa=False):
            reports = FinancialReport.objects.filter(company=member)
            for report in reports:
                print('{} - {} - {}'.format(member.name, report.date.year,
                                            report.report_type))
                # Start session for main report page
                try:
                    response = session.get(report.main_url)
                    assert response.status_code == 200

                    response = session.get(report.url)
                    df = _extract_table(response.content)
                    df.fillna(0, inplace=True)

                    for _, row_data in df.T.to_dict().items():
                        try:
                            description = row_data['Descrição']
                            number = row_data['Conta']

                            account_obj, created = Account.objects.get_or_create(
                                number=number, description=description
                            )
                            if created:
                                print("Account {} {} created".format(number,
                                                                     description))

                            # Parse date columns and create valuefact row
                            print(row_data)

                            for date in list(row_data.keys())[2:]:
                                real_date = datetime.strptime(date.split(' ')[-1], '%d/%m/%Y')
                                date_obj, created = Date.objects.get_or_create(
                                    day=real_date.day, month=real_date.month,
                                    year=real_date.year, date=real_date
                                )
                                if created:
                                    print("Creating date {}".format(real_date))

                                try:
                                    if type(row_data[date]) == float:
                                        row_data[date] = round(row_data[date], 3)

                                    value = str(row_data[date]).replace('.','')
                                    value = int(value)
                                except Exception as e:
                                    value = row_data[date]
                                    print("Error converting value {} for {}".format(e, type(value)))

                                value_obj, created = ValueFact.objects.get_or_create(
                                    account=account_obj, fin_metadata=report, date=date_obj,
                                    value=value
                                )
                                if created:
                                    print("ValueFact created with {}".format(value))
                        except KeyError:
                            print("ERROR parsing.")

                except Exception as e:
                    print('Session error. {}'.format(e))
                    continue
