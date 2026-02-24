# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_invoice_report(self):
        """Override to return custom POS invoice report"""
        self.ensure_one()
        if self.account_move:
            # Return custom POS invoice report
            custom_report = self.env.ref(
                'odoo_custom_invoice.action_custom_invoice_report_pos',
                raise_if_not_found=False
            )
            if custom_report:
                return custom_report
        return super(PosOrder, self)._get_invoice_report()

    def action_print_custom_invoice(self):
        """Print custom POS invoice for this order"""
        self.ensure_one()
        
        if not self.account_move:
            raise UserError('Invoice not found. Please validate the order first.')
        
        # Get custom POS invoice report
        custom_report = self.env.ref(
            'odoo_custom_invoice.action_custom_invoice_report_pos',
            raise_if_not_found=False
        )
        
        if not custom_report:
            raise UserError('Custom POS invoice report not found.')
        
        # Return report action
        return custom_report.report_action(self.account_move)

