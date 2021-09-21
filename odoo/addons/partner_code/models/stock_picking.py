# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _




class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, values):
        return super(StockPicking, self).write(values)


