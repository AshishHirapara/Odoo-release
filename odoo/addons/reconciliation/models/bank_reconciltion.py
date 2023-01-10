from odoo import api, fields, models, _


class BankStatement(models.Model):
    _name = 'bank.reconciliation'


    @api.onchange('time_frame', 'account_id')
    def _get_lines_2(self):
      if self.time_frame:
        self.sudo().write({"date_to":self.time_frame.date_to})
        self.sudo().write({"date_from":self.time_frame.date_from})
        # self.account_id = self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
        self.currency_id = self.journal_id.currency_id or self.journal_id.company_id.currency_id or \
                           self.env.user.company_id.currency_id
        domain = [('account_id', '=', self.account_id.id), ('statement_date', '=', False),('is_done', '=', False)]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
        lines = self.env['account.move.line'].search(domain)
        lines_3 = self.env['account.move.line'].search([('account_id', '=', self.account_id.id),('date', '<=', self.date_from)])
        credit = 0.0
        debit = 0.0
        for line in self.statement_lines:
                 line.bank_statement_id = self.id
        self.statement_lines = lines
        for tran in lines_3:
            credit = credit + abs(tran.credit)
            debit = debit + abs(tran.debit)
        print('gl', credit, debit)
        self.gl_balance = debit - credit
      self._is_reconciled()

    @api.onchange('statement_lines', 'statement_ending_line')
    def _is_reconciled(self):
        self.balance_difference = 0.0
        self.bank_balance = 0.0
        credit_2 = 0.0
        debit_2 = 0.0
        for cr_and_db in self.statement_lines:
            print("cr_and_db.is_reconciled", cr_and_db.is_reconciled)
            if not cr_and_db.is_reconciled:
                credit_2 = credit_2 + abs(cr_and_db.credit)
                debit_2 = debit_2 + abs(cr_and_db.debit)
        self.balance_difference = debit_2 - credit_2
        print("self.statement_ending_line", self.statement_ending_line)
        print("self.statement_ending_line", self.statement_ending_line)
        print("")
        self.bank_balance = self.statement_ending_line - (self.gl_balance + self.balance_difference)




    journal_id = fields.Many2one('account.journal', 'Bank', domain=[('type', '=', 'bank')])
    account_id = fields.Many2one('account.account', 'Bank Account')
    time_frame = fields.Many2one('reconciliation.time.fream', 'Time frame')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    statement_lines = fields.One2many('account.move.line', 'bank_statement_id')
    gl_balance = fields.Float('Balance as per Company Books', readonly=True)
    bank_balance = fields.Float('Unreconciled Difference', readonly=True, store=True)
    balance_difference = fields.Float('Amounts not Reflected in Bank', readonly=True, store=True)
    current_update = fields.Monetary('Balance of entries updated now')
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('bank.statement'))
    statement_ending_line = fields.Float(string='Balance as per Bank', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], default='draft', string="Status")

    def set_done(self):
        print("done")
        if self.time_frame:
            self.state = 'done'
            for line in self.statement_lines:
                if line.is_reconciled:
                    line.is_done = True
                    line.reconciled = True
                    line.time_frame = self.time_frame.name

    def set_draft(self):
        self.state = 'draft'
        for line in self.statement_lines:
            line.is_done = False
            line.reconciled = False
            line.time_frame = ' '