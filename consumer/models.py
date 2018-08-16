#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models


REPORT = (
    ('ab', 'Balanço Patrimonial Ativo'),  # Assets balance sheet
    ('pb', 'Balanço Patrimonial Passivo'),  # Passive balance sheet
    ('is', 'Demonstração do Resultado'),  # Income statement
    ('cf', 'Demonstração do Fluxo de Caixa'),  # Cash flow
    ('da', 'Demonstração do Resultado Abrangente'),  # Result abrangente
    ('va', 'Demonstração de Valor Adicionado'),  # Result abrangente
)

# -- Dimensions
class Date(models.Model):
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    date = models.DateField()


class Account(models.Model):
    number = models.CharField(max_length=50)
    description = models.CharField(max_length=100)


class Company(models.Model):
    symbol = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=50)
    main_url = models.CharField(max_length=255)
    ibovespa = models.BooleanField(default=False)
    segment = models.CharField(max_length=200, default='')
    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sector(self):
        output = map(str.strip, self.segment.split('/'))
        sector, subsector = list(output)[:2]

        return (sector, subsector)

    class Meta:
        db_table = "companies"

class FinancialReport(models.Model):
    report_type = models.CharField(max_length=2, choices=REPORT)
    company = models.ForeignKey(Company)
    main_url = models.CharField(max_length=200)
    url = models.TextField()
    version = models.IntegerField()
    date = models.ForeignKey(Date)


# -- Fact table
class ValueFact(models.Model):
    date = models.ForeignKey(Date)
    account = models.ForeignKey(Account)
    fin_metadata = models.ForeignKey(FinancialReport)
    value = models.FloatField()
