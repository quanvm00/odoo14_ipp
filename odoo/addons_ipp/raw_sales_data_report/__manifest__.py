# -*- coding: utf-8 -*-


{
    "name": "Sales Raw Data",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    "summary": "Sales Raw Data",
    'description': "Sales Raw Data",
    'category': 'Report',
    'author': '',
    'maintainer': '',
    'company': '',
    'website': '',
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    'depends': [
        'base', "web", 'stock', 'sale', 'purchase',
        'partner_code','sales_organization'
    ],
    'data': [
        "views/webclient_templates.xml",
        'views/wizard_view.xml',
        'views/action_manager.xml',
        'security/ir.model.access.csv',

        'wizards/report_raw_sales_data_wizard_view.xml',
    ],
    'images': [],
    "demo": ["demo/report.xml"],

    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
