from odoo import http
from odoo.http import request
class ComplaintController(http.Controller):
    
   @http.route('/addComplaint', type='http', auth='public', website=True, methods=['POST'])
   def addComplaint(self , **kwargs):
       loggedIn_user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
       loggedIn_user_partner_id = loggedIn_user.partner_id.id
       created_complaint = request.env['member.complaint'].sudo().create({
           'issue_subject': kwargs.get('issue_subject'),
           'issue_body': kwargs.get('issue_body'),
           'issue_date': kwargs.get('issue_date'),
           'partner_id': loggedIn_user_partner_id
       })
       status = {}
       if created_complaint:
           status['status'] = "Success"
           status['message'] = "You have successfull added your compliant"
       else:
           status['status'] = "Fail"
           status['message'] = "You have not successfull added your compliant"
       
       return  request.render('membership.compliant_form', {'status': status})
    
   @http.route('/allComplaints', type='http', auth='public', website=True, methods=['GET'])
   def addComplaint(self , **kwargs):
       loggedIn_user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
       loggedIn_user_partner_id = loggedIn_user.partner_id.id
       
       all_compliants = request.env['member.complaint'].sudo().search([('partner_id', '=', loggedIn_user_partner_id)])
       return  request.render('membership.compliant_list', {'all_compliants': all_compliants})