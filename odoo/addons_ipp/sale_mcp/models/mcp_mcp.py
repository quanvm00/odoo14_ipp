# -*- coding: utf-8 -*-
import logging
import re
import numpy as np
import calendar
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
import dateutil
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class aaa(models.Model):
    _name = 'sale.mcp'


class McpMcp(models.Model):
    _name = 'mcp.mcp'
    _description = 'MCP MCP'
    _order = 'partner_id, user_id, company_id, date_visit'

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner', string='Customer', index=True)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True)
    company_id = fields.Many2one('res.company', string='Company', index=True)
    region_area_id = fields.Many2one(related='company_id.region_area_id', string='Area', store=True, readonly=True,
                                     index=True)
    date_visit = fields.Date(string='Date visit', index=True)
    default_code = fields.Char("Customer Code", index=True)
    contact_address = fields.Char('Address')
    type_user = fields.Selection([
        ('sr', 'Saleperson'),
    ], string='Type User', readonly=True, default='sr')

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        for partner in self:
            self.name = self.partner_id.name
            self.company_id = self.partner_id.company_id and self.partner_id.company_id.id or False

    def gen_mcp(self):
        self.action_gen_mcp(self)
        return True

    def gen_mcp_with_date(self, date_from, date_to, lst_partner):
        def _get_value(partner_id, customer_name, default_code, user_id, company_id, contact_address, date_visit):
            return {
                'partner_id': partner_id,
                'company_id': company_id,
                'name': customer_name,
                'default_code': default_code,
                'contact_address': contact_address,
                'user_id': user_id,
                'date_visit': date_visit.strftime("%Y-%m-%d")
            }

        def week_of_month(date):
            x = np.array(calendar.monthcalendar(date.year, date.month))
            week_of_month = np.where(x == date.day)[0][0] + 1
            return week_of_month

        mcp_obj = self.env['mcp.mcp'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        _logger.info("Start gen MCP...")

        dd = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]
        res = []
        if not lst_partner:#res_partner_search_mode
            lst_partner = partner_obj.with_context(res_partner_search_mode='customer').search(
                                            ['|', ('active', '=', False), ('active', '=', True),
                                             ('is_company', '=', False),
                                             ], order="id asc").ids
        # remove old data with condition : date_from <= date_visit <= date_to and partner
        old_data = mcp_obj.search([('date_visit', '>=', date_from),
                                   ('partner_id', 'in', lst_partner)
                                   ])
        old_data.unlink()
        #
        lst_mcp = []
        lst_partner_mcp = partner_obj.search([('active', '=', True),
                                              ('id', 'in', lst_partner)
                                              ]).ids
        lst_partner_mcp.append(-1)
        tuple_partner_mcp = tuple(lst_partner_mcp)
        query = """
                    SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday,
                            partner_id, name, default_code, company_id, 
                            user_id, contact_address,
                            COALESCE('sr') as type_user
                    FROM res_partner_saleperson
                    WHERE partner_id in %s

                """ % str(tuple_partner_mcp)
        self.env.cr.execute(query)
        vals_partner_mcp = self.env.cr.dictfetchall()
        for partner in vals_partner_mcp:
            monday = partner['monday']
            tuesday = partner['tuesday']
            wednesday = partner['wednesday']
            thursday = partner['thursday']
            friday = partner['friday']
            saturday = partner['saturday']
            sunday = partner['sunday']
            # information customer
            partner_id = partner.get('partner_id', False)
            company_id = partner.get('company_id', False)
            customer_name = partner.get('name', '')
            default_code = partner.get('default_code', '')
            user_id = partner.get('user_id', False)
            contact_address = partner.get('contact_address', '')
            #
            if monday or tuesday or wednesday or thursday or friday or saturday or sunday:
                if user_id:
                    for dt in dd:
                        if monday and dt.weekday() == 0:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if tuesday and dt.weekday() == 1:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if wednesday and dt.weekday() == 2:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if thursday and dt.weekday() == 3:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if friday and dt.weekday() == 4:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if saturday and dt.weekday() == 5:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
                        if sunday and dt.weekday() == 6:
                            res.append(
                                _get_value(partner_id, customer_name, default_code, user_id, company_id,
                                           contact_address, dt))
        for line in res:
            mcp_id = mcp_obj.create(line)
            lst_mcp.append(mcp_id)
        _logger.info("Finish gen MCP...")
        return lst_mcp

    def action_gen_mcp(self, partner_ids):
        td = datetime.today()
        from_date = datetime(td.year, td.month, td.day)
        to_date = datetime(td.year, td.month, td.day) + dateutil.relativedelta.relativedelta(days=1)
        self.gen_mcp_with_date(from_date, to_date, partner_ids)
        return True
