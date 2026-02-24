# -*- coding: utf-8 -*-
{
    'name': 'Custom Invoice Reports',
    'version': '15.0.1.0.29',
    'category': 'Accounting',
    'summary': 'Customizable Invoice Reports with Previous Credit Display',
    'description': """
Custom Invoice Reports
======================
* New customizable invoice report for accounting module
* New customizable invoice report for POS module
* Show previous credit amount in invoice
* Customizable report format (logo alignment, font sizes, etc.)
* PDF download button
    """,
    'author': 'Ahmad_odoo5',
    'website': 'https://www.linkedin.com/in/ahmad-odoo5/',
    'license': 'LGPL-3',
    'maintainers': ['AM Odoo Solutions'],
    'price': 50.59,
    'currency': 'USD',
    'depends': ['account', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/invoice_report_settings_views.xml',
        'report/custom_invoice_report_templates.xml',
        'report/custom_invoice_reports.xml',
        'data/report_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'odoo_custom_invoice/static/src/js/auto_invoice_print.js',
            'odoo_custom_invoice/static/src/js/payment_screen.js',
            'odoo_custom_invoice/static/src/js/pos_invoice.js',
            'odoo_custom_invoice/static/src/js/previous credit.js',
            'odoo_custom_invoice/static/src/xml/payment_screen.xml',
        ],
        'web.report_assets_common': [
            'odoo_custom_invoice/static/src/scss/report.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}
