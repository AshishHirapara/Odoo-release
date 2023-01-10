from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class RequisitionResult(models.Model):
    _name = "requisition.result"
    _description = 'requisition result'

    order_id = fields.Many2one('purchase.order', string='Purchase order')
    req = fields.Many2one('purchase.requisition', string='Purchase order')
    amount = fields.Float(string="Product result")
    amount_2 = fields.Float(string="Professional result")
    amount_4 = fields.Float(string="Total result")
    amount_3 = fields.Float(string="Adjustment")
    selection = fields.Selection(
        [('pass', 'pass'),
         ('fail', 'fail')
         ], defulet='fail', string="Status")
    reason = fields.Char(string='Reason')


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    _description = 'purchase requisition Documents'

    document_count = fields.Float(compute='_document_count', string='# Documents')
    document_count_2 = fields.Float(compute='_document_count_2', string='# Documents')
    res_one = fields.One2many('requisition.result', 'req', string='Result')

    def _document_count(self):
        for each in self:
            document_ids = self.env['vendor.document'].sudo().search([('agreement', '=', self.id)])
            each.document_count = len(document_ids)

    def _document_count_2(self):
        for each in self:
            document_id = self.env['product.document'].sudo().search([('agreement', '=', self.id)])
            each.document_count_2 = len(document_id)
            print("count", each.document_count_2)

    def document_view(self):
        self.ensure_one()
        return {
            'name': _('Professional Rule'),
            'domain': [],
            'res_model': 'vendor.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Rule
                        </p>'''),
            'limit': 80,
        }

    def document_view_2(self):
        self.ensure_one()
        return {
            'name': _('Product Rule'),
            'domain': [],
            'res_model': 'product.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Rule
                        </p>'''),
            'limit': 80,
        }

    def result(self):
        terms = []
        price_flag = 0
        price = 0
        if self.res_one:
            self.res_one = [(6,0,0)]
        for price in self.purchase_ids:
            price_flag = price_flag + 1
            if price_flag == 1:
                price = price.amount_total
            else:
                if price > price.amount_total:
                    price = price.amount_total

        for pur in self.purchase_ids:
            per_2 = 0
            per = 0
            for rule in pur.rule:
                print("pur.rule", rule.input_type)
                if rule.input_type == 'attach':
                    # if rule.doc_attachment_id:
                        per_2 = per_2 + rule.value
                elif rule.input_type == 'selection':
                    val = 0
                    val = rule.selection.value / 100 * rule.value
                    per_2 = per_2 + val
                elif rule.input_type == 'price':
                    if pur.amount_total == price:
                        per_2 = per_2 + rule.value
                elif rule.input_type == 'tick':
                    if rule.is_pass:
                        per_2 = per_2 + rule.value
            for line in pur.partner_id.rule:
                print("line", line.name, line.input_type)
                if line.input_type == 'attach':
                   if line.doc_attachment_id:
                    per = per + line.value
                elif line.input_type == 'selection':
                    val = 0
                    val = line.selection.value/100 * line.value
                    per = per + val
                elif line.input_type == 'employee':
                    per = per + pur.partner_id.value_2
                elif line.input_type == 'financial':
                    per = per + pur.partner_id.value
                elif line.input_type == 'tick':
                   if line.is_pass:
                     per = per + line.value
            terms.append((0, 0, {
                    'order_id': pur.id,
                    'amount_2': per,
                    'amount':per_2,
                    'amount_4': (per + per_2)/2,
                    'amount_3': (per + per_2)/2,
                }))
        self.res_one = terms
        flag = 0
        for res in self.res_one:
            flag = flag + 1
            if flag == 1:
              amount = res.amount_4
            else:
                if amount < res.amount_4:
                    amount = res.amount_4
        print("amount", amount)
        for res_2 in self.res_one:
            if res_2.amount_4 == amount:
                res_2.selection = 'pass'
            else:
                res_2.selection = 'fail'

    def action_done(self):
        for res_2 in self.res_one:
            if res_2.selection == 'fail':
                res_2.order_id.state = 'cancel'

        return super(PurchaseRequisition, self).action_done()