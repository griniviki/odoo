from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request


class TripSheetController(http.Controller):

    @http.route(
        "/trip-sheet",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def trip_sheet_page(self, **kwargs):
        return request.render("trip_sheet.trip_sheet_template")

    @http.route(
        "/trip_sheet/save",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def save_trip_sheet(
        self,
        month=None,
        fuel_start=0,
        records=None,
    ):
        if not month:
            return {
                "success": False,
                "message": "Month is required.",
            }

        if not isinstance(records, list):
            return {
                "success": False,
                "message": "Daily records must be a list.",
            }

        try:
            fuel_start_value = float(fuel_start or 0)

            line_values = []

            for record in records:
                if not isinstance(record, dict):
                    continue

                line_values.append(
                    (
                        0,
                        0,
                        {
                            "date_text": str(
                                record.get("date", "")
                            ),
                            "is_weekend": bool(
                                record.get("isWeekend", False)
                            ),
                            "km_before": float(
                                record.get("kmBefore", 0) or 0
                            ),
                            "km_after": float(
                                record.get("kmAfter", 0) or 0
                            ),
                            "km_diff": float(
                                record.get("kmDiff", 0) or 0
                            ),
                            "liters": float(
                                record.get("liters", 0) or 0
                            ),
                            "refill": float(
                                record.get("refill", 0) or 0
                            ),
                            "fuel_end_day": float(
                                record.get("fuelEndDay", 0) or 0
                            ),
                        },
                    )
                )

            trip_sheet = request.env["trip.sheet"].create(
                {
                    "month": str(month).strip(),
                    "fuel_start": fuel_start_value,
                    "line_ids": line_values,
                }
            )

            return {
                "success": True,
                "id": trip_sheet.id,
                "message": "Trip sheet saved successfully.",
            }

        except (ValueError, TypeError) as error:
            return {
                "success": False,
                "message": f"Invalid numeric value: {error}",
            }

        except (AccessError, ValidationError) as error:
            return {
                "success": False,
                "message": str(error),
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"Unexpected server error: {error}",
            }