from odoo import Command, _, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class TripSheetAccounting(models.Model):
    _inherit = "trip.sheet"

    _check_company_auto = True

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    accounting_date = fields.Date(
        string="Accounting Date",
        default=fields.Date.context_today,
        help="Date used for the generated journal entry.",
    )

    fuel_cost = fields.Monetary(
        string="Fuel Cost",
        currency_field="currency_id",
        help=(
            "Total monetary cost of fuel consumed during this Trip Sheet. "
            "This amount is debited to the expense account and credited "
            "to the fuel inventory account."
        ),
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="company_id.currency_id",
        readonly=True,
    )

    journal_entry_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        readonly=True,
        copy=False,
        check_company=True,
    )

    trip_sheet_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        related="company_id.trip_sheet_journal_id",
        readonly=True,
    )

    fuel_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Fuel Account",
        related="company_id.trip_fuel_account_id",
        readonly=True,
    )

    supplier_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Supplier Account",
        related="company_id.trip_supplier_account_id",
        readonly=True,
    )

    expense_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Expense Account",
        related="company_id.trip_expense_account_id",
        readonly=True,
    )

    def _check_accounting_configuration(self):
        for sheet in self:
            missing_items = []

            if not sheet.trip_sheet_journal_id:
                missing_items.append(_("Trip Sheet Journal"))

            if not sheet.fuel_account_id:
                missing_items.append(_("Fuel Account"))

            if not sheet.supplier_account_id:
                missing_items.append(_("Supplier Account"))

            if not sheet.expense_account_id:
                missing_items.append(_("Expense Account"))

            if missing_items:
                raise UserError(
                    _(
                        "Trip Sheet accounting is not configured for "
                        "company %(company)s.\n\n"
                        "Missing configuration:\n- %(items)s"
                    )
                    % {
                        "company": sheet.company_id.display_name,
                        "items": "\n- ".join(missing_items),
                    }
                )

    def _check_accounting_amount(self):
        for sheet in self:
            if not sheet.accounting_date:
                raise ValidationError(
                    _("Select an Accounting Date before generating the entry.")
                )

            comparison = float_compare(
                sheet.fuel_cost,
                0.0,
                precision_rounding=sheet.currency_id.rounding,
            )

            if comparison <= 0:
                raise ValidationError(
                    _("Fuel Cost must be greater than zero.")
                )

    def action_generate_journal_entry(self):
        self.ensure_one()

        if self.journal_entry_id:
            raise UserError(
                _(
                    "A journal entry has already been generated for "
                    "this Trip Sheet: %(entry)s"
                )
                % {
                    "entry": self.journal_entry_id.display_name,
                }
            )

        self._check_accounting_configuration()
        self._check_accounting_amount()

        company = self.company_id
        amount = self.currency_id.round(self.fuel_cost)

        move_values = {
            "move_type": "entry",
            "date": self.accounting_date,
            "journal_id": self.trip_sheet_journal_id.id,
            "company_id": company.id,
            "ref": _("Trip Sheet: %s") % self.display_name,
            "line_ids": [
                Command.create({
                    "name": _(
                        "Fuel expense from Trip Sheet %s"
                    ) % self.display_name,
                    "account_id": self.expense_account_id.id,
                    "debit": amount,
                    "credit": 0.0,
                }),
                Command.create({
                    "name": _(
                        "Fuel write-off from Trip Sheet %s"
                    ) % self.display_name,
                    "account_id": self.fuel_account_id.id,
                    "debit": 0.0,
                    "credit": amount,
                }),
            ],
        }

        move = (
            self.env["account.move"]
            .with_company(company)
            .create(move_values)
        )

        self.journal_entry_id = move.id

        return {
            "type": "ir.actions.act_window",
            "name": _("Journal Entry"),
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_journal_entry(self):
        self.ensure_one()

        if not self.journal_entry_id:
            raise UserError(
                _("No journal entry has been generated yet.")
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Journal Entry"),
            "res_model": "account.move",
            "res_id": self.journal_entry_id.id,
            "view_mode": "form",
            "target": "current",
        }