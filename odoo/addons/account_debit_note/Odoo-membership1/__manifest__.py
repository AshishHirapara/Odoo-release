
{
    'name': 'Membership',
    'version': '1.0',
    'category': 'Extra-tools',
    'description': "",
    "author": " ",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/membership_invoice_views.xml',
        'data/membership_data.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/membership_tempate.xml',
        'report/report_membership_views.xml',
    ],
      'assets': {
        'web.assets_frontend': [
            'custom_web/static/src/css/customstyle.css',
            'custom_web/static/src/js/custom.js',
    ]},
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
