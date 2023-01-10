# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    selected = fields.Boolean('Selected Price', default=False)

    
    
class PurchaseOrderLineUnlink(models.Model):
    _inherit = 'purchase.order.line.unlink'
    selection = fields.Selection([
        ("selected", "selected"),
        ("failed", "failed"),
         ], default='failed')
    reason = fields.Char('Reason')

    
    # def _add_supplier_to_product(self):
    #     # Add the partner in the supplier list of the product if the supplier is not registered for
    #     # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
    #     # could be caused for some generic products ("Miscellaneous").
    #     if self.selection == "selected":
    #         # Do not add a contact as a supplier
    #         partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
    #         if self.order_line.product_id and partner not in self.order_line.product_id.seller_ids.mapped('name') and len(self.order_line.product_id.seller_ids) <= 10:
    #             # Convert the price in the right currency.
    #             currency = partner.property_purchase_currency_id or self.env.company.currency_id
    #             price = self.currency_id._convert(self.price_unit, currency, self.order_line.company_id, self.order_line.date_order or fields.Date.today(), round=False)
    #             # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
    #             if self.order_line.product_id.product_tmpl_id.uom_po_id != self.order_line.product_uom:
    #                 default_uom = self.order_line.product_id.product_tmpl_id.uom_po_id
    #                 price = self.order_line.product_uom._compute_price(price, default_uom)

    #             supplierinfo = {
    #                 'name': partner.id,
    #                 'sequence': max(self.order_line.product_id.seller_ids.mapped('sequence')) + 1 if self.order_line.product_id.seller_ids else 1,
    #                 'min_qty': 0.0,
    #                 'price': price,
    #                 'currency_id': currency.id,
    #                 'delay': 0,
    #             }
    #             # In case the order partner is a contact address, a new supplierinfo is created on
    #             # the parent company. In this case, we keep the product name and code.
    #             seller = self.order_line.product_id._select_seller(
    #                 partner_id=self.order_line.partner_id,
    #                 quantity=self.order_line.product_qty,
    #                 date=self.order_line.order_id.date_order and self.order_line.order_id.date_order.date(),
    #                 uom_id=self.order_line.product_uom)
    #             if seller:
    #                 supplierinfo['product_name'] = seller.product_name
    #                 supplierinfo['product_code'] = seller.product_code
    #             vals = {
    #                 'seller_ids': [(0, 0, supplierinfo)],
    #             }
    #             self.order_line.product_id.write(vals)

    # def button_confirm(self):
    #    # if self.order_line.state not in ['draft', 'sent']:
    #      #   continue
    #     self.order_line._add_supplier_to_product()
    #         # Deal with double validation process
    #     if self.order_line.company_id.po_double_validation == 'one_step'\
    #                 or (self.order_line.company_id.po_double_validation == 'two_step'\
    #                     and self.price_total < self.env.company.currency_id._convert(
    #                         self.order_line.company_id.po_double_validation_amount, self.order_line.currency_id, self.order_line.company_id, self.order_line.date_order or fields.Date.today()))\
    #                 or self.order_line.user_has_groups('purchase.group_purchase_manager'):
    #             self.order_line.button_approve()
    #     else:
    #             self.order_line.write({'state': 'to approve'})
    #             return True