{
    "name": "SAP Connector",
    "version": "19.0.1.0.0",
    "summary": "Synchronize SAP Business Partners with Odoo",
    "author": "viki",
    "license": "LGPL-3",
    "category": "Technical/Integration",

    "depends": [
        "base",
        "contacts",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/sap_connector_views.xml",
    ],

    "installable": True,
    "application": True,
}
