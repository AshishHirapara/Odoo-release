from datetime import date
import datetime
from io import StringIO
from operator import index
from pickle import TRUE
from tokenize import group
from odoo import api, fields, models
import os
import lxml.html
from lxml import etree
import fitz
from PyPDF2 import PdfFileReader, PdfFileWriter
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

from odoo.exceptions import UserError


class ChildTechnicalRules(models.Model):
    _name='child.technical.rules'


    parent_rule_id = fields.Many2one('technical.rules', string='Parent Technical Rule', required=True)
    rule_name = fields.Char(string='Criteria Name', required=True)
    remark = fields.Text(string='Remark')
    point_given = fields.Integer(string='Point', required=True)
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'Dropdown'),
         ('tick', 'Check'),
         ('number', 'Number Input Value'),
         ], string="Input Type")
    selection = fields.Many2many('technical.selection.field', string='Selection')
    selection_view = fields.Boolean('To view selection')
    number = fields.One2many('number.variant.rule', 'child_rule_id',string='Number Variant Rule')

    @api.model
    def create(self, vals):
        parent = self.env['technical.rules'].search([('id', '=', vals['parent_rule_id'])])
        total = 0
        for child in  parent.child_rule_ids:
            total += child['point_given']
        total += vals['point_given']
        if total > parent['weight']:
            raise UserError(('Please correct the parent rule weight its exceeding the total.'))
            
        res = super(ChildTechnicalRules, self).create(vals)
        return res


class TechnicalSelectionField(models.Model):
    _name = 'technical.selection.field'
    _description = 'Technical selection field'

    name = fields.Char(string='Selection name', required=True)
    value = fields.Float(string="Selection value")
    child_rule_id = fields.Many2one('child.technical.rules', string='Rule')


class NumberVariantSelection(models.Model):
    _name = 'number.variant.rule'
    _description = 'Number Variant Rule'

    amount = fields.Float(string="Amount")
    value = fields.Float(string="value")
    child_rule_id = fields.Many2one('child.technical.rules', string='Rule')
