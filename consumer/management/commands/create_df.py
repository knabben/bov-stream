from pandas import DataFrame
from django.db.models import Q


def get_facts(facts, idx, filter_desc=None, label=None, show=False):
    ret_dict = {}
    account_number = Q(account__number__in=idx)

    if filter_desc:
        facts = facts.filter(account__description__regex=filter_desc)
    rev = facts.filter(account_number)

    for data in rev:
        if show:
            print(data.account.description, data.account.number, label)
        if label is None:
            label = data.account.number
        ret_dict[label] = [data.value]
    return ret_dict


def _calc_fct(df):
    df['3.4_fct'] = df['3.1_fco'] + df['3.2_fci'] + df['3.3_fcf']
    df['3.5_fcl'] = df['3.1_fco'] + df['3.2_fci']
    df['3.6_fci/ll'] = (df['3.2_fci'] / df['1.9.1_net_income'])*100

    df['1.5_op_result'] = (df['1.4_op_expense'] - df['1.5_net_equit']) + df['1.3_gross_profit']


def _calc_ebitda(df):
    df['1.3.1_gross_margin'] = (df['1.3_gross_profit'] / df['1.1_revenue']) * 100

    df['1.9.3_ebitda'] = (
        (df['1.9.1_net_income'] - df['1.7_financial_result']) -
         df['1.8.2_taxes'] - df['1.9.2_depreciation']
    )

    df['1.9.4_ebitda_margin'] = (df['1.9.3_ebitda'] / df['1.1_revenue']) * 100
    df['1.9.5_roe'] = (df['1.9.1_net_income'] / df['1.10_net_worth']) * 100
    df['1.9.6_roa'] = (df['1.6_bef_fin_tax'] / df['2.1_assets']) * 100
    df['1.9.7_equity_mul'] = (df['2.1_assets'] / df['1.10_net_worth']) * 100


def _calc_cash_loan(df):
    df['2.2_cash'] = df['2.2_cash'] + df['2.3_fin_app']

    try:
        label = '2.4.2_gross_debt'
        df[label] = df['2.4_money_loan'] + df['2.4.1_finan_loan']
    except KeyError:
        print("ERROR {}".format(label))
    else:
        df['2.4.3_liquid_debt'] = df['2.4.2_gross_debt'] - df['2.2_cash']
        df['2.4.4_gross_debt/nw'] = (df['2.4.2_gross_debt'] / df['1.10_net_worth']) * 100


def create_data_company(company, year=2016):
    print("Company {}".format(company.name))

    for report in FinancialReport.objects.filter(company=company):
        value_facts = report.valuefact_set.filter(date__year=year)

        for (idx, label, desc, show) in ([
            (['3.01'], '1.1_revenue', None, False),                        # Revenue
            (['3.02'], '1.2_cost_goods', None, False),                     # Cost of goods sold
            (['3.03'], '1.3_gross_profit', None, False),                   # Gross profit

            (['3.04'], '1.4_op_expense', None, False),                     # Operating expenses
            (['3.04.06', '3.04.07'], '1.5_net_equit', 'Resultado(.*)Equivalência(.*)', False),

            (['3.05'], '1.6_bef_fin_tax', None, False),                           # Earnings before interest and taxes (EBIT)

            (['3.06'], '1.7_financial_result', 'Resultado Financeiro', False), # Financial results
            (['3.07'], '1.8.1_loss_bef_taxes', 'Resultado Antes dos Tributos(.*)', False), # Loss before 
            (['3.99.01.01'], '1.8.2_loss_per_stock', 'ON', False),  # Loss per stock
            (['3.08', '3.06'], '1.8.2_taxes', 'Imposto de Renda(.*)', False),  # Taxes

            (['4.01'], '1.9.1_net_income', None, False),                     # Net income
            (['7.05.01', '7.04.01'], '1.9.2_depreciation', 'Depreciaç(.*)', False), # Depreciation
            (['2.03', '2.08'], '1.10_net_worth', 'Patrimônio Líquido(.*)', False), # Net Worth

            (['1'], '2.1_assets', 'Ativo(.*)', False),                            # Assets
            (['1.01.01', '1.01'], '2.2_cash', 'Caixa(.*)', False),            # Cash
            (['1.01.02', '1.02'], '2.3_fin_app', 'Financeira(.*)', False),       # Financial application

            (['2.01.04'], '2.4_money_loan', 'Empréstimos(.*)', False),
            (['2.02.01'], '2.4.1_finan_loan', 'Empréstimos(.*)', False),

            (['6.01'], '3.1_fco', 'Caixa(.*)', False),
            (['6.02'], '3.2_fci', 'Caixa(.*)', False),
            (['6.03'], '3.3_fcf', 'Caixa(.*)', False),
        ]):
            output = get_facts(value_facts, idx, label=label, filter_desc=desc, show=show)
            main_data.update(output)

    company_df = DataFrame(main_data)

    try:
        _calc_fct(company_df)
        _calc_ebitda(company_df)
        _calc_cash_loan(company_df)
    except Exception as e:
        print("ERROR: {}".format(e))
        return

    company_df['name'] = company.name
    company_df['segment'] = company.segment
    company_df['year'] = year
    return company_df


main_df = DataFrame()
for c in Company.objects.all():
    for year in [2016]:
        df = create_data_company(c, year)
        main_df = main_df.append(df, ignore_index=True)
