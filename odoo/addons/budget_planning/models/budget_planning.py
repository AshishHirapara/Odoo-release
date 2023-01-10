import logging
from datetime import date
from datetime import datetime, timedelta
import datetime
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


STATES = [
    ('draft', 'Draft'),
    ('requested', 'Request'),
    ('approved', 'Approve'),
    ('rejected', 'Rejected'),
    ('done', 'Done'),
]

class BudgetPlanning(models.Model):
    _name = "budget.planning"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Budget Planning"
    
    
    name = fields.Char('Budget Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    detail_information = fields.One2many(
        "budget.planning.details",
        "budget_id",
        help="Budget Planning detail Information",
    )
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    description = fields.Html(string='Description')
    planned_amount = fields.Float("Planned Amount",readonly=True)
    budgeted_amount = fields.Float("Budgeted Amount", required=True)
    amount_total = fields.Float('Total Planned Amount', readonly=True ,tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False, ondelete='set null',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", check_company=True,
        help="Analytic account to which this project is linked for financial management. "
             "Use an analytic account to record cost and revenue on your project.")
    department = fields.Many2one('hr.department','Department')
    output = fields.Text('Out Put', translate=True)
    budget_planner = fields.Many2one('res.users',"Project Leader")
    employee_id = fields.Many2one('hr.employee', string="employee")
    state = fields.Selection(STATES,
                              'Status', required=True,
                              copy=False, default='draft')
    teams = fields.Many2many('res.users', string='Team Members', tracking=True)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    date = fields.Datetime(string="Date")
    
    partner_id = fields.Many2many('res.partner', string='partner', tracking=True)
    partner_phone = fields.Char(related='partner_id.phone', related_sudo=False, tracking=True)
    partner_email = fields.Char(related='partner_id.email', related_sudo=False, tracking=True)
    alias_enabled = fields.Boolean(string='Use email alias', readonly=False)
    user_id = fields.Many2one('res.users', string='Budget Planner', default=lambda self: self.env.user, tracking=True)
    squ = fields.Char(string='BPF', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
  
    work_stream_line = fields.One2many(
        "work.activity.stream",
        "activity_id",
        help="Work stream budget breakdown",
    )
    compute_field = fields.Boolean(string="check field", compute='get_user')


    @api.depends('compute_field')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('budget_planning.group_requester') and not res_user.has_group('budget_planning.group_request_budget_approval'):
            self.compute_field = True
            
        else:
            self.compute_field = False

    
    def write(self, vals):
        if vals.get('work_stream_line', None) is not None:
            work_stream = vals.get('work_stream_line') 
            budget = 0 
            new_budget = 0
            for work in work_stream:
                if work[2] != False:
                    self.env["work.activity.stream"].sudo().create({
                       "name": work[2]['name'],
                        "target_point":work[2]['target_point'],
                        "budget_amount": work[2]['budget_amount'],
                        "activity_id": self.id  })
            for workstream in self:
                for line in workstream.work_stream_line:
                    new_budget += line.budget_amount
            res = super(BudgetPlanning, self).write({'planned_amount': budget + new_budget })
            return res
       
       
    def _compute_attachment_number(self):
        domain = [('res_model', '=', 'budget.planning'), ('user_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)
            
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'budget.planning'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'budget.planning', 'default_res_id': self.id}
        return res
            

    @api.model
    def create(self, vals):
        if vals.get('squ', _('New')) == _('New'):
            vals['squ'] = self.env['ir.sequence'].next_by_code('budget.planning') or _('New')
        if vals.get('work_stream_line', None) is not None:
            work_stream = vals.get('work_stream_line') 
            budget = 0 
            for work in work_stream:
                budget += work[2]['budget_amount']
            vals.update({'planned_amount':budget})
        res = super(BudgetPlanning, self).create(vals)
        return res

    def action_set_to_draft(self):
        self.state = "draft"
        super(BudgetPlanning, self).write({'state':'draft'})
        
    
    def action_reject(self):
        self.state = "rejected"
        super(BudgetPlanning, self).write({'state':'rejected'})
        

    def action_request(self):
        self.state = "requested"
        super(BudgetPlanning, self).write({'state':'requested'})
        
    def action_approve(self):
        project_name = self.name
        analytic_account = self.name
        search_project = self.env["project.project"].sudo().search([('name','=',project_name)])
        
        if len(search_project) > 0:
            _logger.info("Project Name already exist***************")
        else:
            analytic = self.env["account.analytic.account"].sudo().search([('name','=',analytic_account)])
            
            if analytic.name == analytic_account:
                _logger.info("analytic account exist:--")
            else:
                create_analytic_account = self.env["account.analytic.account"].sudo().create({"name": analytic_account,})
                    
                self.env["project.project"].sudo().create({
                    "name": self.name,
                    "analytic_account_id":create_analytic_account.id,
                    "user_id": self.budget_planner.id,
                })
                
                budget = self.env["budget.budget"].sudo().search([('name','=',project_name)])
                if len(budget) >= 1:
                    _logger.info("analytic account exist:--")
                else:
                    months = 11   
                    self.env["budget.budget"].sudo().create({
                        "name": project_name,
                        "date_from": fields.Date.today(),
                        "date_to": fields.Date.to_string(datetime.now() + timedelta(months))
                    
                    })
                self.state = "approved"
                super(BudgetPlanning, self).write({'state':'approved'})
                
    def action_done(self):
        project_name = self.name
        project = self.env["project.project"].sudo().search([('name','=',project_name)]) 
        for workstream in self.work_stream_line:
                self.env["project.task"].sudo().create({
                        "name": workstream.name,
                        "stage_id": 1,
                        "project_id":project.id,
                        "user_id":self.budget_planner.id,
                        "budget_amount":workstream.budget_amount,
                        "target_area":workstream.target_point
                    })
                
        budget = self.env["budget.budget"].sudo().search([('name','=',project_name)])
     
        # if len(budget) == 1:
        #     days = 10 
        #     months = 11
        #     analytic = self.env["account.analytic.account"].sudo().search([('name','=',budget.name)])
        #     for line in budget:
        #         self.env['budget.lines'].sudo().create({
        #             'budget_id': line.id,
        #             'analytic_account_id' : analytic.id,
        #             'general_budget_id' : budget.id,
        #             'planned_amount': self.planned_amount,
        #             'date_from': fields.Date.today(),
        #             "date_to": fields.Date.to_string(datetime.now() + timedelta(months)),
        #             "paid_date": fields.Date.today(),
        #         })
        self.state = "approved"
        super(BudgetPlanning, self).write({'state':'done'})
                
    def margin_action(self): 
        search_project = self.env["project.project"].sudo().search([('name','=',self.name)])   
        planned_budget = self.env['budget.planning'].sudo().search([('name','=',self.name)])
        
        if planned_budget.name == self.name and self.state == 'done':
            
            date_cal = date.today() + relativedelta(months=+2)
            work_stream =[]
            for line in planned_budget.work_stream_line:
                work_stream.append ((line.name))
                
                # search_project.env['project.task'].sudo().create({
                #     'name': line.name,
                # })
            # n = 0  
            # for task in work_stream:
            #     _logger.info("######################")
            #     _logger.info(task)
            #     # _logger.info(self.project_id)
            #     task_list = self.env['project.task'].sudo().search(['project_id','like',search_project.id])
            #     _logger.info(task_list)
            #     self.env['project.task'].sudo().create({
                    
            #         'name': task
            #     })
            #     _logger.info("************** %s:",search_project)
            #     n +=1

        


class WorkStreamActivity(models.Model):
    _name = "work.activity.stream"
    _description = 'Work Stream Activity'
    

    activity_id = fields.Many2one('budget.planning', string='WorkStreamActivity Reference',help='Relation field', ondelete='cascade', index=True, copy=False)
    
    name = fields.Char('Activity Name',  tracking=True)
    target_point = fields.Char('Target Area',  tracking=True)
    budget_amount = fields.Float('Plane amount',  tracking=True)
    amount_total = fields.Float('Total Planned Amount', readonly=True, compute='_compute_total',  tracking=True)
    
   
class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    
    budgeted_amount = fields.Float('Budgeted amount',  tracking=True)
    used_percentage = fields.Float(
    compute='_compute_budget_percentage', string='Budget Usage',
    help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    unused_percentage = fields.Float(
    compute='_compute_budget_percentage', string='Rest Budget',
    help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
   
    def _compute_budget_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount)
            else:
                line.percentage = 0.00
   


class BudgetPlanningDetails(models.Model):
    _name = "budget.planning.details"
    _description = 'Budget Planning Detail Information'
    
    @api.depends('budget_amount')
    def _compute_total(self):
        """
        Compute the total budget amount of the Work activity.
        """
        amount_total = values = 0.0
        for order in self:
            amount_total = values = 0.0
           
            values += order.budget_amount
            values.append((values))
            # order.update({
                
            #     'amount_total': values + amount_tax,
            # })
    
    name = fields.Char('Activity Name',  tracking=True)
    target_point = fields.Char('Target Area',  tracking=True)
    budget_amount = fields.Float('Planned amount', tracking=True)
    amount_total = fields.Float('Total Planned Amount', readonly=True, compute='_compute_total', tracking=True)
    budget_id = fields.Many2one('budget.planning', string='Budget Reference',help='Relation field', ondelete='cascade', index=True, copy=False)
    
class Task(models.Model):
    _inherit="project.task"
    
    target_area = fields.Char('Target Area')
    budget_amount = fields.Float('Plan Amount')
    
    
