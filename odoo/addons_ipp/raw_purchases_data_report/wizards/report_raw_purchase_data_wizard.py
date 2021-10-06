# -*- coding: utf-8 -*-
import calendar
from odoo import api, fields, models
import time
from datetime import timedelta, datetime, date
import pytz
import json
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

LIST_YEAR = [(str(num), str(num)) for num in range(2020, (datetime.now().year) + 1)]
DICT_MONTH = {'1': 'January', '2': 'February', '3': 'March', '4': 'April',
              '5': 'May', '6': 'June', '7': 'July', '8': 'August',
              '9': 'September', '10': 'October', '11': 'November', '12': 'December'
              }


# LIST_YEAR = [('2021', '2021')]


class ReportRowDataWizard(models.TransientModel):
    _name = 'report.raw.purchases.data.wizard'
    _description = 'Report Raw Purchases Data Wizard'

    def _get_default_categ_ids(self):
        cate_obj = self.env['product.category']
        lst_cate = cate_obj.search([('child_id', '=', False)])

        return lst_cate.ids

    def _default_month(self):
        now = datetime.now()
        return str(now.month)

    def _default_year(self):
        now = datetime.now()
        return str(now.year)

    def _get_default_date_from(self):
        return datetime.today().replace(day=1)

    def _get_default_date_to(self):
        today = datetime.today()
        y = today.year
        m = today.month
        i, c = calendar.monthrange(y, m)
        last_day = datetime(y, m, c)
        return last_day

    company_id = fields.Many2one('res.company', string='Company')

    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string='Month', required=True, default=_default_month)
    year = fields.Selection(
        [('2021', '2021')]
        , string='Year', required=True, default=_default_year)

    # year = fields.Selection(
    #     # LIST_YEAR
    #     ([(num, str(num)) for num in range(2021, (datetime.now().year) + 1)], 'Year')
    #     , string='Year', required=True, default=_default_year)

    categ_ids = fields.Many2many('product.category', 'reportrowdata_cate_rel', 'wizard_id', 'categ_id',
                                 'Product Categories',
                                 default=_get_default_categ_ids
                                 )
    use_range_date = fields.Boolean(string='Use Range Date', default=False, copy=False)
    date_from = fields.Date(string='From', default=_get_default_date_from)
    date_to = fields.Date(string='To', default=_get_default_date_to)

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'wizard': self
        }
        return {'type': 'ir.actions.report',
                'data': {'model': 'report.raw.purchases.data.wizard',
                         'options': json.dumps(data, default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'Raw data',
                         },
                'report_type': 'xlsx'}


    def convert_tz_utc(self, dt):
        tz = self.env['res.users'].browse(self._uid).tz
        if tz:
            import pytz

            utc = pytz.timezone('UTC')
            tz = pytz.timezone(tz)
            tz_timestamp = tz.localize(dt, is_dst=False)
            utc_timestamp = tz_timestamp.astimezone(utc)
            str_dt = datetime.strftime(utc_timestamp, DEFAULT_SERVER_DATETIME_FORMAT)
            return str_dt
        else:
            return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def generate_header(self, sheet, workbook, month, year, wizard):
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
             'bold': True})
        format1.set_align('center')
        str_header = 'REPORT IN : ' + DICT_MONTH[month] + ', ' + str(year)
        if wizard.use_range_date:
            a1 = datetime.strptime(str(wizard.date_from), '%Y-%m-%d')
            a2 = datetime.strptime(str(wizard.date_to), '%Y-%m-%d')
            str_a1 = a1.strftime('%d/%m/%Y')
            str_a2 = a2.strftime('%d/%m/%Y')
            str_header = 'REPORT IN : %s -> %s' % (str_a1, str_a2)
        sheet.merge_range('A2:G2', str_header, format1)

    def generate_title(self, sheet, workbook):
        format_title = workbook.add_format(
            {'font_size': 11, 'bold': True, 'font_color': '#FFFFFF', 'align': 'center', 'bg_color': '#4BACC6',
             'valign': 'vcenter', 'text_wrap': True})
        row = 3
        col_cate = 0
        lst_title = [
            'Date', 'DTR Code', 'Dist Name',
            'Order Nbr', 'SR Code', 'SR Name', 'Customer Code', 'Customer Name', 'Street',
            'Region/ Area',
            'Province Code', 'Province Name',
            'Product Category Code', 'Product Code', 'Product Name', 'Unit Sold',
            'Price',
            'Amount',
        ]
        sheet.write_row(row, col_cate, lst_title, format_title)
        sheet.set_row(row, 20)

    def get_data(self, wizard):
        limit_row = 1048500
        year = int(wizard.year)
        month = int(wizard.month)
        date_from = wizard.date_from
        date_to = wizard.date_to

        categ_ids = wizard.categ_ids
        lst_po = self.env['purchase.order'].search([('state', 'in', ['done', 'purchase'])

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
        select_str = """
        select
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            count(*) as nbr,
            s.name as name,
            s.date_order as date,
            to_char(s.date_order, 'YYYY-MM-DD HH24:MI:SS') as str_date_order,          
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            t.categ_id as categ_id,
            p.product_tmpl_id,
            l.price_unit as price_unit,
            s.id as order_id,
            c.region_area_id as region_area_id
        """
        from_str = """
        from
            purchase_order_line l
                right outer join purchase_order s on (s.id=l.order_id)
                    join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    join res_company c on s.company_id = c.id
                left join uom_uom u on (u.id=l.product_uom)
                left join uom_uom u2 on (u2.id=t.uom_id)
              
        """
        group_by_str = """
        group by
            l.product_id,
            l.order_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.user_id,
            s.state,
            s.company_id,
            p.product_tmpl_id,
            l.price_unit,
            s.id,
            c.region_area_id
        order by s.date_order
        """
        where_str = """WHERE 
                s.date_order >=%s  
                AND s.date_order <=%s 
                
                AND t.categ_id in %s 
                AND s.state not in  ('draft', 'cancel', 'sent')
                AND s.id in %s
                
                """
        cates = categ_ids.ids
        cates.append(-1)
        sql_filters = (hn_utc, aaa, tuple(cates), tuple(lst_po))
        if wizard.use_range_date:
            sql_filters = (date_from_utc, date_to_utc, tuple(cates), tuple(lst_po))

        sql = ' '.join((select_str, from_str, where_str, group_by_str))

        self.env.cr.execute(sql, sql_filters)
        sr_detail = self.env.cr.dictfetchall()
        if len(sr_detail) <= limit_row:
            return sr_detail
        else:
            return []
        return []

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


    def get_company(self):
        sql = """ SELECT com.id as id, partner.name as name,  COALESCE(partner.default_code, '') as code
                    FROM res_company com
                        INNER JOIN res_partner partner ON (partner.id = com.partner_id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_partner(self):
        sql = """ SELECT id, COALESCE(default_code, '')    as code, name, street FROM res_partner"""
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

    def get_user(self):
        sql = """ SELECT res_user.id as id, partner.name as name, 
                        COALESCE(' ', ' ') as code
                    FROM res_users res_user
                        INNER JOIN res_partner partner ON (partner.id = res_user.partner_id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_partner_province(self):
        sql = """ SELECT partner.id, province.code as code, province.name as name 
                    FROM res_partner partner
                    LEFT JOIN res_country_state province ON (partner.state_id = province.id)
        """
        res = self.get_dict_value(sql)
        return res

    def get_product_category(self):
        sql = """ SELECT id, name,  parent_id  FROM product_category"""
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

    def get_region_area_id(self):
        sql = """ SELECT id, name  FROM region_area"""
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
                        }
                    })
        return res

    def get_product(self):
        sql = """ SELECT p.id as id, p.default_code as code, t.name as name_t, 
                        CONCAT(t.name, ' ') as name
                    FROM product_product p
                    LEFT JOIN product_template t ON (t.id = p.product_tmpl_id)

        """
        res = self.get_dict_value(sql)
        return res

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
        get_partner = self.get_partner()
        get_company = self.get_company()
        get_user = self.get_user()
        get_partner_province = self.get_partner_province()
        get_product = self.get_product()
        get_product_category = self.get_product_category()
        get_region_area = self.get_region_area_id()
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
            region_area_id = line.get('region_area_id', False)
            tmp_date = datetime.strptime(line.get('str_date_order', ''), "%Y-%m-%d %H:%M:%S")
            tmp = self.convert_utc_tz(employee_tz, tmp_date)

            sheet.write(row, col_line, tmp, format_data)
            sheet.write(row, col_line + 1, company_id and get_company[company_id]['code'] or '', format_data)
            sheet.write(row, col_line + 2, company_id and get_company[company_id]['name'] or '', format_data)
            sheet.write(row, col_line + 3, line.get('name', ''), format_data)

            sheet.write(row, col_line + 4, user_id and get_user[user_id].get('code', '') or '', format_data)
            sheet.write(row, col_line + 5, user_id and get_user[user_id]['name'] or '', format_data)
            sheet.write(row, col_line + 6, partner_id and get_partner[partner_id]['code'] or '', format_data)
            sheet.write(row, col_line + 7, partner_id and get_partner[partner_id]['name'] or '', format_data)
            sheet.write(row, col_line + 8, partner_id and get_partner[partner_id]['street'] or '', format_data)
            sheet.write(row, col_line + 9, region_area_id and get_region_area[region_area_id]['name'] or '', format_data)
            sheet.write(row, col_line + 10, partner_id and get_partner_province[partner_id]['code'] or '', format_data)
            sheet.write(row, col_line + 11, partner_id and get_partner_province[partner_id]['name'], format_data)
            sheet.write(row, col_line + 12, categ_id and get_product_category[categ_id]['name'], format_data)
            sheet.write(row, col_line + 13, product_id and get_product[product_id]['code'], format_data)
            sheet.write(row, col_line + 14, product_id and get_product[product_id]['name'], format_data)
            sheet.write(row, col_line + 15, line.get('product_uom_qty', ''), data_body_num_fmt)
            sheet.write(row, col_line + 16, line.get('price_unit', ''), data_body_num_fmt)
            sheet.write(row, col_line + 17, line.get('price_total', ''), data_body_num_fmt)

            row += 1

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Data')
        wizard = self.browse(data['ids'])
        value = self.get_data(wizard)
        year = wizard.year
        month = wizard.month
        self.generate_header(sheet, workbook, month, year, wizard)
        self.generate_title(sheet, workbook)
        self.generate_info(sheet, workbook, value)

        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')

        sheet.set_column(0, 0, 11)
        sheet.set_column(1, 12, 18)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
