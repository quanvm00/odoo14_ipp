# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Report Excel',
    'version': '14.0.1.0.0',

    'summary': "Report Excel",
    'description': "Report Excel",
    'category': 'Report',
    'author': '',
    'maintainer': '',
    'company': '',
    'website': '',
    'depends': [
        'base', 'stock', 'sale', 'purchase',
        'partner_code',
        'report_xlsx'
    ],
    'data': [
        'views/wizard_view.xml',
        'views/action_manager.xml',
        'security/ir.model.access.csv',

        'wizards/report_row_data_wizard_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
