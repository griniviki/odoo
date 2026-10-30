{
    "name": "Manual Bank Statements",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Manual bank statement and transaction management",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_bank_statement_views.xml",
        "views/bank_payment_match_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
