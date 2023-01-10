# -*- coding: utf-8 -*-
{
    'name': "budget Prepartion",
    'author': "",
    'version' : '1.1',
    'summary': 'Invoices & Payments',
    'sequence': 100,
    'description': """
        Budget preparation & budget approval & implementation 
        ====================
        """,
    'category': 'Accounting/Accounting',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'data/data.xml',
        'security/budget_group_rules.xml',
        'security/ir.model.access.csv',
        'views/budget_planning.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
