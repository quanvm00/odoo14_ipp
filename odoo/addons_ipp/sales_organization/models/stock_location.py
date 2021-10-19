# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    location_type = fields.Selection(
        [('main', 'Main'),
         ('promotion', 'Promotion'),
         ('other', 'Other'),
         ], 'Type', copy=False, default='main')
    code = fields.Char('Code')
