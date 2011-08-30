#!/usr/bin/env python
# encoding: utf-8
from django.contrib.auth.models import User
from django.db import models


class Divida(models.Model):
    valor = models.FloatField()
    devedor = models.ForeignKey(User, related_name="devedores")
    credor = models.ForeignKey(User, related_name="credores")

    class ValorNegativo(Exception):
        pass

    def ajusta_valor(self, valor):
        if self.valor + valor < 0:
            raise Divida.ValorNegativo(self.valor)
        self.valor += valor

    def __unicode__(self):
        return "%s deve R$ %s a %s" % (self.devedor.username, self.valor, self.credor.username)

class Compra(models.Model):
    data = models.DateField()
    descricao = models.CharField(u"Descrição", max_length=255)
    valor = models.FloatField()
    comprador = models.ForeignKey(User)

    def __unicode__(self):
        return "%s gastou R$ %s em compras em %s" % (self.comprador.username, self.valor, self.data.strftime('%d/%m/%Y'))

class Pagamento(models.Model):
    valor = models.FloatField()
    pagador = models.ForeignKey(User, related_name="pagadores")
    recebedor = models.ForeignKey(User, related_name="recebedores")

    def __unicode__(self):
        return "%s pagou R$ %s para %s" % (self.pagador.username, self.valor, self.recebedor.username)
