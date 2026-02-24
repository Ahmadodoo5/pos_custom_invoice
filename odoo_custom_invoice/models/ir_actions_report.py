# -*- coding: utf-8 -*-

from odoo import models, api


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_template(self, template, values=None):
        """Override to intercept account.report_invoice_document template for POS invoices"""
        # Check if this is account.report_invoice_document template
        if template == 'account.report_invoice_document':
            # Get docs from values or from context
            docs = []
            if values:
                docs = values.get('docs', [])
                # If docs not in values, try to get from res_ids in context
                if not docs and 'res_ids' in values:
                    res_ids = values.get('res_ids', [])
                    if res_ids:
                        docs = self.env['account.move'].browse(res_ids)
            
            if docs and self.model == 'account.move':
                # Handle both recordset and list of IDs
                invoice_ids = []
                for d in docs:
                    if hasattr(d, 'id'):
                        invoice_ids.append(d.id)
                    elif isinstance(d, int):
                        invoice_ids.append(d)
                
                if invoice_ids:
                    invoices = self.env['account.move'].browse(invoice_ids)
                    for invoice in invoices:
                        if 'point_of_sale' in self.env.registry:
                            from_pos = self.env['pos.order'].search_count([
                                ('account_move', '=', invoice.id)
                            ], limit=1) > 0
                            
                            if from_pos:
                                # Use custom POS invoice report template instead
                                return super(IrActionsReport, self)._render_template(
                                    'odoo_custom_invoice.custom_invoice_report_pos', 
                                    values
                                )
        
        return super(IrActionsReport, self)._render_template(template, values)
    
    def _render_qweb_html(self, res_ids=None, data=None):
        """Override to use custom POS invoice report when rendering HTML"""
        # Check if this is account.report_invoice_document for POS invoices
        if self.report_name == 'account.report_invoice_document' and res_ids:
            if self.model == 'account.move':
                invoices = self.env['account.move'].browse(res_ids)
                for invoice in invoices:
                    if 'point_of_sale' in self.env.registry:
                        from_pos = self.env['pos.order'].search_count([
                            ('account_move', '=', invoice.id)
                        ], limit=1) > 0
                        
                        if from_pos:
                            # Use custom POS invoice report instead
                            custom_report = self.env.ref(
                                'odoo_custom_invoice.action_custom_invoice_report_pos',
                                raise_if_not_found=False
                            )
                            if custom_report and custom_report.id != self.id:
                                return custom_report._render_qweb_html(res_ids, data)
        
        return super(IrActionsReport, self)._render_qweb_html(res_ids, data)

    def render_qweb_pdf(self, res_ids=None, data=None):
        """Override to use custom POS invoice report when printing from POS"""
        # Check if this is an invoice report
        if res_ids and self.model == 'account.move':
            invoices = self.env['account.move'].browse(res_ids)
            
            # Check if any invoice comes from POS
            if 'point_of_sale' in self.env.registry:
                for invoice in invoices:
                    from_pos = self.env['pos.order'].search_count([
                        ('account_move', '=', invoice.id)
                    ], limit=1) > 0
                    
                    if from_pos:
                        # Use custom POS invoice report instead of default
                        custom_report = self.env.ref(
                            'odoo_custom_invoice.action_custom_invoice_report_pos',
                            raise_if_not_found=False
                        )
                        if custom_report and custom_report.id != self.id:
                            # Use custom POS report
                            return custom_report.render_qweb_pdf(res_ids, data)
        
        return super(IrActionsReport, self).render_qweb_pdf(res_ids, data)
    
    @api.model
    def _get_report_from_name(self, report_name):
        """Override to use custom POS invoice report when printing from POS"""
        res = super(IrActionsReport, self)._get_report_from_name(report_name)
        
        # Check if this is a POS invoice report request
        if report_name == 'point_of_sale.report_invoice':
            # Check if invoice comes from POS from context
            active_model = self.env.context.get('active_model')
            active_ids = self.env.context.get('active_ids', [])
            
            if active_model == 'account.move' and active_ids:
                invoice = self.env['account.move'].browse(active_ids[0])
                # Check if invoice comes from POS
                if 'point_of_sale' in self.env.registry:
                    from_pos = self.env['pos.order'].search_count([
                        ('account_move', '=', invoice.id)
                    ], limit=1) > 0
                    
                    if from_pos:
                        # Return custom POS invoice report
                        custom_report = self.env.ref(
                            'odoo_custom_invoice.action_custom_invoice_report_pos',
                            raise_if_not_found=False
                        )
                        if custom_report:
                            return custom_report
        
        return res
    
    def get_report(self, res_ids, options=None):
        """Override to use custom POS invoice report when getting report from POS"""
        # Check if this is an invoice report
        if self.model == 'account.move' and res_ids:
            invoice = self.env['account.move'].browse(res_ids[0])
            
            # Check if invoice comes from POS
            if 'point_of_sale' in self.env.registry:
                from_pos = self.env['pos.order'].search_count([
                    ('account_move', '=', invoice.id)
                ], limit=1) > 0
                
                if from_pos:
                    # Use custom POS invoice report
                    custom_report = self.env.ref(
                        'odoo_custom_invoice.action_custom_invoice_report_pos',
                        raise_if_not_found=False
                    )
                    if custom_report and custom_report.id != self.id:
                        return custom_report.get_report(res_ids, options)
        
        return super(IrActionsReport, self).get_report(res_ids, options)

