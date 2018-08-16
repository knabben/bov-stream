import json
import re
import requests
import urllib
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict

from datetime import datetime
from bmf.models import Company, Date, FinancialReport, REPORT


session = requests.Session()

index_url = 'http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?Indice=IBOV&idioma=pt-br'
bovespa_listing = 'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/'
query_action = 'http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp'
query_rad_cvm = 'https://www.rad.cvm.gov.br/ENETCONSULTA/'


def fetch_portfolio_composition():
    """
    Fetch IBOVESPA portfolio index composition, basic data from main page
    """

    response, index_members = requests.get(index_url), {}

    data = BeautifulSoup(response.content, 'lxml')

    for tr in data.find_all('tr'):
        try:
            col_vle = [member.text.strip() for member in tr.find_all('span')]
            col_desc = ['name', 'type', 'qty', 'part']
            symbol = col_vle.pop(0)

            for i, (value, desc) in enumerate(zip(col_vle, col_desc)):
                if i == 0:
                    if not symbol.startswith('Quantidade'):
                        index_members[symbol] = {}

                index_members[symbol][desc] = value
        except (KeyError, ValueError, IndexError) as e:
            print("WARN: could not be able to parse data {}".format(e))
            continue

    for member_symbol, member_data in index_members.items():
        company, created = Company.objects.get_or_create(
            symbol=member_symbol, name=member_data['name'],
            ibovespa=True
        )
        if created:
            print("Creating {} ".format(company.name))


def fetch_company_link():
    """ Grab company link for main page on BVMF """

    response = session.get(bovespa_listing + 'BuscaEmpresaListada.aspx?idioma=pt-br')
    data = BeautifulSoup(response.content, 'lxml')

    fields = {}
    for hidden in data.find_all('form')[0].find_all(type='hidden'):
        try:
            value = hidden.attrs['value']
            name = hidden.attrs['name']
            fields[name] = value
        except KeyError:
            continue

    # Must fill all hidden fields to fetch all companies listing
    fields['__EVENTARGUMENT'] = ''
    fields['__EVENTTARGET'] = 'ctl00:contentPlaceHolderConteudo:BuscaNomeEmpresa1:btnTodas'
    fields['RadAJAXControlID'] = 'ctl00_contentPlaceHolderConteudo_AjaxPanelBusca'
    fields['ctl00_contentPlaceHolderConteudo_AjaxPanelBuscaPostDataValue'] = \
        'ctl00_contentPlaceHolderConteudo_AjaxPanelBusca,ActiveElement,ctl00_contentPlaceHolderConteudo_BuscaNomeEmpresa1_btnTodas;'
    fields['ctl00$contentPlaceHolderConteudo$tabMenuEmpresaListada'] = \
        '{"State":{},"TabState":{"ctl00_contentPlaceHolderConteudo_tabMenuEmpresaListada_tabNome":{"Selected":true}}}'
    fields['httprequest'] = 'true'

    response = session.post(
        bovespa_listing + 'BuscaEmpresaListada.aspx?idioma=pt-br', data=fields)

    # Start parsing ALL rows to fetch company link
    data = BeautifulSoup(response.content, 'lxml')
    for tr in data.find_all('tr'):
        try:
            link = tr.find_all('a')[1]
            name = link.text
        except (AttributeError, IndexError):
            continue
        else:
            try:
                company, created = Company.objects.get_or_create(name=name)
                if created:
                    print("Creating {}".format(company.name))
            except:
                continue
            try:
                # Fetch SYMBOL
                original_resume = link.attrs['href']
                cvm_code = original_resume.split("?")[1].split("=")[1]
                cvm_url = "{0}?CodCVM={1}&ViewDoc=".format(query_action, cvm_code)
                from collections import OrderedDict

                headers = OrderedDict()
                headers["Host"] = "bvmf.bmfbovespa.com.br"
                headers["Connection"] = "keep-alive"
                headers["Upgrade-Insecure-Requests"] = "1"
                headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                headers["Accept-Encoding"] = "gzip, deflate"
                headers["Accept-Language"] = "en-US,en;q=0.9"

                new_session = requests.Session()
                new_session.headers = headers

                response = requests.get(cvm_url, headers=headers)
                data = BeautifulSoup(response.content, 'lxml')

                # Fetch DFP urls
                if not company.main_url:
                    finance = link.attrs['href'].replace(
                        'ResumoEmpresaPrincipal', 'HistoricoFormularioReferencia'
                    )
                    company.main_url = (bovespa_listing + finance + "&tipo=dfp&ano=0")
                    company.save()
                    print("Adding main_url for {}".format(company.name))

            except Exception as e:
                print("Getting an already filled company {}".format(e))


def _extract_table(body):
    data = BeautifulSoup(body, 'lxml')
    return pd.read_html(str(data.find('table')), header=0)[0]


def fetch_dfp_urls(url):
    """
    Fetch external system report detail:
    - Income statement
    - Balance sheet
    - Cash flow

    Attributes
    ----------
    index_members: List
        Portfolio composition being the last element a URL

    Returns
    -------
    list:
        A list of reports URL
    """
    response = session.get(url)
    params = url.split('?')[-1]

    data = BeautifulSoup(response.content, 'lxml')

    # Finding detailing report URLs
    urls = re.search(',(?P<data>\[(.*)\])',
                     data.find_all('script')[-2].text).group('data')

    # Returning a dict with real URL
    real_dict = {}
    for item in json.loads(urls):
        url = item['Value']+"&"+params
        real_dict[item['Text']] = urljoin(query_rad_cvm, url)

    return real_dict


def _extract_links(response):
    links = defaultdict(dict)

    main_data = BeautifulSoup(response.content, 'lxml')
    # Lets try just the first year with the cluster now
    item = main_data.find_all('a')[8]
    try:
        data = re.search('^(?P<date>\d+\/\d+\/\d+)(.*)(?P<version>\d+).0$', item.text)
        version, date = int(data.group('version')), data.group('date')

        if '- Vers' in item.text:
            url = re.search("\'(?P<url>(.*))\'", item.attrs['href']).group('url')
            data_input = {'version': version, 'url': url}

            links[date] = data_input
    except AttributeError:
        print("WARN: can't extract financial items")

    return links


def _create_date(real_date):
    date_obj, created = Date.objects.get_or_create(
        day=real_date.day, month=real_date.month,
        year=real_date.year, date=real_date
    )
    if created:
        print("Creating date {}".format(real_date))

    return date_obj


def fetch_report_page():
    """ Financial report page extraction from main page """

    index_members = defaultdict(dict)

    for member in Company.objects.filter(ibovespa=False):
        key, url = member.symbol, member.main_url

        response = session.get(url)
        links = _extract_links(response)

        # Fetch report reports page for each company
        for date, payload in links.items():
            date_obj = _create_date(datetime.strptime(date, '%d/%m/%Y'))
            version, main_url = payload['version'], payload['url']

            # Fetch financial reports URLs and create Finance Reports objects
            for kind, report_url in fetch_dfp_urls(main_url).items():
                print("Financial Report - {} from {} on {}".format(
                    kind, member.symbol, date_obj.date
                ))

                for key, value in REPORT:
                    if kind == value:
                        report, created = FinancialReport.objects.get_or_create(
                            company=member, date=date_obj, main_url=main_url,
                            version=version, url=report_url, report_type=key
                        )
                        if created:
                            print("Creating report {} for {}".format(date_obj.date, member.name))
                        break
                print('-'*100)

    return index_members


def fetch_company_segments():
    response = session.get(
        bovespa_listing + 'BuscaEmpresaListada.aspx?idioma=pt-br'
    )

    # Extract second round POST data
    data = BeautifulSoup(response.content, 'lxml')

    fields = {}
    for hidden in data.find_all('form')[0].find_all(type='hidden'):
        try:
            value = hidden.attrs['value']
            name = hidden.attrs['name']
            fields[name] = value
        except KeyError:
            continue

    # Must fill all hidden fields to fetch all companies listing
    fields['__EVENTARGUMENT'] = ''
    fields['__EVENTTARGET'] = 'ctl00:contentPlaceHolderConteudo:BuscaNomeEmpresa1:btnTodas'
    fields['RadAJAXControlID'] = 'ctl00_contentPlaceHolderConteudo_AjaxPanelBusca'
    fields['ctl00_contentPlaceHolderConteudo_AjaxPanelBuscaPostDataValue'] = \
        'ctl00_contentPlaceHolderConteudo_AjaxPanelBusca,ActiveElement,ctl00_contentPlaceHolderConteudo_BuscaNomeEmpresa1_btnTodas;'
    fields['ctl00$contentPlaceHolderConteudo$tabMenuEmpresaListada'] = \
        '{"State":{},"TabState":{"ctl00_contentPlaceHolderConteudo_tabMenuEmpresaListada_tabNome":{"Selected":true}}}'
    fields['httprequest'] = 'true'

    response = session.post(
        bovespa_listing + 'BuscaEmpresaListada.aspx?idioma=pt-br',
        data=fields
    )

    # Start parsing ALL rows to fetch company link
    data = BeautifulSoup(response.content, 'lxml')
    for tr in data.find_all('tr'):
        try:
            link = tr.find_all('a')[1]
            name = link.text
        except (AttributeError, IndexError):
            continue
        else:
            try:
                company = Company.objects.get(name=name)
            except (Company.DoesNotExist, Company.MultipleObjectsReturned):
                print("ERROR {} {}".format(name, link))
                continue
            else:
                response = session.get(bovespa_listing + link.attrs['href'])
                data = BeautifulSoup(response.content)

                url = data.find_all('iframe')[1]['src'].split('..')[-1]
                response = session.get('http://bvmf.bmfbovespa.com.br/' + url)

                data_1 = BeautifulSoup(response.content)
                data_2 = data_1.find('table', {'class': 'ficha'}).find_all('td')

                try:
                    name = data_2[1].text
                    try:
                        company_symbol = data_2[3].find_all('a')[1].text
                    except:
                        company_symbol = ''
                    section = data_2[-3].text
                    company.symbol = company_symbol.split('-')[-1]
                    company.segment = section
                    company.save()
                    print(name, company_symbol, section)
                except Exception as e:
                    print(e)
