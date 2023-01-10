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


class TechnicalRules(models.Model):
    _name = 'technical.rules'
    _description = 'Mandatory Technical Rules for specific purchase aggrement'


    reference_no = fields.Char(string='Technical Rule Reference', required=True,
                          readonly=True, default='New', index=True)
    rule_name = fields.Char(string='Criteria Name', required=True)
    weight = fields.Integer(string='Weight', required=True)
    child_rule_ids = fields.One2many('child.technical.rules', 'parent_rule_id', 'Rules Under Parent')
    requestion_id = fields.Many2one('purchase.requisition', string='Purchase Aggrement')

    @api.model
    def create(self, vals):
        requestion = self.env.context.get('active_ids', [])
        vals.update({'requestion_id': requestion[0],'selection_view': True,})
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('technical.rules')
        res = super(TechnicalRules, self).create(vals)
        return res

    def name_get(self):
        result = []
        for rec in self:
         result.append((rec.id, '%s - %s' % (rec.rule_name,rec.weight)))  
        return result

