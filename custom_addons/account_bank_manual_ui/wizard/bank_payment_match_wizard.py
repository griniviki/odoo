from odoo import fields, models
from odoo.exceptions import UserError


class BankPaymentMatchWizard(models.TransientModel):
    _name = "bank.payment.match.wizard"
    _description = "Match Bank Transaction with Existing Payment"

    bank_transaction_id = fields.Many2one(
        "account.bank.statement.line",
        string="Bank Transaction",
        required=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        related="bank_transaction_id.partner_id",
        readonly=True,
    )

    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Journal",
        related="bank_transaction_id.journal_id",
        readonly=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="bank_transaction_id.company_id",
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="bank_transaction_id.currency_id",
        readonly=True,
    )

    expected_payment_amount = fields.Float(
        string="Expected Payment Amount",
        compute="_compute_expected_payment_amount",
        readonly=True,
    )

    def _compute_expected_payment_amount(self):
        for wizard in self:
            wizard.expected_payment_amount = -wizard.bank_transaction_id.amount

    payment_id = fields.Many2one(
        "account.payment",
        string="Existing Payment",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()

        if not self.bank_transaction_id:
            raise UserError("Please select a bank transaction.")

        if not self.payment_id:
            raise UserError("Please select a payment.")

        self.bank_transaction_id.action_match_existing_payment(
            self.payment_id
        )

        return {"type": "ir.actions.act_window_close"}
