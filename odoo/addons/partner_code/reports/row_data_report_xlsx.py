# -*- coding: utf-8 -*-

# from datetime import date, datetime, timedelta
from datetime import timedelta, datetime
from odoo import models, fields
import calendar
from odoo.addons.partner_code.reports.str_sql import select_sql, from_sql, group_by_sql, where_sql
from xlsxwriter.utility import xl_rowcol_to_cell
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import random
import pytz

DICT_MONTH = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
              9: 'September', 10: 'October', 11: 'November', 12: 'December'
              }


class RowDataReportXlsx(models.AbstractModel):
    _name = 'report.partner_code.row_data_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def convert_tz_utc(self, dt):
        tz = self.env['res.users'].browse(self._uid).tz
        if tz:
            import pytz
            import datetime
            utc = pytz.timezone('UTC')
            tz = pytz.timezone(tz)
            tz_timestamp = tz.localize(dt, is_dst=False)
            utc_timestamp = tz_timestamp.astimezone(utc)
            str_dt = datetime.datetime.strftime(utc_timestamp, DEFAULT_SERVER_DATETIME_FORMAT)
            return str_dt
        else:
            return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_data(self, wizard):
        limit_row = 1048500
        year = wizard.year
        month = wizard.month
        date_from = wizard.date_from
        date_to = wizard.date_to

        categ_ids = wizard.categ_ids
        lst_so = self.env['sale.order'].search([('state', 'in', ['done', 'sale'])

                                                ]).ids or [-1]
        last_day_of_month = calendar.monthrange(year, month)[1]
        date_start = '{:04d}-{:02d}-01'.format(year, month)
        date_end = '{:04d}-{:02d}-{:02d}'.format(year, month, last_day_of_month)
        hn = fields.Datetime.from_string(date_start)
        hn_utc = self.convert_tz_utc(hn)

        tmr = fields.Datetime.from_string(date_end)
        tmr += timedelta(1)
        b = tmr
        tmr = tmr.strftime('%m/%d/%Y')
        aaa = self.convert_tz_utc(b)

        date_from_str = fields.Datetime.from_string(date_from)
        date_to_str = fields.Datetime.from_string(date_to)

        date_from_utc = self.convert_tz_utc(date_from_str)
        date_to_str += timedelta(1)
        date_to_utc = self.convert_tz_utc(date_to_str)

        # get sql
        select_str = select_sql % self.env['res.currency']._select_companies_rates()
        from_str = from_sql
        group_by_str = group_by_sql
        where_str = where_sql
        cates = categ_ids.ids
        cates.append(-1)
        sql_filters = (hn_utc, aaa, tuple(cates), tuple(lst_so))
        if wizard.use_range_date:
            sql_filters = (date_from_utc, date_to_utc, tuple(cates), tuple(lst_so))
        # print(hn_utc, aaa)
        # print(date_from_utc, date_to_utc)

        sql = ' '.join((select_str, from_str, where_str, group_by_str))

        self.env.cr.execute(sql, sql_filters)
        sr_detail = self.env.cr.dictfetchall()
        if len(sr_detail) <= limit_row:
            return sr_detail
        else:
            return []
        return []

    def generate_header(self, sheet, workbook, month, year, wizard):
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
             'bold': True})
        format1.set_align('center')
        str_header = 'REPORT IN : ' + DICT_MONTH[month] + ', ' + str(year)
        if wizard.use_range_date:
            import datetime
            a1 = datetime.datetime.strptime(wizard.date_from, '%Y-%m-%d')
            a2 = datetime.datetime.strptime(wizard.date_to, '%Y-%m-%d')
            str_a1 = a1.strftime('%d/%m/%Y')
            str_a2 = a2.strftime('%d/%m/%Y')
            str_header = 'REPORT IN : %s -> %s' % (str_a1, str_a2)
        sheet.merge_range('A2:G2', str_header, format1)

    def get_dict_value(self, sql):
        res = {}
        if sql:
            self.env.cr.execute(sql)
            value = self.env.cr.dictfetchall()
            for line in value:
                if line['id'] not in res:
                    res.update({
                        line['id']: {
                            'name': line['name'] or '',
                            'code': line['code'] or ''}
                    })
        return res

    def get_area(self):
        sql = """ SELECT id, name, code FROM res_area"""
        res = self.get_dict_value(sql)
        return res

    def get_partner(self):
        sql = """ SELECT id, default_code as code, name, street FROM res_partner"""
        res = {}
        if sql:
            self.env.cr.execute(sql)
            value = self.env.cr.dictfetchall()
            for line in value:
                if line['id'] not in res:
                    res.update({
                        line['id']: {
                            'name': line['name'] or '',
                            'code': line['code'] or '',
                            'street': line.get('street', ''),
                        }
                    })
        return res

    def get_partner_province(self):
        sql = """ SELECT partner.id, province.code as code, province.name as name 
                    FROM res_partner partner
                    LEFT JOIN res_province province ON (partner.province_id = province.id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_province(self):
        sql = """ SELECT id, code, name FROM res_province"""
        res = self.get_dict_value(sql)
        return res

    def get_company(self):
        sql = """ SELECT com.id as id, partner.name as name, partner.default_code as code
                    FROM res_company com
                        INNER JOIN res_partner partner ON (partner.id = com.partner_id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_user(self):
        sql = """ SELECT res_user.id as id, partner.name as name, 
                        COALESCE(res_user.erp_code, ' ') as code
                    FROM res_users res_user
                        INNER JOIN res_partner partner ON (partner.id = res_user.partner_id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_product(self):
        sql = """ SELECT p.id as id, p.default_code as code, t.name as name_t, 
                        CONCAT(t.name, t.name_option1) as name
                    FROM product_product p
                    LEFT JOIN product_template t ON (t.id = p.product_tmpl_id)
        
        """
        res = self.get_dict_value(sql)
        return res

    def get_product_category(self):
        sql = """ SELECT id, name, code, parent_id  FROM product_category"""
        # res = self.get_dict_value(sql)
        res = {}
        if sql:
            self.env.cr.execute(sql)
            value = self.env.cr.dictfetchall()
            for line in value:
                if line['id'] not in res:
                    res.update({
                        line['id']: {
                            'name': line.get('name', ''),
                            'code': line.get('code', ''),
                            'parent_id': line.get('parent_id', 0)
                        }
                    })
        return res

    def generate_title(self, sheet, workbook):
        format_title = workbook.add_format(
            {'font_size': 11, 'bold': True, 'font_color': '#FFFFFF', 'align': 'center', 'bg_color': '#4BACC6',
             'valign': 'vcenter', 'text_wrap': True})
        row = 3
        col_cate = 0
        lst_title = [
            'Date', 'Area Code', 'Area Name', 'SS Code', 'SS Name', 'DTR Code', 'Dist Name',
            'Order Nbr', 'SR Code', 'SR Name', 'Customer Code', 'Customer Name', 'Street',
            'Province Code', 'Province Name',
            'Product Category Code', 'Product Code', 'Product Name', 'Unit Sold',
            'Price', 'Price(NPP)',
            'Discount(%)', 'Discount NPP(%)',
            'Amount', 'Amount(NPP)',
            'From APP'
        ]
        sheet.write_row(row, col_cate, lst_title, format_title)
        sheet.set_row(row, 20)

    def convert_utc_tz(self, employee_tz, dt):
        tz = employee_tz
        if tz:
            tz = pytz.timezone(tz)
            utc = pytz.timezone('UTC')
            utc_timestamp = utc.localize(dt, is_dst=False)
            tz_timestamp = utc_timestamp.astimezone(tz)
            str_dt = datetime.strftime(tz_timestamp, DEFAULT_SERVER_DATETIME_FORMAT)
            return str_dt
        else:
            return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def generate_info(self, sheet, workbook, value):
        format_data = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': True})
        data_body_num_fmt = workbook.add_format({'border': True, 'font_size': 10, 'bold': False, 'align': 'right'})
        data_body_num_fmt.set_num_format('#,##0_);[RED](#,##0);"-"')
        # sheet.set_column(4, 20, 15)
        # sheet.set_column(1, 3, 25)
        get_area = self.get_area()
        get_province = self.get_province()
        get_partner = self.get_partner()
        get_company = self.get_company()
        get_user = self.get_user()
        get_partner_province = self.get_partner_province()
        get_product = self.get_product()
        get_product_category = self.get_product_category()
        row = 4
        col_line = 0

        employee_tz = self.sudo().env.user.tz

        for line in value:
            #  lay      theo    company
            # manager_id = line.get('manager_id', False)
            company_id = line.get('company_id', False)
            user_id = line.get('user_id', False)
            partner_id = line.get('partner_id', False)
            product_id = line.get('product_id', False)
            categ_id = line.get('categ_id', False)
            tmp_date = datetime.strptime(line.get('str_date_order', ''), "%Y-%m-%d %H:%M:%S")
            tmp = self.convert_utc_tz(employee_tz, tmp_date)

            sheet.write(row, col_line, tmp, format_data)
            sheet.write(row, col_line + 5, company_id and get_company[company_id]['code'] or '', format_data)
            sheet.write(row, col_line + 6, company_id and get_company[company_id]['name'] or '', format_data)
            sheet.write(row, col_line + 7, line.get('name', ''), format_data)

            sheet.write(row, col_line + 8, user_id and get_user[user_id].get('code', '') or '', format_data)
            sheet.write(row, col_line + 9, user_id and get_user[user_id]['name'] or '', format_data)
            sheet.write(row, col_line + 10, partner_id and get_partner[partner_id]['code'] or '', format_data)
            sheet.write(row, col_line + 11, partner_id and get_partner[partner_id]['name'] or '', format_data)
            sheet.write(row, col_line + 12, partner_id and get_partner[partner_id]['street'] or '', format_data)
            sheet.write(row, col_line + 13, partner_id and get_partner_province[partner_id]['code'] or '', format_data)
            sheet.write(row, col_line + 14, partner_id and get_partner_province[partner_id]['name'], format_data)
            sheet.write(row, col_line + 15, categ_id and get_product_category[categ_id]['name'], format_data)
            sheet.write(row, col_line + 16, product_id and get_product[product_id]['code'], format_data)
            sheet.write(row, col_line + 17, product_id and get_product[product_id]['name'], format_data)
            sheet.write(row, col_line + 18, line.get('product_uom_qty', ''), data_body_num_fmt)
            sheet.write(row, col_line + 19, line.get('price_unit', ''), data_body_num_fmt)
            sheet.write(row, col_line + 21, line.get('discount', ''), data_body_num_fmt)
            sheet.write(row, col_line + 23, line.get('price_total', ''), data_body_num_fmt)

            row += 1

    def write_cell(self, sheet, row, column, value, format_data):
        sheet.write(row, column, value, format_data)
        return column + 1

    def _get_data_sr(self, sr_id, categ_id, amount, list_aso, amount_total):
        amount_title = 'amount'
        amount_total_title = 'total'
        lst_aso_title = 'list_aso'
        list_aso_total_title = 'total'
        return {sr_id: {
            amount_title: {
                categ_id: amount,
            },
            lst_aso_title: {
                categ_id: list_aso,
                list_aso_total_title: list_aso
            },
            amount_total_title: amount_total + amount
        }}

    def generate_xlsx_report(self, workbook, data, wizard):
        # data in wizard
        year = wizard.year
        month = wizard.month
        value = self.get_data(wizard)
        # res = self._get_data_aso(value)

        sheet = workbook.add_worksheet('Data')
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
        format3.set_align('center')
        font_size_8.set_align('center')

        sheet.set_column(0, 17, 20)
        sheet.set_column(4, 4, 30)
        sheet.set_column(12, 12, 30)
        self.generate_header(sheet, workbook, month, year, wizard)
        self.generate_title(sheet, workbook)
        # self.generate_info(sheet, workbook, value)

        # sheet 2
        # sheet2 = workbook.add_worksheet('ASO')
        # self.generate_info2(sheet2, workbook, res)

# data_sorted = sorted(DATA, key=lambda item: item['ups_ad'])
