# -*- coding: utf-8 -*-


{
    "name": "Sale MCP",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    "summary": "Sale MCP",
    'description': "Sale MCP",
    'category': 'Sale',
    'author': '',
    'company': '',
    'website': '',
    'depends': [
        'crm',
        'sales_organization'

    ],
    'data': [

        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/mcp_mcp_view.xml',
        'views/res_partner_view.xml',

        'wizards/sale_gen_mcp_wizard_view.xml',

    ],
    'images': [],

    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
