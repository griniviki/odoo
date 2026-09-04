from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TripSheet(models.Model):
    _name = "trip.sheet"
    _description = "Vehicle Trip Sheet"
    _order = "month desc, id desc"

    month = fields.Char(string="Month", required=True, index=True)
    fuel_start = fields.Float(string="Starting Fuel", required=True, default=0.0)
    line_ids = fields.One2many("trip.sheet.line", "trip_sheet_id", string="Daily Records")
    user_id = fields.Many2one(
        "res.users",
        string="Created By",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )
    employee_id = fields.Many2one(
    "hr.employee",
    string="Employee",
    required=True,
    index=True,
    check_company=True,
    )

    # Monthly summary fields
    opening_odometer = fields.Float(string="Opening Odometer", compute="_compute_monthly_summary", store=True)
    closing_odometer = fields.Float(string="Closing Odometer", compute="_compute_monthly_summary", store=True)
    total_distance = fields.Float(string="Total Distance", compute="_compute_monthly_summary", store=True)
    total_fuel_used = fields.Float(string="Fuel Used", compute="_compute_monthly_summary", store=True)
    total_refill = fields.Float(string="Fuel Refilled", compute="_compute_monthly_summary", store=True)
    fuel_end = fields.Float(string="Fuel at End", compute="_compute_monthly_summary", store=True)

    @api.constrains("fuel_start")
    def _check_fuel_start(self):
        for record in self:
            if record.fuel_start < 0:
                raise ValidationError("Starting fuel cannot be negative.")

    @api.depends(
        "fuel_start",
        "line_ids.date_text",
        "line_ids.km_before",
        "line_ids.km_after",
        "line_ids.liters",
        "line_ids.refill",
        "line_ids.fuel_end_day",
    )
    def _compute_monthly_summary(self):
        for sheet in self:
            lines = sheet.line_ids.sorted(key=lambda l: l.date_text or "")
            if not lines:
                sheet.opening_odometer = 0
                sheet.closing_odometer = 0
                sheet.total_distance = 0
                sheet.total_fuel_used = 0
                sheet.total_refill = 0
                sheet.fuel_end = sheet.fuel_start
                continue

            first_line, last_line = lines[0], lines[-1]
            sheet.opening_odometer = first_line.km_before
            sheet.closing_odometer = last_line.km_after
            sheet.total_distance = sheet.closing_odometer - sheet.opening_odometer
            sheet.total_fuel_used = sum(lines.mapped("liters"))
            sheet.total_refill = sum(lines.mapped("refill"))
            sheet.fuel_end = last_line.fuel_end_day


class TripSheetLine(models.Model):
    _name = "trip.sheet.line"
    _description = "Vehicle Trip Sheet Daily Record"
    _order = "id"

    trip_sheet_id = fields.Many2one("trip.sheet", string="Trip Sheet", required=True,
                                    ondelete="cascade", index=True)
    date_text = fields.Char(string="Date", required=True)
    is_weekend = fields.Boolean(string="Weekend", default=False)
    km_before = fields.Float(string="Km Before")
    km_after = fields.Float(string="Km After")
    km_diff = fields.Float(string="Km Difference")
    liters = fields.Float(string="Fuel Used")
    refill = fields.Float(string="Refill")
    fuel_end_day = fields.Float(string="Fuel at End of Day")

    @api.constrains("km_before", "km_after", "km_diff", "liters", "refill", "fuel_end_day")
    def _check_values(self):
        for record in self:
            if record.km_before < 0 or record.km_after < 0:
                raise ValidationError("Mileage values cannot be negative.")
            if record.km_after < record.km_before:
                raise ValidationError("Km after cannot be less than km before.")
            if record.refill < 0:
                raise ValidationError("Refill cannot be negative.")
            if record.fuel_end_day < 0:
                raise ValidationError("Fuel at the end of the day cannot be negative.")
