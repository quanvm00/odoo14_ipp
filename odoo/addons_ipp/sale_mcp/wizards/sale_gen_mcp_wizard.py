# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
import calendar
import logging

_logger = logging.getLogger(__name__)


class SaleGenMcpWizard(models.TransientModel):
    _name = 'sale.gen.mcp.wizard'
    _description = 'Sale Gen MCP Wizard'

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    name = fields.Char("Name")

    # company_id = fields.Many2one('res.company', string='NPP')
    company_id = fields.Many2one('res.company', 'Company')

    area_id = fields.Many2one('res.area', related='company_id.region_area_id', string='Area', readonly=True)

    user_id = fields.Many2one('res.users', string='Salesperson')

    date_from = fields.Date(string='Start Date', default=_get_default_date)
    date_to = fields.Date(string='End Date', default=_get_default_date)
    date_todate = fields.Date(string='Today', default=_get_default_date)

    line_ids = fields.One2many('sale.gen.mcp.wizard.line', 'mcp_id', string='Lines', auto_join=True)

    @api.onchange('date_from', 'date_todate')
    def _onchange_date_from(self):
        if self.date_from and self.date_todate and self.date_from < self.date_todate:
            raise UserError(_('Start Date is after today .'))

    @api.onchange('date_to', 'date_todate')
    def _onchange_date_to(self):
        if self.date_to and self.date_todate and self.date_to < self.date_todate:
            raise UserError(_('End Date is after today .'))

    @api.onchange('user_id', )
    def _onchange_parent_id(self):
        partner_saleperson_obj = self.env['res.partner.saleperson']
        vals = {}
        if self.user_id:
            old_line = []
            lst_customer = partner_saleperson_obj.search([('user_id', '=', self.user_id.id)])
            for line in lst_customer:
                old_line.append((0, 0, {'partner_id': line.partner_id.id,
                                        'phone': line.partner_id.phone or '',
                                        'mobile': line.partner_id.mobile or '',
                                        'user_id': self.user_id,
                                        'company_id': line.partner_id.company_id and line.partner_id.company_id.id or False,

                                        'monday': line.monday or '',
                                        'tuesday': line.tuesday or '',
                                        'wednesday': line.wednesday or '',
                                        'thursday': line.thursday or '',
                                        'friday': line.friday or '',
                                        'saturday': line.saturday or '',
                                        'sunday': line.sunday or '',
                                        }))

            vals.update({
                'line_ids': old_line
            })
        self.update(vals)

    def date_range(self, date_from, date_to):
        r = (date_to + timedelta(days=1) - date_from).days
        return [date_from + timedelta(days=i) for i in range(r)]

    def gen_mcp(self):
        for mcp in self:
            if mcp.date_from < mcp.date_todate or mcp.date_to < mcp.date_todate:
                raise UserError(_('Start Date/ End Date is after today .'))
            date_from = fields.Date.from_string(mcp.date_from)
            date_to = fields.Date.from_string(mcp.date_to)
            lst_partner_errorstr = ''
            for line in mcp.line_ids:

                if not line.monday and not line.tuesday and not line.wednesday \
                        and not line.thursday and not line.friday and not \
                        line.saturday and not line.sunday:
                    lst_partner_errorstr = '%s \n %s[%s]' % (lst_partner_errorstr,
                                                             line.partner_id.name,
                                                             line.partner_id.default_code)

            if lst_partner_errorstr:
                raise UserError(_('You must check for customers: %s.') % (lst_partner_errorstr))

            lst_partner = [line.partner_id.id for line in mcp.line_ids]
            self.gen_mcp_with_date(date_from, date_to, lst_partner)
        return True

    def gen_mcp_with_date(self, date_from, date_to, lst_partner):
        res = self.env['mcp.mcp'].gen_mcp_with_date(date_from, date_to, lst_partner)
        return res


class SaleGenMcpWizardLine(models.TransientModel):
    _name = 'sale.gen.mcp.wizard.line'
    _description = 'Sale Gen MCP Wizard Line'

    mcp_id = fields.Many2one('sale.gen.mcp.wizard', 'MCP')

    partner_id = fields.Many2one('res.partner', string='Customer',
                                 required=True)
    user_id = fields.Many2one('res.users', string='Salesperson')
    company_id = fields.Many2one('res.company', string='Company')

    default_code = fields.Char(related='partner_id.default_code', string='Code')
    phone = fields.Char(related='partner_id.phone', string='Phone')
    mobile = fields.Char(related='partner_id.mobile', string='Mobile')
    contact_address = fields.Char(related='partner_id.contact_address', string='Address')

    monday = fields.Boolean(string='Monday')
    tuesday = fields.Boolean(string='Tuesday')
    wednesday = fields.Boolean(string='Wednesday')
    thursday = fields.Boolean(string='Thursday')
    friday = fields.Boolean(string='Friday')
    saturday = fields.Boolean(string='Saturday')
    sunday = fields.Boolean(string='Sunday')
