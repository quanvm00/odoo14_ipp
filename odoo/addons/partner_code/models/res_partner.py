# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence', required=False)

    def gen_sequence(self):
        sequence_obj = self.env['ir.sequence']
        # lst_state = self.search([])
        for state in self:
            if not state.sequence_id and state.code:
                sequence = sequence_obj.create({
                    'name': '[Sequence]-%s' % (state.name or ''),
                    'code': '[Sequence]-%s' % (state.code or ''),
                    'prefix': state.code + '%(month)s%(y)s',
                    'implementation': 'standard',
                    'padding': 4,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'company_id': False,
                })
                state.write({'sequence_id': sequence.id})
        return True

    @api.model
    def create(self, vals):
        state = super(ResCountryState, self).create(vals)
        self.gen_sequence()
        return state


class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_code = fields.Char('Code', index=True)

    @api.model
    def create(self, vals):
        IrSequenceSudo = self.env['ir.sequence'].sudo()
        if vals.get('state_id', False):
            province_obj = self.env['res.country.state']
            code = province_obj.browse(vals.get('state_id', False)).sequence_id.code
            vals['default_code'] = IrSequenceSudo.next_by_code(code) or _('New')
        ##

        p = super(ResPartner, self).create(vals)
        return p


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _search_is_sale(self, operator, operand):
        group_obj = self.env['res.groups']
        sale1 = self.env.ref('sales_team.group_sale_salesman')
        sale2 = self.env.ref('sales_team.group_sale_salesman_all_leads')
        sale3 = self.env.ref('sales_team.group_sale_manager')
        group_obj |= sale1
        group_obj |= sale2
        group_obj |= sale3
        lst_u = []
        for g in group_obj:
            lst_u.extend(g.users.ids)
        lst_u = list(set(lst_u))
        return [('id', 'in', lst_u)]

    @api.depends('groups_id')
    def _compute_is_sale(self):
        for u in self:
            is_sale = False
            if u.has_group('sales_team.group_sale_salesman') or u.has_group(
                    'sales_team.group_sale_salesman_all_leads') or u.has_group('sales_team.group_sale_manager'):
                is_sale = True
            u.is_sale = is_sale

    is_sale = fields.Boolean('Is Sale', compute='_compute_is_sale',
                             search='_search_is_sale'
                             )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('user_company'):
            args.append(('company_id', '=', self.env.user.company_id.id))
            args.append(('is_sale', '=', True))
        return super(ResUsers, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                             access_rights_uid=access_rights_uid)

