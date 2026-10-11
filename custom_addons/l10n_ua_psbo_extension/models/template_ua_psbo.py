from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ua_psbo", "account.journal")
    def _get_ua_psbo_trip_sheet_journal(self):
        return {
            "ua_psbo_trip_sheet_journal": {
                "name": "Trip Sheet Journal",
                "code": "TSJ",
                "type": "general",
            },
        }

    @template("ua_psbo", "res.company")
    def _get_ua_psbo_trip_sheet_company(self):
        return {
            self.env.company.id: {
                "trip_sheet_journal_id": "ua_psbo_trip_sheet_journal",
                "trip_fuel_account_id": "ua_psbp_203",
                "trip_supplier_account_id": "ua_psbp_631",
                "trip_expense_account_id": "ua_psbp_93",
            },
        }
