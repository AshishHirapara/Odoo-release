from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class BidPurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    rules_count = fields.Integer(compute='_rules_count', string='# Rules')
    rules_ids = fields.One2many('technical.rules', 'requestion_id', 'Rules')

    def _rules_count(self):
        for each in self:
            rules_ids = self.env['technical.rules'].search([('requestion_id', '=', each['id'])])
            each.rules_count = len(rules_ids)

    def rule_view(self):
        self.ensure_one()
        #(ensured["id"], 'in', [rule.requestion_id.id for rule in self.rules_ids])
        return {
            'name': _('Rules'),
            'domain': [],
            'res_model': 'technical.rules',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Rules
                        </p>'''),
            'limit': 80,
        }

