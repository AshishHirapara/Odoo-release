# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from email.policy import default
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang

PURCHASE_REQUISITION_STATES = [
    ('draft', ),
    ('ongoing', ),
    ('in_progress', ),
    ('open', ),
    ('system_min_selection', 'Confirm System Result'),
    ('done', ),
    ('cancel', )
]

COMPUTATION_TYPES = [
    ('individual_items', 'Compute Individual'),
    ('total', 'Compute Total')
]

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    state = fields.Selection(selection_add=PURCHASE_REQUISITION_STATES)
    state_blanket_order = fields.Selection(selection_add=PURCHASE_REQUISITION_STATES)

    def filterTheDict(dictObj, callback):
        newDict = dict()
        for (key, value) in dictObj.items():
            if callback((key, value)):
                newDict[key] = value
        return newDict

    def action_Previous(self):
        self.write({'state': 'open'})

    def to_be_confirmed(self):
        self.write({'state': 'system_min_selection'})

    def action_confirm_system_result(self):
        selected_from_total = self.purchase_ids.filtered(lambda r: r.selected == False)
        for item in selected_from_total:
            item.state = 'cancel'
            item.write({"state":'cancel'})
        self.write({'state': 'done'})

    def individuals_selected_before(self):
        selected_from_individual = self.line_id_2.filtered(lambda r: r.selection == 'selected')
        if len(selected_from_individual) >0:
            return True

    def total_selected_before(self):
        selected_from_total = self.purchase_ids.filtered(lambda r: r.selected == True)
        if len(selected_from_total) >0:
            return True

    def check_for_new_total_added(self):
        selected_from_total = self.purchase_ids.filtered(lambda r: r.selected == True)
        if self.state == 'open':
            all_listed_totals = self.purchase_ids
            minPricedTotal = min(all_listed_totals, key=lambda x:x['amount_total'])
            for selected in selected_from_total:
                if selected.amount_total > minPricedTotal.amount_total:
                    selected.selection = False
                    selected.write({"selected":False})
                    minPricedTotal.selection = True
                    minPricedTotal.write({"selected":True})
                    for order in minPricedTotal.order_line:
                        order.write({"selection":'selected'})

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
            

    def check_for_new_individual_added(self):
        selected_from_individual = self.line_id_2.filtered(lambda r: r.selection == 'selected')
        individual_name = self.line_id_2.filtered(lambda r: r.selection == 'selected').mapped('name')
        with_different_product = []
        selected = []
        
        if self.state == 'open':
            for name in individual_name:
                individuals = self.line_id_2.filtered(lambda r: r.name == name)
                with_different_product.append(individuals)
                individuals2 = selected_from_individual.filtered(lambda r: r.name == name)
                selected.append(individuals2)

            zipped_items = zip(with_different_product, selected)
            for an_item in zipped_items:
                minPricedItem = min(an_item[0], key=lambda x:x['price_unit'])
                for item in an_item[0]:
                    if minPricedItem.id != item.id:
                        minPricedItem.selection = 'failed'
                        minPricedItem.write({"selection":'failed'})
                        minPricedItem.selection = 'selected'
                        minPricedItem.write({"selection":'selected'})
                

    def action_individal(self):
        if len(self.line_id_2) == 0:
            raise UserError(_('No Quotations yet'))
        else:
             prevously_selected = self.individuals_selected_before()
             if prevously_selected:
                 self.check_for_new_individual_added()
             else:
                self.check_for_any_results(individual_has_been_clicked=True)
                products_with_price = []
                for products in self.line_id_2:
                    each_product_with_price = {
                        'id': products.id,
                        'vendor': products.name,
                        'quantity': products.product_qty,
                        'unit_price': products.price_unit,
                        'subtotal_price': products.price_subtotal,
                        'total_price': products.price_total,
                        'price_tax': products.price_tax,
                        'selection': products.selection,
                        'product' : products.product_id.name
                    }
                    products_with_price.append(each_product_with_price)

                product_names = [d['product'] for d in products_with_price if d['product'] != ""]
                listed_product_names = list(set(product_names))

                same_key_list = []
                for name in listed_product_names:
                    nameOfProduct = name
                    thesamekey = []
                    for item in products_with_price:
                        if(nameOfProduct in item.values()):
                            thesamekey.append(item)
                    same_key_list.append(thesamekey)

                allSmallPriced =[]
                for sameproducts in same_key_list:
                    minPricedItem = min(sameproducts, key=lambda x:x['unit_price'])          
                    allSmallPriced.append(minPricedItem)
                for small in allSmallPriced:
                    record = self.env['purchase.order.line.unlink'].search([('id', '=', small['id'])])
                    record.selection = 'selected'
                    record.write({"selection":'selected'})
             self.to_be_confirmed()



    def action_total(self):
        if len(self.purchase_ids) == 0:
            raise UserError(_('No Quotations yet'))
        else:
            prevously_selected = self.total_selected_before()
            if prevously_selected:
                 self.check_for_new_total_added()
            self.check_for_any_results(total_has_been_clicked=True)
            orders_with_price = []
            for order in self.purchase_ids:
                each_product_with_price = {
                    'id': order.id,
                    'amount_total': order.amount_total,
                    'company_id': order.company_id.name,
                    'selected': order.selected,
                    'name': order.name,
                    'product_id': order.product_id.display_name
                }
                orders_with_price.append(each_product_with_price)
            
            minPricedItem = min(orders_with_price, key=lambda x:x['amount_total'])
            record = self.env['purchase.order'].search([('id', '=', minPricedItem['id'])])
            record.selection = 'selected'
            record.write({"selected":True})
            for order in record.order_line:
                order.write({"selection":'selected'})
            self.to_be_confirmed()

    def check_for_any_results(self, individual_has_been_clicked=False, total_has_been_clicked=False):

        if(total_has_been_clicked):
            all_list = self.line_id_2.filtered(lambda r: r.selection == 'selected')
            for selected_product in all_list:
                selected_product.selection = 'failed'
                selected_product.write({"selection":'failed'})
        
        if(individual_has_been_clicked):
            all_list = self.purchase_ids.filtered(lambda r: r.selected == True)
            for selected_product in all_list:
                selected_product.selected = False
                selected_product.write({"selected":False})
                for items in selected_product.order_line:
                    items.selection = 'failed'
                    items.write({"selection":'failed'})


