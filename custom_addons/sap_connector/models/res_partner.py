from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sap_business_partner_id = fields.Char(
        string="SAP Business Partner ID",
        index=True,
        copy=False,
    )
