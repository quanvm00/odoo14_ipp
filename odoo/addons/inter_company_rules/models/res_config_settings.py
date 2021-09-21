# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .res_company import new_rule_type


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_validation = fields.Boolean(related='company_id.auto_validation', readonly=False)
    warehouse_id = fields.Many2one(related='company_id.warehouse_id', string='Warehouse For Purchase Orders', readonly=False, domain=lambda self: [('company_id', '=', self.env.company.id)])
    rule_type = fields.Selection(related='company_id.rule_type', readonly=False)
    intercompany_user_id = fields.Many2one(related='company_id.intercompany_user_id', readonly=False, required=True)
    rules_company_id = fields.Many2one(related='company_id', string='Select Company', readonly=True)
    intercompany_transaction_message = fields.Char(compute='_compute_intercompany_transaction_message')

    @api.onchange('rule_type')
    def onchange_rule_type(self):
        if self.rule_type not in new_rule_type.keys():
            self.auto_validation = False
            self.warehouse_id = False
        else:
            warehouse_id = self.warehouse_id or self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
            self.warehouse_id = warehouse_id

    @api.depends('rule_type', 'company_id', 'auto_validation', 'warehouse_id')
    def _compute_intercompany_transaction_message(self):
        for record in self:
            record.company_id.auto_validation = record.auto_validation
            record.company_id.warehouse_id = record.warehouse_id
            record.company_id.rule_type = record.rule_type
            record.intercompany_transaction_message = record.company_id.intercompany_transaction_message
