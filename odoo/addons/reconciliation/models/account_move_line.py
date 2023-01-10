# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    def post(self):
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('is_active', '=', True)])
        active = 0
        for line in active_time_frame:
          if self.date:
            if line.date_from <= self.date and line.date_to >= self.date:
                active = active + 1
        if active == 0:
          if self.date:
            raise AccessError(_("You Posting date out of the current time frame."))
        return super(AccountMove, self).post()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_statement_id = fields.Many2one('bank.reconciliation', 'Bank Statement', copy=False)
    statement_date = fields.Date('Bank.St Date', copy=False)
    reconciled = fields.Boolean('Is reconciled')
    is_reconciled = fields.Boolean('Is reconciled')
    is_done = fields.Boolean('Is done')
    time_frame = fields.Char('Time frame')

    # def write(self, vals):
    #     if not vals.get("statement_date"):
    #         vals.update({"reconciled": False})
    #         for record in self:
    #             if record.payment_id and record.payment_id.state == 'reconciled':
    #                 record.payment_id.state = 'posted'
    #     elif vals.get("statement_date"):
    #         vals.update({"reconciled": True})
    #         for record in self:
    #             if record.payment_id:
    #                 record.payment_id.state = 'reconciled'
    #     res = super(AccountMoveLine, self).write(vals)
    #     return res
