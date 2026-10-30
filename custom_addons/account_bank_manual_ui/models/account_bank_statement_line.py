from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    manual_counterpart_account_id = fields.Many2one(
        "account.account",
        string="Counterpart Account",
        check_company=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            account_id = vals.get("manual_counterpart_account_id")

            if account_id:
                vals["counterpart_account_id"] = account_id

        lines = super().create(vals_list)

        statements = lines.statement_id
        statements._compute_date()
        statements._compute_name()
        statements._compute_balance_start()

        return lines

    def action_remove_manual_transaction(self):
        self.unlink()
        return True

    def action_match_existing_payment(self, payment):
        self.ensure_one()
        payment.ensure_one()

        if self.company_id != payment.company_id:
            raise UserError("The payment and bank transaction must belong to the same company.")

        if self.currency_id != payment.currency_id:
            raise UserError("The payment and bank transaction must use the same currency.")

        if self.partner_id != payment.partner_id:
            raise UserError("The payment and bank transaction must have the same partner.")

        if self.journal_id != payment.journal_id:
            raise UserError("The payment and bank transaction must use the same journal.")

        if self.amount != -payment.amount:
            raise UserError("The bank transaction amount must be opposite to the payment amount.")


        payment_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
        liquidity_lines, suspense_lines, other_lines = self._seek_for_lines()

        if len(payment_lines) != 1 or len(suspense_lines) != 1:
            raise UserError("Expected one payment line and one bank suspense line.")

        if suspense_lines.account_id != self.journal_id.suspense_account_id:
            raise UserError("The bank transaction must use the suspense account.")

        if payment.move_id.state != "posted" or self.move_id.state != "posted":
            raise UserError("Both accounting entries must be posted.")


        payment_line = payment_lines[0]
        bank_line = suspense_lines[0]

        if payment.payment_type != "outbound":
            raise UserError("Only outgoing payments are supported.")

        if payment.state != "in_process":
            raise UserError("The payment must be in process.")

        if payment.is_matched:
            raise UserError("This payment is already matched.")

        if len(counterpart_lines) != 1 or writeoff_lines:
            raise UserError("The payment has an unexpected accounting structure.")

        if len(liquidity_lines) != 1 or other_lines:
            raise UserError("The bank transaction is already processed or has unexpected lines.")

        if not payment.outstanding_account_id.reconcile:
            raise UserError("The outstanding account must allow reconciliation.")

        if payment_line.account_id != payment.outstanding_account_id:
            raise UserError("The payment uses an unexpected outstanding account.")

        if payment_line.reconciled or bank_line.reconciled:
            raise UserError("One of the accounting lines is already reconciled.")

        if payment_line.balance + bank_line.balance != 0:
            raise UserError("The accounting line balances do not match.")

        bank_line.with_context(skip_readonly_check=True).write({
            "account_id": payment.outstanding_account_id.id,
        })
        (payment_line | bank_line).reconcile()
    def action_open_payment_match_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Match Existing Payment",
            "res_model": "bank.payment.match.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_bank_transaction_id": self.id,
            },
        }
