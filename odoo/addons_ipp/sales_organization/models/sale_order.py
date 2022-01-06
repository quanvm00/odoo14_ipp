# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def search_read_for_api(self, domain=None, fields=None, offset=0, limit=None, order=None):
        return {'a':1,
                'b':2
                }
