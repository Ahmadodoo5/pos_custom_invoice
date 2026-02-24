# -*- coding: utf-8 -*-

from . import models


from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    """Remove all POS Invoice A5 reports (since we renamed it to A5 Report)"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find and delete ALL reports with name "POS Invoice A5" and model "account.move"
    # Since we renamed our report to "A5 Report", any "POS Invoice A5" is now unwanted
    try:
        duplicate_reports = env['ir.actions.report'].search([
            ('name', '=', 'POS Invoice A5'),
            ('model', '=', 'account.move')
        ])
        if duplicate_reports:
            duplicate_reports.unlink()
    except Exception:
        # If error occurs, skip cleanup
        pass

