# -*- coding: utf-8 -*-

{
    "name": "Sales Organization",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    "summary": "Sales Organization",
    'description': "Sales Organization",
    'category': 'Sales',
    'author': '',
    'company': '',
    'website': '',
    'depends': [
        'base',
        'crm',
        'sale',
        'account',
        'stock', 'restful'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/master_data_menu.xml',
        'views/region_area_view.xml',
        'views/res_company_view.xml',
        "views/account_fiscal_year_views.xml",
        'views/stock_location_view.xml',
    ],
    'images': [],

    'installable': True,
    'auto_install': False,
}
