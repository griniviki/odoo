{
    "name": "Trip Sheet",
    "version": "19.0.1.0.0",
    "author": "viki",
    "license": "LGPL-3",

    "depends": [
        "base",
        "web",
        "website",
        "hr",
        "fleet",
        "account",
        "hr_employee_extension",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/trip_sheet_views.xml",
        "views/trip_sheet_menus.xml",
        "views/trip_sheet_template.xml",
        "views/trip_sheet_accounting_views.xml",
        "views/res_company_views.xml",
    ],

    "assets": {
        "web.assets_frontend": [
            "trip_sheet/static/src/css/trip_sheet.css",
            "trip_sheet/static/src/js/trip_sheet_form.js",
        ],
    },

    "installable": True,
    "application": True,
}
