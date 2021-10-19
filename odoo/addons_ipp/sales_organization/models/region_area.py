# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RegionArea(models.Model):
    _name = 'region.area'
    _description = 'Area'

    name = fields.Char('Name', required=True, )
    code = fields.Char('Code')
    manager_id = fields.Many2one('res.users', string='Manager')
    user_ids = fields.Many2many('res.users', 'region_area_user_rel', string='Users')
