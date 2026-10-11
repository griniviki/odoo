from odoo import api, fields, models


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
        """Remove an incorrectly entered manual bank transaction.

        Native account.bank.statement.line.unlink() also handles the
        associated account.move according to Odoo's audit-trail rules.
        """
        self.unlink()
        return True
