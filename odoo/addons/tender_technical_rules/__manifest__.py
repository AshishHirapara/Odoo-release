# -*- coding: utf-8 -*-
{
    'name': "Technical Rules",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition'],

    # always loaded
    'data': [
        'data/seq.xml',
        'security/ir.model.access.csv',
        'views/technical_rule_views.xml',
        'views/child_technical_rule_views.xml',
        'views/bid_purchase_requisition_views.xml',
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
