# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Respartner(models.Model):
    _inherit = 'res.partner'

    saleperson_ids = fields.One2many('res.partner.saleperson', 'partner_id', string='Salepersons')
    default_code = fields.Char("Customer Code")

    def gen_mcp(self):
        mcp_obj = self.env['mcp.mcp'].sudo()
        mcp_obj.action_gen_mcp(self.ids)
        return True