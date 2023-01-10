from email.policy import default
from odoo import _, api, models, fields
import logging
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError,Warning ,ValidationError
from datetime import datetime, timedelta
import requests, re
from collections import defaultdict
from odoo.exceptions import UserError,Warning 

class PayrollParnetStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    parent_name = fields.Many2one('hr.payroll.structure' ,string="Parent Name",index=True, store=True)
    rule_ids = fields.One2many('hr.salary.rule', 'struct_id', string='Salary Rules', default={})
 
    
    @api.onchange('parent_name')
    def _compute_structure_parent(self):
        _logger.info(datetime.now())
        _logger.info(self.name)
        _logger.info(self.rule_ids)
        str_type = self.env['hr.payroll.structure'].sudo().search([('id','=', self.parent_name.id)])
        rules = []
        _logger.info("****************payroll**********")
        _logger.info(str_type.name)
        
        for l in range(len(str_type)):
            for line in str_type.rule_ids:
                _logger.info("oooooooooooooooooooooooooooooooooo")
                
                val = {}
                val['name']= line.name
                val['code']= line.code
                val['category_id'] =  line.category_id
                val['partner_id'] = line.partner_id.id
               
                rules.append((0,0, val))
        self['rule_ids'] = rules
        _logger.info(self['rule_ids'])

class PayrollContract(models.Model):
    _inherit = 'hr.contract'
    
    stucture_type_selector = fields.Many2one('hr.payroll.structure' ,string="Salary Structure Type",index=True, store=True)
    
 