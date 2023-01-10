from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    has_pension = fields.Boolean(string='Has Pension')
