# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    previous_credit = fields.Monetary(
        string='Previous Credit',
        compute='_compute_previous_credit',
        store=False,
        currency_field='company_currency_id',
        help='Total Customer Account payments across all POS orders for this customer'
    )

    previous_credit_invoice_ids = fields.Many2many(
        'account.move',
        'account_move_previous_credit_rel',
        'move_id',
        'previous_move_id',
        string='Previous Invoices with Due Amount',
        compute='_compute_previous_credit',
        store=False
    )

    # ----------------------------------------------------------
    # Helper: check if a payment method is "Customer Account"
    # ----------------------------------------------------------
    @staticmethod
    def _is_customer_account_pm(pm):
        """Return True if payment method is Customer Account type."""
        if not pm:
            return False
        name = (pm.name or '').lower()
        return (
                'customer' in name or
                'account' in name or
                'credit' in name
        )

    # ----------------------------------------------------------
    # Compute Previous Credit
    # Previous Credit = Total Customer Account payments from ALL POS orders
    #                   for this customer (including current order)
    # ----------------------------------------------------------
    @api.depends('partner_id', 'move_type', 'state')
    def _compute_previous_credit(self):
        for move in self:
            previous_credit = 0.0
            previous_invoices = self.env['account.move']

            if move.partner_id and move.move_type in ('out_invoice', 'out_refund'):

                # ── POS Invoice: sum Customer Account payments from ALL pos orders ──
                if 'point_of_sale' in self.env.registry:
                    pos_order = self.env['pos.order'].search([
                        ('account_move', '=', move.id)
                    ], limit=1)

                    if pos_order:
                        # Find ALL POS orders for this partner (all statuses that are confirmed)
                        all_pos_orders = self.env['pos.order'].search([
                            ('partner_id', '=', move.partner_id.id),
                            ('state', 'in', ['paid', 'done', 'invoiced']),
                        ])

                        # Sum Customer Account payments from all orders
                        total_ca = 0.0
                        for order in all_pos_orders:
                            for payment in order.payment_ids:
                                if self._is_customer_account_pm(payment.payment_method_id):
                                    total_ca += payment.amount

                        move.previous_credit = total_ca
                        move.previous_credit_invoice_ids = previous_invoices
                        continue

                # ── Regular Accounting Invoice (non-POS): sum unpaid invoice residuals ──
                domain = [
                    ('partner_id', '=', move.partner_id.id),
                    ('move_type', 'in', ('out_invoice', 'out_refund')),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('id', '!=', move.id),
                ]
                previous_invoices = self.env['account.move'].search(domain)
                previous_credit = sum(previous_invoices.mapped('amount_residual'))

            move.previous_credit = previous_credit
            move.previous_credit_invoice_ids = previous_invoices

    # ----------------------------------------------------------
    # POS Previous Credit RPC
    # Called from JS BEFORE current order is validated.
    # Returns: sum of Customer Account payments from all PREVIOUSLY
    #          confirmed POS orders (current order not saved yet).
    # JS will then ADD the current order's Customer Account amount on top.
    # ----------------------------------------------------------
    @api.model
    def pos_get_previous_credit(self, partner_id, company_id=None, current_order_ref=None):
        """
        Return total Customer Account payments from ALL confirmed POS orders
        for this customer, EXCLUDING the current (not-yet-saved) order.

        JS will add the current order's Customer Account amount separately.

        Formula:
          previous_credit (JS) = backend_result + current_order_CA_amount
          previous_credit (PDF) = sum of ALL pos orders' CA payments (incl. current)
        """
        if not partner_id:
            return 0.0

        # Search all confirmed POS orders for this customer
        domain = [
            ('partner_id', '=', int(partner_id)),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if company_id:
            domain.append(('company_id', '=', int(company_id)))

        pos_orders = self.env['pos.order'].search(domain)

        # Exclude current order (it's not saved yet but filter by ref just in case)
        if current_order_ref:
            pos_orders = pos_orders.filtered(
                lambda o: (o.pos_reference or '') != current_order_ref
                          and (o.name or '') != current_order_ref
            )

        # Sum Customer Account payments
        total_ca = 0.0
        for order in pos_orders:
            for payment in order.payment_ids:
                if self._is_customer_account_pm(payment.payment_method_id):
                    total_ca += payment.amount

        return float(total_ca)

    # ----------------------------------------------------------
    # Download Invoice PDF Button
    # ----------------------------------------------------------
    def action_download_invoice_pdf(self):
        """Download invoice as PDF"""
        self.ensure_one()

        from_pos = False
        if 'point_of_sale' in self.env.registry:
            from_pos = self.env['pos.order'].search_count([
                ('account_move', '=', self.id)
            ], limit=1) > 0

        if from_pos:
            report_ref = 'odoo_custom_invoice.action_custom_invoice_report_pos'
        else:
            report_ref = 'odoo_custom_invoice.action_custom_invoice_report_accounting'

        report = self.env.ref(report_ref, raise_if_not_found=False)
        if not report:
            raise UserError(_('Report not found: %s') % report_ref)

        return report.report_action(self)
