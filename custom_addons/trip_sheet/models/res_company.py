from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    trip_sheet_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Trip Sheet Journal",
        check_company=True,
        domain="[('type', '=', 'general'), ('company_id', '=', id)]",
        help="General journal used to create Trip Sheet accounting entries.",
    )

    trip_fuel_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Trip Sheet Fuel Account",
        check_company=True,
        domain="[('account_type', '=', 'asset_current')]",
        help="Fuel inventory account. For Ukrainian PS(B)O: account 203.",
    )

    trip_supplier_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Trip Sheet Supplier Account",
        check_company=True,
        domain="[('account_type', '=', 'liability_payable')]",
        help="Supplier payable account. For Ukrainian PS(B)O: account 631.",
    )

    trip_expense_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Trip Sheet Expense Account",
        check_company=True,
        domain="[('account_type', '=', 'expense')]",
        help="Fuel expense account. For Ukrainian PS(B)O: account 93.",
    )
