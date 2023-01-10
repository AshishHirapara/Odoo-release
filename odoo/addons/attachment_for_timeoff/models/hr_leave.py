from odoo import api, fields, models


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    attachment = fields.Binary(string="Attachment")
    attachment_name = fields.Char(string='File Name')