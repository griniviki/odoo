import requests

from odoo import _, fields, models
from odoo.exceptions import UserError


class SapConnector(models.Model):
    _name = "sap.connector"
    _description = "SAP Connector"

    name = fields.Char(
        string="Name",
        required=True,
        default="SAP Business Partner Connector",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    base_url = fields.Char(
        string="SAP Base URL",
        required=True,
        default="http://sap-mock:8081",
    )

    last_sync_date = fields.Datetime(
        string="Last Sync",
        readonly=True,
    )

    last_sync_count = fields.Integer(
        string="Partners Synchronized",
        readonly=True,
    )

    def action_sync_business_partners(self):
        self.ensure_one()

        url = (
            self.base_url.rstrip("/")
            + "/odata/A_BusinessPartner"
        )

        try:
            response = requests.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise UserError(
                _("Could not connect to SAP: %s") % exc
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise UserError(
                _("SAP returned invalid JSON.")
            ) from exc

        business_partners = payload.get("value")

        if not isinstance(business_partners, list):
            raise UserError(
                _("SAP response does not contain a valid 'value' list.")
            )

        synchronized = 0

        for sap_partner in business_partners:
            sap_id = str(
                sap_partner.get("BusinessPartner") or ""
            ).strip()

            if not sap_id:
                continue

            first_name = str(
                sap_partner.get("FirstName") or ""
            ).strip()

            last_name = str(
                sap_partner.get("LastName") or ""
            ).strip()

            partner_name = " ".join(
                value
                for value in [first_name, last_name]
                if value
            )

            if not partner_name:
                partner_name = sap_id

            partner = self.env["res.partner"].search(
                [
                    (
                        "sap_business_partner_id",
                        "=",
                        sap_id,
                    )
                ],
                limit=1,
            )

            values = {
                "name": partner_name,
                "sap_business_partner_id": sap_id,
            }

            if partner:
                partner.write(values)
            else:
                self.env["res.partner"].create(values)

            synchronized += 1

        self.write({
            "last_sync_date": fields.Datetime.now(),
            "last_sync_count": synchronized,
        })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("SAP synchronization"),
                "message": _(
                    "%s Business Partner(s) synchronized."
                ) % synchronized,
                "type": "success",
                "sticky": False,
            },
        }
