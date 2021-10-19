# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Respartner(models.Model):
    _inherit = 'res.partner'

    saleperson_ids = fields.One2many('res.partner.saleperson', 'partner_id', string='Salepersons')
