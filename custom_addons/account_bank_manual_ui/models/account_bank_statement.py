from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    balance_difference = fields.Monetary(
        string="Difference",
        compute="_compute_balance_difference",
        store=True,
        readonly=True,
        currency_field="currency_id",
    )

    @api.depends("balance_end", "balance_end_real")
    def _compute_balance_difference(self):
        for statement in self:
            statement.balance_difference = (
                statement.balance_end_real - statement.balance_end
            )
