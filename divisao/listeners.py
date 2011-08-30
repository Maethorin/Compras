#!/usr/bin/env python
# encoding: utf-8
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from divisao.models import Compra, Divida, Pagamento

def grava_divida(devedor, credor, valor):
    divida = Divida.objects.get(devedor=devedor, credor=credor)
    divida.ajusta_valor(valor)
    divida.save()


def atualiza_divida(sender, instance, **kwargs):
    users = User.objects.all()
    dividendo = len(users)
    valor_dividido = round(instance.valor / float(dividendo), 2)
    for user in users:
        if user.username != instance.comprador.username:
            try:
                grava_divida(instance.comprador, user, -valor_dividido)
            except Divida.DoesNotExist:
                try:
                    grava_divida(user, instance.comprador, valor_dividido)
                except Divida.DoesNotExist:
                    Divida.objects.create(valor=valor_dividido, devedor=user, credor=instance.comprador)
            except Divida.ValorNegativo:
                try:
                    divida = Divida.objects.get(devedor=instance.comprador, credor=user)
                    valor = divida.valor - valor_dividido
                    divida.ajusta_valor(valor)
                    divida.save()
                except Divida.DoesNotExist:
                    Divida.objects.create(valor=valor_dividido, devedor=user, credor=instance.comprador)


def realiza_pagamento(sender, instance, **kwargs):
    try:
        grava_divida(instance.pagador, instance.recebedor, -instance.valor)
    except Divida.ValorNegativo, e:
        return "%s não deve tanto assim para %s. A dívida é só de R$ %s" % (instance.pagador, instance.recebedor, e)
    except Divida.DoesNotExist:
        return "Não existe dívida de %s para %s" % (instance.recebedor, instance.pagador)

post_save.connect(atualiza_divida, sender=Compra)

post_save.connect(realiza_pagamento, sender=Pagamento)