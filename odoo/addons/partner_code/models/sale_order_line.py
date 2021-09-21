# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.order_line:
                line.write({
                    'qty_confirmed': line.product_uom_qty
                })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_confirmed = fields.Float(string='Confirmed Quantity', digits='Product Unit of Measure', required=True,
                                 default=1.0)

    @api.onchange('product_uom_qty')
    def product_uom_qty_change(self):
        self.qty_confirmed = self.product_uom_qty

    def write(self, values):
        return super(SaleOrderLine, self).write(values)

    def _get_return_product_qty(self, move_ids):
        self.ensure_one()
        qty = 0.0
        for move in move_ids.filtered(lambda r: r.state in ['done'] and not r.scrapped):
            # if move.location_dest_id.usage == "customer":
            #     if not move.origin_returned_move_id:
            #         qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
            if move.location_dest_id.usage != "customer" and move.to_refund and move.origin_returned_move_id:
                qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
            if move.location_dest_id.usage == "customer" and move.to_refund and move.origin_returned_move_id:
                qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
        return qty
