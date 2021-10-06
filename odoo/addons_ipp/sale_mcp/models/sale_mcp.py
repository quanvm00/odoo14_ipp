# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleMcp(models.Model):
    _name = 'sale.mcp'
    _description = 'Sale MCP'
    _order = 'partner_id, user_id, company_id, date_visit'

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner', string='Customer')
    user_id = fields.Many2one('res.users', string='Salesperson')
    company_id = fields.Many2one('res.company', string='Company')
    date_visit = fields.Date(string='Date visit')
    default_code = fields.Char("Customer Code")
    contact_address = fields.Char('Address')
    type_user = fields.Char('Type User')

    type_user = fields.Selection([
        ('sr', 'Saleperson'),
    ], string='Type User', readonly=True, default='sr')
