# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        return super(StockMove, self).write(values)

    # def _action_done(self, cancel_backorder=False):
    #     result = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
    #     for line in result.mapped('sale_line_id').sudo():
    #         line.product_uom_qty = line._get_product_qty()
    #     return result

    def _action_cancel(self):
        result = super(StockMove, self)._action_cancel()
        for move in self:
            qty = move.sale_line_id.product_uom_qty - move.product_uom_qty
            if move.sale_line_id and qty >= 0 and not move.to_refund:
                # if move.sale_line_id and qty >= 0 and move.sale_line_id.qty_delivered == 0:
                move.sale_line_id.product_uom_qty = qty
        return result

    def _action_done(self, cancel_backorder=False):
        for m in self:
            if m.quantity_done > m.product_uom_qty:
                raise ValidationError(_('You cannot validate because qty Done > qty Demand.'))
        result = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        for move in result.filtered('to_refund'):
            for sol in move.mapped('sale_line_id').sudo():
                if sol.product_uom_qty < sol._get_return_product_qty(move):
                    raise ValidationError(_('You can not return with large Qty with Sale order Lines!'))
                a = sol.product_uom_qty - sol._get_return_product_qty(move)
                # if a < sol.product_uom_qty:
                sol.product_uom_qty = a
        return result
