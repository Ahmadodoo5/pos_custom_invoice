# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InvoiceReportSettings(models.Model):
    _name = 'invoice.report.settings'
    _description = 'Invoice Report Settings'
    _rec_name = 'company_id'

    # Company Header Settings
    company_name_font_size = fields.Integer(
        string='Company Name Font Size (px)',
        default=16,
        help='Font size for company name label in header'
    )
    company_name_bold = fields.Boolean(
        string='Company Name Bold',
        default=False,
        help='Bold setting for company name label in header'
    )
    company_name_value_font_size = fields.Integer(
        string='Company Name Value Font Size (px)',
        default=16,
        help='Font size for company name value in header'
    )
    company_name_value_bold = fields.Boolean(
        string='Company Name Value Bold',
        default=False,
        help='Bold setting for company name value in header'
    )

    company_address_font_size = fields.Integer(
        string='Company Address Font Size (px)',
        default=12,
        help='Font size for company address label in header'
    )
    company_address_bold = fields.Boolean(
        string='Company Address Bold',
        default=False,
        help='Bold setting for company address label in header'
    )
    company_address_value_font_size = fields.Integer(
        string='Company Address Value Font Size (px)',
        default=12,
        help='Font size for company address value in header'
    )
    company_address_value_bold = fields.Boolean(
        string='Company Address Value Bold',
        default=False,
        help='Bold setting for company address value in header'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Logo Settings
    custom_logo = fields.Binary(
        string='Custom Logo',
        help='Custom logo to display above customer name in invoice reports'
    )
    logo_alignment = fields.Selection([
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ], string='Logo Alignment', default='left', required=True)
    logo_width = fields.Integer(
        string='Logo Width (px)',
        default=200,
        help='Width of the logo in pixels'
    )
    logo_height = fields.Integer(
        string='Logo Height (px)',
        default=80,
        help='Height of the logo in pixels'
    )

    # Font Sizes
    invoice_number_font_size = fields.Integer(
        string='Invoice Number Font Size (px)',
        default=24,
        help='Font size for invoice number'
    )
    customer_name_font_size = fields.Integer(
        string='Customer Name Font Size (px)',
        default=16,
        help='Font size for customer name'
    )
    invoice_date_font_size = fields.Integer(
        string='Invoice Date Heading Font Size (px)',
        default=12,
        help='Font size for invoice date heading'
    )
    invoice_date_value_font_size = fields.Integer(
        string='Invoice Date Value Font Size (px)',
        default=12,
        help='Font size for invoice date value'
    )
    due_date_font_size = fields.Integer(
        string='Due Date Heading Font Size (px)',
        default=12,
        help='Font size for due date heading'
    )
    due_date_value_font_size = fields.Integer(
        string='Due Date Value Font Size (px)',
        default=12,
        help='Font size for due date value'
    )
    customer_name_value_font_size = fields.Integer(
        string='Customer Name Value Font Size (px)',
        default=16,
        help='Font size for customer name value'
    )
    source_font_size = fields.Integer(
        string='Source Heading Font Size (px)',
        default=12,
        help='Font size for source field heading'
    )
    source_value_font_size = fields.Integer(
        string='Source Value Font Size (px)',
        default=12,
        help='Font size for source field value (Order Ref)'
    )
    reference_font_size = fields.Integer(
        string='Reference Font Size (px)',
        default=12,
        help='Font size for reference field'
    )

    # Bold Settings
    invoice_number_bold = fields.Boolean(
        string='Invoice Number Bold',
        default=True
    )
    customer_name_bold = fields.Boolean(
        string='Customer Name Bold',
        default=False
    )
    invoice_date_bold = fields.Boolean(
        string='Invoice Date Heading Bold',
        default=False
    )
    invoice_date_value_bold = fields.Boolean(
        string='Invoice Date Value Bold',
        default=False
    )
    due_date_bold = fields.Boolean(
        string='Due Date Heading Bold',
        default=False
    )
    due_date_value_bold = fields.Boolean(
        string='Due Date Value Bold',
        default=False
    )
    customer_name_value_bold = fields.Boolean(
        string='Customer Name Value Bold',
        default=False
    )
    source_bold = fields.Boolean(
        string='Source Heading Bold',
        default=False
    )
    source_value_bold = fields.Boolean(
        string='Source Value Bold',
        default=False,
        help='Bold setting for source field value (Order Ref)'
    )
    reference_bold = fields.Boolean(
        string='Reference Bold',
        default=False
    )

    # Table Settings
    table_description_font_size = fields.Integer(
        string='Description Font Size (px)',
        default=12
    )
    table_quantity_font_size = fields.Integer(
        string='Quantity Font Size (px)',
        default=12
    )
    table_price_font_size = fields.Integer(
        string='Price Font Size (px)',
        default=12
    )
    table_taxes_font_size = fields.Integer(
        string='Taxes Font Size (px)',
        default=12
    )
    table_amount_font_size = fields.Integer(
        string='Amount Font Size (px)',
        default=12
    )

    # Table Value Bold Settings
    table_description_bold = fields.Boolean(
        string='Description Value Bold',
        default=False
    )
    table_quantity_bold = fields.Boolean(
        string='Quantity Value Bold',
        default=False
    )
    table_price_bold = fields.Boolean(
        string='Price Value Bold',
        default=False
    )
    table_taxes_bold = fields.Boolean(
        string='Taxes Value Bold',
        default=False
    )
    table_amount_bold = fields.Boolean(
        string='Amount Value Bold',
        default=False
    )

    # Previous Credit Settings
    previous_credit_heading_font_size = fields.Integer(
        string='Previous Credit Heading Font Size (px)',
        default=12,
        help='Font size for "Previous Credit" heading'
    )
    previous_credit_value_font_size = fields.Integer(
        string='Previous Credit Value Font Size (px)',
        default=12,
        help='Font size for previous credit amount value'
    )
    previous_credit_heading_bold = fields.Boolean(
        string='Previous Credit Heading Bold',
        default=False
    )
    previous_credit_value_bold = fields.Boolean(
        string='Previous Credit Value Bold',
        default=False
    )
    previous_invoices_heading_font_size = fields.Integer(
        string='Previous Invoices Heading Font Size (px)',
        default=12,
        help='Font size for "Previous Invoices with Due Amount" heading'
    )
    previous_invoices_value_font_size = fields.Integer(
        string='Previous Invoices Value Font Size (px)',
        default=12,
        help='Font size for previous invoices list value'
    )
    previous_invoices_heading_bold = fields.Boolean(
        string='Previous Invoices Heading Bold',
        default=False
    )
    previous_invoices_value_bold = fields.Boolean(
        string='Previous Invoices Value Bold',
        default=False
    )

    # Total and Amount Due Settings
    total_heading_font_size = fields.Integer(
        string='Total Heading Font Size (px)',
        default=12,
        help='Font size for "Total" heading'
    )
    total_value_font_size = fields.Integer(
        string='Total Value Font Size (px)',
        default=12,
        help='Font size for total amount value'
    )
    total_heading_bold = fields.Boolean(
        string='Total Heading Bold',
        default=False
    )
    total_value_bold = fields.Boolean(
        string='Total Value Bold',
        default=True,
        help='Bold setting for total amount value'
    )
    amount_due_heading_font_size = fields.Integer(
        string='Amount Due Heading Font Size (px)',
        default=12,
        help='Font size for "Amount Due" heading'
    )
    amount_due_value_font_size = fields.Integer(
        string='Amount Due Value Font Size (px)',
        default=12,
        help='Font size for amount due value'
    )
    amount_due_heading_bold = fields.Boolean(
        string='Amount Due Heading Bold',
        default=True,
        help='Bold setting for "Amount Due" heading'
    )
    amount_due_value_bold = fields.Boolean(
        string='Amount Due Value Bold',
        default=True,
        help='Bold setting for amount due value'
    )

    # Report Type
    report_type = fields.Selection([
        ('accounting', 'Accounting Invoice'),
        ('pos', 'POS Invoice'),
    ], string='Report Type', default='accounting', required=True)

    # Paper Size
    paper_size = fields.Selection([
        ('a4', 'A4 (210 x 297 mm)'),
        ('a5', 'A5 (148 x 210 mm)'),
        ('legal', 'Legal (8.5 x 14 inches)'),
        ('letter', 'Letter (8.5 x 11 inches)'),
    ], string='Paper Size', default='a4', required=True, help='Paper size for invoice reports')

    @api.model
    def get_settings(self, report_type='accounting'):
        """Get settings for current company and report type"""
        company = self.env.company
        settings = self.search([
            ('company_id', '=', company.id),
            ('report_type', '=', report_type)
        ], limit=1)

        if not settings:
            # Create default settings
            settings = self.create({
                'company_id': company.id,
                'report_type': report_type,
            })

        return settings
