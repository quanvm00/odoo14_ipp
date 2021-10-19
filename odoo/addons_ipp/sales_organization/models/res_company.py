# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    region_area_id = fields.Many2one('region.area', string='Area')
    code = fields.Char('Code')
