from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tin_number = fields.Char(string='Tin Number')

    _sql_constraints = [
                     ('tin_number', 
                      'unique(tin_number)',
                      'A Tin Number already exists. Tin Number must be unique')
    ]