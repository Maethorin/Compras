#!/usr/bin/env python
# encoding: utf-8
from django.contrib import admin
from divisao.models import Compra, Divida, Pagamento

admin.site.register(Compra)
admin.site.register(Divida)
admin.site.register(Pagamento)