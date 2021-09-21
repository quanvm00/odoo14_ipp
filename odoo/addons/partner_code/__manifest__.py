# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner code',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Partner code',
    'description': """
Partner code
""",
    'depends': ['base', 'sale',
                'stock', 'sale_stock',
                'report_xlsx'],
    'data': [
        'views/res_partner_views.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
