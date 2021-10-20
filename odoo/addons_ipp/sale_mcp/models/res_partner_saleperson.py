# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerSaleperson(models.Model):
    _name = 'res.partner.saleperson'
    _description = 'Res Partner Saleperson'

    name = fields.Char("Customer Name")
    partner_id = fields.Many2one('res.partner', string='Customer')
    user_id = fields.Many2one('res.users', string='Salesperson', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    default_code = fields.Char("Customer Code")
    contact_address = fields.Char("Customer Address")
    # define list day of week
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday')
    sunday = fields.Boolean('Sunday')

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id:
            self.company_id = self.partner_id.company_id or False
            self.default_code = self.partner_id.default_code or ''
            self.contact_address = self.partner_id.contact_address or ''

    @api.model_create_multi
    def create(self, vals_list):
        partner_obj = self.env['res.partner']
        for vals in vals_list:
            partner_id = vals.get('partner_id',False)
            if partner_id:
                partner = partner_obj.browse(partner_id)
                vals.update({
                    'company_id': partner.company_id and partner.company_id.id or False,
                    'name': partner.name or '',
                    'default_code': partner.default_code or '',
                    'contact_address': partner.contact_address or '',
                })
        res = super().create(vals_list)
        return res