#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from datetime import datetime
from django.contrib.auth.models import User

from divisao.models import Compra, Divida
import divisao.listeners

class SimpleTest(TestCase):

    def setUp(self):
        self.comprador = User.objects.get(username="marcio_santana")

    def tearDown(self):
        Compra.objects.all().delete()
        Divida.objects.all().delete()

    def cria_compra(self, valor=20.28, comprador=None):
        comprador = comprador or self.comprador
        Compra.objects.create(
            comprador=comprador,
            data=datetime.strptime('20/08/2011', '%d/%m/%Y'),
            valor=valor,
            descricao="Compra em teste",
        )

    def test_deve_incluir_dividas_novas_quando_nao_existe_ao_salvar_uma_compra(self):
        """ deve incluir divida nova quando nao existe ao salvar uma compra """
        dividas = Divida.objects.filter(credor=self.comprador)
        self.assertEquals(len(dividas), 0)
        self.cria_compra()
        dividas = Divida.objects.filter(credor=self.comprador)
        self.assertEquals(len(dividas), 3)

    def test_deve_dividir_igualmente_o_valor_da_compra_pra_cada_user(self):
        """ deve dividir igualmente o valor da compra pra cada user """
        self.cria_compra()
        dividas = Divida.objects.filter(credor=self.comprador)
        for divida in dividas:
            self.assertEquals(divida.valor, 5.07)

    def test_deve_arredondar_o_valor_pra_cima_na_divisao(self):
        """ deve arredondar o valor pra cima na divisao """
        self.cria_compra(valor=20.27)
        dividas = Divida.objects.filter(credor=self.comprador)
        for divida in dividas:
            self.assertEquals(divida.valor, 5.07)

    def test_deve_atualizar_os_valores_da_divida_caso_ja_exista(self):
        """ deve atualizar os valores da divida caso ja exista """
        self.cria_compra(valor=20.0)
        self.cria_compra(valor=12.0)
        dividas = Divida.objects.filter(credor=self.comprador)
        self.assertEquals(len(dividas), 3)
        for divida in dividas:
            self.assertEquals(divida.valor, 8.0)

    def test_deve_abater_da_divida_se_credor_ja_tem_divida_com_devedor_menor_que_a_divida_atual(self):
        """ deve abater da divida se credor ja tem divida com devedor menor que a divida atual """
        self.cria_compra(valor=20.0)
        outro_comprador = User.objects.get(username="diego_pinheiro")
        self.cria_compra(valor=12.0, comprador=outro_comprador)
        dividas_outro_comprador = Divida.objects.filter(credor=outro_comprador)
        self.assertEquals(len(dividas_outro_comprador), 2)
        dividas = Divida.objects.filter(credor=self.comprador, devedor=outro_comprador)
        self.assertEquals(len(dividas), 1)
        self.assertEquals(dividas[0].valor, 2.0)

    def test_deve_compensar_valor_se_ja_tem_divida_com_devedor_maior_que_a_divida_atual(self):
        """ deve compensar valor se ja tem divida com devedor maior que a divida atual """
        self.cria_compra(valor=20.0)
        outro_comprador = User.objects.get(username="diego_pinheiro")
        self.cria_compra(valor=30.0, comprador=outro_comprador)
        dividas = Divida.objects.filter(credor=self.comprador, devedor=outro_comprador)

        self.assertEquals(dividas[0].valor, 2.5)


        
