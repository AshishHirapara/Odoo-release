# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ctypes import sizeof
from http import client
import base64
import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import pprint
import operator
import os
import re
import sys
import tempfile
# from numpy import True_

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata




import odoo
from odoo.addons.base.models.res_partner import Partner
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS




_logger = logging.getLogger(__name__)
import string
# import africastalking



_logger = logging.getLogger(__name__)



class WebRegisteration(AuthSignupHome):
    
    
    @http.route('/success', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.redirect('/shop')
    
    @http.route('/membership/signup', type='http',  auth='public', website=True)
    def membershipsignup(self,  **kw):
        projects = request.env['project.project'].sudo().search([])
        print(projects[0])
        return http.request.render('membership.membership_register', {"projects":projects})

    @http.route('/web/signupform', type='http',  auth='public', website=True)
    def signupform(self,  **kw):
        return http.request.render('membership.membership_register')


    @http.route('/register/reset_password', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.render('custom_web.reset_password')
    
        
    @http.route('/my/profile', type='http',  auth='public', website=True)
    def my_profile(self,  **kw):
        profile = request.env['res.partner'].sudo().search([('id','=',1)])
        return http.request.render('membership.my_profile',{"profile":profile})
          
        
    @http.route('/api/fileupload', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def upload_image(self, **kw):
        _logger.info("##############IN UPLOAD ##############")
        _logger.info(request.httprequest.files.getlist('image'))
        _logger.info(request.httprequest.files.getlist('file'))
        _logger.info(kw)
        
        files = request.httprequest.files.getlist('file')
        _logger.log("########### files:%s",files)


    
    #Mentroship Registration api

    @http.route('/membership_signup',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_signup(self, *args, **kw):
        
        qcontext = self.get_auth_signup_qcontext()
        print(kw)
        _logger.info("qcontext: %s",qcontext)
        
        FileStorage = kw.get('image')
        FileData = FileStorage.read()
        file_base64 = base64.encodestring(FileData)
        projects = request.httprequest.form.getlist('projects[]')
        
        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1).write({"free_member": "1",   
                    "image_1920":file_base64})
            
            for project in projects:
                request.env['project.project'].sudo().search([('name','=', project)], limit=1).write({'project_ids': [(0, 0, [partner_id.id, project.id])]})
                
            # if partner_id:
            #     partner_id.write({
            #         "free_member": "1",   
            #         "image_1920":file_base64
            #         })

            # return request.render('http://207.154.229.160:8069/shop')
            return werkzeug.utils.redirect('/shop')
        
        except UserError as e:
            qcontext['error'] = e.args[0]
       
        # response = request.render('auth_signup.signup', qcontext)
        response = request.render('auth_signup.signup', qcontext)

        response.headers['X-Frame-Options'] = 'DENY'
        return response
      

   
    
    @http.route('/signupformset', type='http', auth='public', website=True, sitemap=False)
    def signupformset(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        try:
            _logger.info("oooooooooooooooooooooooooo")
            self.do_signup(qcontext)
            
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            if partner_id:
                partner_id.write({
                    "free_member": "1",  
                    })
               
            # if res_user_id:
            #     res_user_id.partner_id.write({
            #         "age": kw.get('age'),
            #         "phone": kw.get('phone')
            #     })
            #     res_user_id.write({
            #         "age": kw.get('age')
            #     })
                
            #     _logger.info("res_user: %s", pprint.pformat(res_user_id))
            #     _logger.info("res.partner: %s",  pprint.pformat(partner_id))
                        
            return request.render('register.sign_up_thanks')
            
        
        except UserError as e:
            qcontext['error'] = e.args[0]
       
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
      
      
    #Custome forget password form Website side 
    
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def custom_reset_password(self, *args, **kw):
        _logger.info("############# custom reset password form website ##############")
        _logger.info("Data:%s",kw)
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    # assert phone, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(phone)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response  
    
    
        
        
        
    
    ###### This for Json [APP register Form]
    
    @http.route('/api/registerform', type='json', auth='public', website=False, sitemap=False)
    def registerForm(self, *args, **kw):
        _logger.info("############# Values form Json ###############")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("qcontext: %s",qcontext)

        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                    
            _logger.info("________________________ Write Custom fileds_____________________________")

            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            if res_user_id:
                res_user_id.partner_id.write({
                    "age": kw.get('age'),
                    "phone": kw.get('phone')
                })
                
                _logger.info("res_user: %s", res_user_id)
                _logger.info("res.partner: %s",  partner_id)
                    
                return {
                    "success": True,
                    "message": "Successfully registered"
                        
                        }

            
        except:
            return {
                "success": False,
                "message": "Something went wrong"
                     
            }
            
    
    

        
        
        

        
    
    
 
class CustomSignin(Home):
    
    
    @http.route('/web/signin', type='http',  auth='public', website=True)
    def signin_webform(self,  **kw):
        _logger.info("##########################")
        return http.request.render('register.sign_in_form')
        # return "Hello hkkkku" #request.render('register.sign_up_form',{})
    
    
    ### Website login
     
    @http.route('/membership_signin', type='http',website=True, auth='none')
    def membership_signin(self, redirect=None, **kw): 
        _logger.info("************** Membership  Sign in ****************")
        _logger.info("Data: %s",kw)
        _logger.info(request.params)
        email = kw.get("login")
        password = kw.get("password")
        
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('http://localhost:8069/shop')
        # response = request.render('web.login', values)

        response.headers['X-Frame-Options'] = 'DENY'
        return response
 
       
    
class AuthSignupHome(Home):
    
    # Website Reset Password 
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        _logger.info("**************** custom Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                _logger.info("*********** ***************")
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info("*********** Searching phone number user***************")
                    
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('phone','=',phone)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('phone','=',phone)], limit=1)
                    
                    _logger.info("Search_result:%s User Name: %s  phone: %s",search_user, search_user.name, search_user.phone)
                    # assert phone, _("No phone provided.")
                    _logger.info("search_user:%s",search_user)
                    response = request.render('register.confirm_reset_password',{"search_user":search_user})
                    phont_len = str(phone)
                    _logger.info(len(phont_len))
                    
                    
                    if  search_user.phone != phone:
                        qcontext['error'] = _("Invalid phone number")
                    elif  len(phont_len) == 10 and re.search("^[0-9]+$", phont_len) and search_user.phone == phone is not None:
                        _logger.info("************ 10 digit  right user*************") 
                        
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        ## here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            phone = str(phone)
                            partner_id.write({
                                'verification_code':verification
                            })
                            
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        
                        return response
                    elif  len(phont_len) == 13:
                        _logger.info("************ 13 digits  right user*************") 
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        partner_id.write({
                                'verification_code':verification
                            })
                        ### here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            
                           
                            
                            partner_id.write({
                                'verification_code':verification
                            })
                            _logger.info("verification_code writed on res partner: %s",partner_id.verification_code)
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        return response
                    else:
                        qcontext['error'] = _("Incorrect phone number")
                   
            except UserError as e:
                
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    #confirm password reset with verification
    
    @http.route('/register/web/confirm_reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_confirm_reset_password(self, *args, **kw):
        _logger.info("**************** Confirm Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
               
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('id','=',kw.get('user_id'))], limit=1)
                    _logger.info(search_user)
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    if kw.get('password') != kw.get("cpassword"):
                        qcontext['error'] = _("Password Not Match")

                    elif kw.get('password') == kw.get("cpassword"): # and search_user.phone == phone:
                        _logger.info("************ Correct password  match *************")
                        result = request.env['res.users'].sudo().confirm_reset_password(qcontext)
                        _logger.info("Finallly result: %s",result)
                        
                      
                        response = request.render('register.sign_in_form')
                        
                        return response
                    else:
                        qcontext['error'] = _("Invalid password  ")
                    
            except UserError as e:
                
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.confirm_reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    #App Side password reset
    
    @http.route('/register/api/reset_password', type='json', auth='public', website=False, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        _logger.info("**************** App  Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                _logger.info("*********** ***************")
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info("*********** Searching phone number user***************")
                    
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('phone','=',phone)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('phone','=',phone)], limit=1)
                    
                    _logger.info("Search_result:%s User Name: %s  phone: %s",search_user, search_user.name, search_user.phone)
                    # assert phone, _("No phone provided.")
                    _logger.info("search_user:%s",search_user)
                    # response = request.render('register.confirm_reset_password',{"search_user":search_user})
                    phont_len = str(phone)
                    _logger.info(len(phont_len))
                    
                    
                    if  search_user.phone != phone:
                        qcontext['error'] = _("Invalid phone number")
                    elif  len(phont_len) == 10 and re.search("^[0-9]+$", phont_len) and search_user.phone == phone is not None:
                        _logger.info("************ 10 digit  right user*************") 
                        
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        ## here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            phone = str(phone)
                            partner_id.write({
                                'verification_code':verification
                            })
                            username = "ETTADEV"   # use 'sandbox' for development in the test environment
                            api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
                            africastalking.initialize(username, api_key)
                            sms = africastalking.SMS
                            sms_response = sms.send(f"{verification} is your verification code for ZODO", [f"+251{phone}"],"8707")
                            partner_id.write({
                                'verification_code':verification
                            })
                            return {
                                    "success": True,
                                    "result":{
                                        'verification_code':verification,
                                        'phone':search_user.phone,
                                        'userId':search_user.id
                                    },
                                    "message": "Verfication successfully Sent"
                                    }
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                             return {
                                    "success": False,
                                    "message": "Something went wrong"
                                    }
                            
                        
                       
                    elif  len(phont_len) == 13:
                        _logger.info("************ 13 digits  right user*************") 
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        partner_id.write({
                                'verification_code':verification
                            })
                        ### here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            
                            username = "ETTADEV"   # use 'sandbox' for development in the test environment
                            api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
                            africastalking.initialize(username, api_key)
                            sms = africastalking.SMS
                            sms_response = sms.send(f"{verification} is your verification code for ZODO", [phone],"8707")
                            
                            partner_id.write({
                                'verification_code':verification
                            })
                            _logger.info("verification_code writed on res partner: %s",partner_id.verification_code)
                            return {
                                    "success": True,
                                    "result":{
                                        'verification_code':verification,
                                        'phone':search_user.phone,
                                        'userId':search_user.id
                                    },
                                    "message": "Verfication successfully Sent"
                                    }
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                             return {
                                    "success": False,
                                    "message": "Something went wrong"
                                    }
                    else:
                        
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                   
            except UserError as e:
                
                return {
                            "success": False,
                            "message": "Something went wrong"
                        }



    #App Side confirm password reset with verification
    
    @http.route('/register/api/confirm_reset_password', type='json', auth='public', website=False, sitemap=False)
    def web_auth_confirm_reset_password(self, *args, **kw):
        _logger.info("**************** Appside Confirm Reset password With Verfication Code ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
               
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('id','=',kw.get('user_id'))], limit=1)
                    _logger.info(search_user)
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    if kw.get('password') != kw.get("cpassword"):
                        qcontext['error'] = _("Password Not Match")

                    elif kw.get('password') == kw.get("cpassword"): # and search_user.phone == phone:
                        _logger.info("************ Correct password  match *************")
                        result = request.env['res.users'].sudo().confirm_reset_password(qcontext)
                        _logger.info("Finallly result: %s",result)
                        
                      
                        return {
                            "success": True,
                            "message": "Successfully Reset"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Something went wrong"
                        }
                    
            except:
                return {
                            "success": False,
                            "message": "Something went wrong"
                        }
           
    
    
    


        
    
    
   