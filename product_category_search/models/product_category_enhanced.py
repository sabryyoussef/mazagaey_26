# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductCategory(models.Model):
    """Enhanced Product Category with Service Type Classification"""
    _inherit = 'product.category'
    
    # Service Type Classification
    service_type = fields.Selection([
        ('visa', 'Visa Services'),
        ('accounting', 'Accounting Services'),
        ('banking', 'Banking Services'),
        ('business_setup', 'Business Setup'),
        ('business_admin', 'Business Administration'),
        ('company_renewal', 'Company Renewal'),
        ('company_liquidation', 'Company Liquidation'),
        ('value_added', 'Value Added Services'),
        ('service_fees', 'Service Fees'),
        ('miscellaneous', 'Miscellaneous'),
    ], string='Service Type', help='Primary service type for this category')
    
    # Department Assignment
    department_ids = fields.Many2many(
        'product.department',
        'product_category_department_rel',
        'category_id',
        'department_id',
        string='Target Departments',
        help='Departments that use products in this category',
    )
    
    # Compliance Level
    compliance_level = fields.Selection([
        ('high', 'High Compliance'),
        ('medium', 'Medium Compliance'),
        ('low', 'Low Compliance'),
        ('none', 'No Compliance Required'),
    ], string='Compliance Level', default='none',
       help='Required compliance level for products in this category')
    
    # Visual Display
    category_icon = fields.Char(
        string='Icon Class',
        help='Font Awesome icon class',
        default='fa-folder',
    )
    category_color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color for Kanban view (0-11)',
    )
    
    # Statistics
    avg_price = fields.Monetary(
        string='Average Product Price',
        compute='_compute_category_statistics',
        currency_field='currency_id',
    )
    total_value = fields.Monetary(
        string='Total Category Value',
        compute='_compute_category_statistics',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    
    # Document Requirements
    requires_documents = fields.Boolean(
        string='Requires Documents',
        compute='_compute_document_flags',
        store=True,
    )
    avg_required_docs = fields.Float(
        string='Avg Required Documents',
        compute='_compute_document_stats',
    )
    avg_deliverable_docs = fields.Float(
        string='Avg Deliverable Documents',
        compute='_compute_document_stats',
    )
    
    @api.depends('product_count')
    def _compute_category_statistics(self):
        """Compute category pricing statistics"""
        for category in self:
            products = self.env['product.template'].search([
                ('categ_id', '=', category.id)
            ])
            if products:
                prices = products.mapped('list_price')
                category.avg_price = sum(prices) / len(prices) if prices else 0.0
                category.total_value = sum(prices)
            else:
                category.avg_price = 0.0
                category.total_value = 0.0
    
    @api.depends('product_count')
    def _compute_document_flags(self):
        """Check if category products require documents"""
        for category in self:
            # Check if unified_documents fields exist
            ProductTemplate = self.env['product.template']
            if not (hasattr(ProductTemplate, 'document_required_type_ids') or 
                    hasattr(ProductTemplate, 'document_deliverable_type_ids')):
                category.requires_documents = False
                continue
            
            products = ProductTemplate.search([
                ('categ_id', '=', category.id),
                '|',
                ('document_required_type_ids', '!=', False),
                ('document_deliverable_type_ids', '!=', False),
            ], limit=1)
            category.requires_documents = bool(products)
    
    @api.depends('product_count')
    def _compute_document_stats(self):
        """Compute average document counts"""
        for category in self:
            # Check if unified_documents is installed
            ProductTemplate = self.env['product.template']
            if not (hasattr(ProductTemplate, 'document_required_type_ids') or 
                    hasattr(ProductTemplate, 'document_deliverable_type_ids')):
                category.avg_required_docs = 0.0
                category.avg_deliverable_docs = 0.0
                continue
            
            products = ProductTemplate.search([
                ('categ_id', '=', category.id)
            ])
            if products:
                # Get document counts from unified_documents if available
                required_counts = []
                deliverable_counts = []
                for product in products:
                    if hasattr(product, 'document_required_type_ids'):
                        required_counts.append(len(product.document_required_type_ids))
                    if hasattr(product, 'document_deliverable_type_ids'):
                        deliverable_counts.append(len(product.document_deliverable_type_ids))
                
                category.avg_required_docs = sum(required_counts) / len(required_counts) if required_counts else 0.0
                category.avg_deliverable_docs = sum(deliverable_counts) / len(deliverable_counts) if deliverable_counts else 0.0
            else:
                category.avg_required_docs = 0.0
                category.avg_deliverable_docs = 0.0
