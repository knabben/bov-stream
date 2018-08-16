from django.db.models import Q
from itertools import groupby


def fetch_data(lte=2017, gte=2008, desc=['1.01'], symbol='', values=['date__year', 'account__description', 'account__number']):
    data = ValueFact.objects.filter(
        fin_metadata__company__symbol=symbol,
        date__year__lte=lte,
        date__year__gte=gte,
        account__in=desc,
        fin_metadata__url__contains='Informacao=2'
    ).order_by('-date').values(*values).annotate(value=Max('value'))
    return data

def df_data_1(data):
    index = []
    new_dict = defaultdict(list)
    try:
        grouping = groupby(data.all(), key=lambda x: x['date__year'])
        for k, g in grouping:
            index.append(k)
            for n in list(g):
                new_dict[n['account__number']].append(n.get('value'))
        return DataFrame(new_dict, index=index)
    except Exception as e:
        print(index)
        print(e)
        print(new_dict)
        return None

def df_data_2(data):
    # There are changes of numbers between reports
    # trying to normalizing it fetching the first
    # one registered
    index = []
    new_dict = defaultdict(list)
    grouping = groupby(data.all(),key=lambda x: x['date__year'])
    for k, g in grouping:
        index.append(k)
        value = min(list(g), key=lambda x: x['fin_metadata__date__year'])
        new_dict['depreciation'].append(value.get('value'))
    return DataFrame(new_dict, index=index)


def df_data_3(data):
    index = []
    new_dict = defaultdict(list)
    grouping = groupby(data.all(),key=lambda x: x['date__year'])
    for k, g in grouping:
        index.append(k)
        d1 = list(g)
        
        for k1, g1 in groupby(d1, key=lambda x: x['fin_metadata__date__year']):
            for l1 in list(g1):
                new_dict[l1.get('account__number')].append(l1.get('value'))
            
            break
    return DataFrame(new_dict, index=index)


companies = Company.objects.all()
print(companies.count())
for company in companies.exclude(symbol='BBSE3'):
    print('-'*100)
    print(company.name, company.symbol)
    
    def fetch_gross_revenue(init, end, symbol):
        # 3.01sales_revenue = 'Receita de Venda de Bens e/ou Serviços' 
        # 3.03    gross_revenue = 'Resultado Bruto' 
        # 3.05    ebit = 'Resultado Antes do Resultado Financeiro e dos Tributos' 
        # 1       assets = 'Ativo Total'
        # 3.06.01 receita = 'Receitas Financeiras' 
        # 3.06.02 dispenses = 'Despesas' 
        # 3.11    profit = 'Lucro/Prejuizo do periodo' 
        # 
        main_query = Q(number__in=['3.01', '3.03', '3.05', '3.06.01', '3.06.02'])
        main_base = Account.objects.filter(main_query)
        data = df_data_1(fetch_data(init, end, desc=main_base, symbol=symbol))
        data['gross_margin'] = (data['3.03']/data['3.01'])*100
        data['financial_result'] = data['3.06.01'] + data['3.06.02']
        return data
    
    # Problems - BBDC3 have a very odd report
        
    def fetch_depreciation(init, end, symbol):
        depreciation_query = Q(description__icontains='Depreciaç', number__startswith='6.')
        main_base = Account.objects.filter(depreciation_query)
        data = df_data_2(fetch_data(init, end, desc=main_base, symbol=symbol, values=[
            'fin_metadata__date__year', 'date__year', 'account__description', 'account__number'
        ]))

        return data
    
    def fetch_cash_flow(init, end, symbol):
        # patrimonio liquido - 2.03
        # caixa liquido operacional - 6.01 - fco
        # caixa liquido investimento - 6.02 - fci
        # caixa liquido financiamento - 6.03 - fcf
        main_base = Account.objects.filter(number__in=['6.01', '6.02', '6.03', '2.03', '1',
                                                       '2.02.01', '2.01.04', '1.01.01', '1.01.02'])
        data = df_data_3(fetch_data(init, end, desc=main_base, symbol=symbol, values=[
            'fin_metadata__pk', 'fin_metadata__date__year', 'date__year', 'account__description', 'account__number'
        ]))
        data['fct'] = data['6.01'] + data['6.02'] + data['6.03'] 
        data['fcl'] = data['6.01'] + data['6.02']
        data['equity_mult'] = data['1'] / data['2.03']
        
        #data['caixa'] = data['1.01.01'] + data['1.01.02']
        #data['divida_bruta'] = data['2.02.01'] + data['2.01.04']
        #df['liquid_margin'] = (df['3.11'] / df['3.01']) * 100
        return data
    
    def ebitda(df):
        df['ebitda'] = df['3.05'] + df['depreciation']
        df['ebitda_margin'] = (df['ebitda'] / df['3.01']) * 100
        
    def financial_results(df):
        #df['caixa'] = df['1.01.01'] + df['1.01.02']
        
        
        pass
    
    
    df_1 = fetch_gross_revenue(2017, 2008, company.symbol)
    df_2 = fetch_depreciation(2017, 2008, company.symbol)
    df_3 = fetch_cash_flow(2017, 2008, company.symbol)
        
    df_final = pd.concat([df_1, df_2, df_3], axis=1)
    
    ebitda(df_final)
            
    if df_final is not None:
        df_final.dropna(inplace=True)
        
    print(df_final)
