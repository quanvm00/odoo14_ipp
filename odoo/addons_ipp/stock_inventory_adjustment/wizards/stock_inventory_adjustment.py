# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions
import xlrd, os, base64

class ReportRowDataWizard(models.TransientModel):
    _name = 'stock.inventory.adjustment.wizard'
    _description = 'Inventory Adjustment Wizard'

    name = fields.Char('Name', default='New')
    line_ids = fields.One2many('stock.inventory.adjustment.wizard.line', 'wizard_id')
    file = fields.Binary('File')
    filename = fields.Char('File Name')

    @api.onchange('file')
    def onchange_file(self):
        company_obj = self.env['res.company'].sudo()
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']
        production_lot_obj = self.env['stock.production.lot']
        if not self.file:
            return

        book = xlrd.open_workbook(file_contents=base64.b64decode(self.file) or b'')
        sheets = book.sheet_names()
        for sheet_name in sheets:
            company_id = company_obj.search(['|',('name','=',sheet_name),('code','=',sheet_name)])
            if not company_id:
                raise exceptions.UserError('The company %s not exists. Please check again.' % sheet_name)

            line_ids = []
            sheet = book.sheet_by_name(sheet_name)
            for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows))):
                product_id = product_obj.search([('type', '=', 'product'),('default_code','=',row[0].value),
                                                 '|', ('company_id', '=', False), ('company_id', '=', company_id.id),], limit=1)

                # get products
                if not product_id:
                    raise exceptions.UserError('The product %s not exists in company %s. Please check again.' % (row[0].value, company_id.name))

                # get stock location
                location_id = location_obj.search([('code', '=', row[1].value),('company_id', '=', company_id.id),
                                                   ('usage', 'in', ['internal', 'transit'])], limit=1)

                # get products
                if not location_id:
                    raise exceptions.UserError('The location %s not exists in company %s. Please check again.' % (row[1].value, company_id.name))

                # get products lot
                lot_id = production_lot_obj.search([('name','=',row[2].value),('product_id','=',product_id.id),('company_id','=',company_id.id)])
                if not lot_id:
                    lot_id = production_lot_obj.create({
                        'name': row[2].value,
                        'product_id': product_id.id,
                        'company_id': company_id.id,
                    })
                line_ids.append((0, 0, {
                    'product_id': product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                    'company_id': company_id.id,
                    'location_id': location_id.id,
                    'prod_lot_id': lot_id.id,
                    'product_qty': row[3].value,
                }))
            self.line_ids = line_ids

    def import_xls(self):
        inventory_obj = self.env['stock.inventory']
        inventory_adjustment_ids = []
        for company_id in list(set([rec.company_id.id for rec in self.line_ids])):
            line_ids = self.line_ids.filtered(lambda l: l.company_id.id == company_id)
            # create Inventory Adjustment
            inventory_id = inventory_obj.create({
                'location_ids': [(6, 0, list(set([line.location_id.id for line in line_ids])))],
                'product_ids': [(6, 0, list(set([line.product_id.id for line in line_ids])))],
                'company_id': company_id,
                'exhausted': True,
            })
            inventory_id.action_start()
            for line in inventory_id.line_ids:
                line_id = line_ids.filtered(lambda l: l.product_id.id == line.product_id.id and l.location_id.id == line.location_id.id)
                line.write({'product_qty':line_id.product_qty})
            inventory_adjustment_ids.append(inventory_id.id)
        action = self.env.ref('stock.action_inventory_form').read([])[0]
        action['domain'] = [('id','in',inventory_adjustment_ids)]
        return action


class ReportRowDataWizardLine(models.TransientModel):
    _name = 'stock.inventory.adjustment.wizard.line'
    _description = 'Inventory Adjustment Wizard Line'

    wizard_id = fields.Many2one('stock.inventory.adjustment.wizard')
    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True,
        index=True, required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True, readonly=False)
    product_qty = fields.Float(
        'Counted Quantity',
        digits='Product Unit of Measure', default=0)
    categ_id = fields.Many2one(related='product_id.categ_id', store=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', check_company=True,
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]",
        index=True, required=True)
    package_id = fields.Many2one(
        'stock.quant.package', 'Pack', index=True, check_company=True,
        domain="[('location_id', '=', location_id)]",
    )
    prod_lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number', check_company=True,
        domain="[('product_id','=',product_id), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', index=True, readonly=False, store=True)
    product_tracking = fields.Selection(string='Tracking', related='product_id.tracking', readonly=True)
