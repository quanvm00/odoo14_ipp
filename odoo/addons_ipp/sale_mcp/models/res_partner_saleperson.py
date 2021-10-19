# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerSaleperson(models.Model):
    _name = 'res.partner.saleperson'
    _description = 'Res Partner Saleperson'

    name = fields.Char("Customer Name")
    partner_id = fields.Many2one('res.partner', string='Customer')
    user_id = fields.Many2one('res.users', string='Salesperson', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    # define list day of week
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday')
    sunday = fields.Boolean('Sunday')
