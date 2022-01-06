from odoo import http
from odoo.addons.restful.controllers.main import validate_token, APIController
from odoo.addons.restful.common import (extract_arguments, invalid_response,
                                        valid_response)
from odoo.http import request
import json

_routes = ["/ipp/<model>", "/ipp/<model>/<id>", "/ipp/<model>/<id>/<action>"]


class APIController(APIController):
    """."""

    @validate_token
    @http.route('/ipp/get_sale_order', type="http", auth="none", methods=["GET"], csrf=False)
    def get_sale_order(self, model=None, id=None, **payload):
        """."""
        # print("quan ga", payload.get('domain'))
        so_obj = request.env['sale.order'].sudo()
        domain, fields, offset, limit, order = extract_arguments(payload)
        res = []
        if domain:
            for so in so_obj.search(domain):
                lst_sol = []
                for line in so.order_line:
                    line_val = {
                        'id': line.id,
                        'name': line.name or '',
                        'product_id': line.product_id.id or False,
                        'product_name': line.product_id.name or '',

                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_uom and line.product_uom.id or False,
                        'product_uom': line.product_uom and line.product_uom.name or '',

                        'qty_delivered': line.qty_delivered,
                        'qty_invoiced': line.qty_invoiced,
                        'price_subtotal': line.price_subtotal,
                        'price_tax': line.price_tax,
                        'price_total': line.price_total,
                    }
                    lst_sol.append(line_val)

                so_val = {
                    'user_id': so.user_id and so.user_id.id or False,
                    'partner_id': so.partner_id.id,
                    'partner_code': so.partner_id.default_code or '',
                    'partner_invoice_id': so.partner_invoice_id and so.partner_invoice_id.id or False,
                    'partner_invoice_name': so.partner_invoice_id and so.partner_invoice_id.name or '',
                    'partner_shipping_id': so.partner_invoice_id and so.partner_shipping_id.id or False,
                    'partner_shipping_name': so.partner_invoice_id and so.partner_shipping_id.name or '',
                    'channel': '',
                    'code': so.name or '',
                    'create_date': so.create_date or '',
                    'date_order': so.date_order or '',
                    'company_id': so.company_id and so.company_id.id or False,
                    'company_name': so.company_id and so.company_id.name or False,
                    'note': so.note,
                    'status': so.state,
                    'order_line_items': lst_sol
                }
                res.append(so_val)

        return valid_response(res)
