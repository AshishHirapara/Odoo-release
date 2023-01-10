from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class SelectionField(models.Model):
    _name = 'selection.field_2'
    _description = 'selection field'

    name = fields.Char(string='selection name', required=True)
    value = fields.Float(string="selection value")
    vendor_document = fields.Many2one('vendor.document', string='vendor document')


class VendorDocument(models.Model):
    _name = 'product.document'
    _description = 'product Documents'

    name = fields.Char(string='Rule name', required=True, copy=False, help='You can give your'
                                                                                 'Document number.')
    description = fields.Text(string='Description', copy=False, help="Description")
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), help="Date of issue", copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Tick'),
         ('price', 'price')
         ], string="Input Type")

    selection = fields.Many2many('selection.field_2', string='selection')
    agreement = fields.Many2one('purchase.requisition', string='agreement')
    selection_view = fields.Boolean('To see selection')
    number = fields.One2many('number.document_2', 'doc',string='numbering')
    value = fields.Float(string="value in %")

    @api.model
    def create(self, vals):
        agreement_id = self.env.context.get('active_ids', [])
        vals.update({'agreement': agreement_id[0],
                      'selection_view': True,
                     })
        return super(VendorDocument, self).create(vals)


class NumberSelection(models.Model):
    _name = 'number.document_2'
    _description = 'numeber Documents'

    amount = fields.Float(string="Amount")
    value = fields.Float(string="value in %")
    doc = fields.Many2one('vendor.document', string='doc')