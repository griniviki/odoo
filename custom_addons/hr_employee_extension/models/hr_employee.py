from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    personal_number = fields.Char(
        string="Personal Number",
        index=True,
        copy=False,
    )

    first_name = fields.Char(
        string="First Name",
    )

    last_name = fields.Char(
        string="Last Name",
    )

    fuel_card_number = fields.Char(
        string="Fuel Card Number",
        index=True,
        copy=False,
    )

    @api.onchange("first_name", "last_name")
    def _onchange_first_last_name(self):
        for employee in self:
            parts = [
                employee.first_name,
                employee.last_name,
            ]

            full_name = " ".join(
                part.strip()
                for part in parts
                if part
            )

            if full_name:
                employee.name = full_name
