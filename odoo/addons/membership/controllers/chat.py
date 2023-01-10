from odoo import http
from odoo.http import request
class Sale(http.Controller):
    
   @http.route('/my_message', type='http', auth='public', website=True)
   def sale_details(self , **kwargs):
       logged_user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
       sale_details = request.env['mail.message'].sudo().search([('author_id', '=', logged_user.partner_id.id)])
       return  request.render('membership.message_page', {'my_details': sale_details})