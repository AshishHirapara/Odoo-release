from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class BidingProduct(models.Model):
    _name = 'biding.product'
    _description = 'biding product'
#
    name = fields.Char(string='Rule name')
    # doc_attachment_id = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments')
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Tick'),
         ('price', 'price'),
         ], string="Input Type")
    amount = fields.Float(string="Amount")
    selection = fields.Many2one('selection.field', string='selection')
    rule = fields.Many2one('product.document', string='rule')
    purchase = fields.Many2one('purchase.order', string='vendor')
    value = fields.Float(string="value in %")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = 'Purchase Order'

    rule = fields.One2many('biding.product', 'purchase', string='rule')
    agreement = fields.Many2one('purchase.requisition', string='Purchase agreement')


    @api.onchange('agreement')
    def onchange_input_type(self):
        if self.rule:
            self.rule = [(6, 0, 0)]
        rules = self.env['product.document'].search([('agreement', '=', self.agreement.id)])
        terms = []
        for rule in rules:
            values = {}
            values['name'] = rule.name
            values['input_type'] = rule.input_type
            values['rule'] = rule.id
            values['value'] = rule.value

            terms.append((0, 0, values))
        self.rule = terms
