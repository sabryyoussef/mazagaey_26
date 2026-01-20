# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    """Enhanced Product Template with Advanced Search and Categorization"""
    _inherit = 'product.template'
    
    # ============================================================================
    # SERVICE CLASSIFICATION
    # ============================================================================
    
    service_type_id = fields.Many2one(
        'product.service.type',
        string='Service Type',
        help='Classification of service type (Visa, Accounting, Banking, etc.)',
        index=True,
    )
    
    product_department_id = fields.Many2one(
        'product.department',
        string='Target Department',
        help='Primary department responsible for this product',
        index=True,
    )
    
    target_department = fields.Selection([
        ('accounts', 'Accounts Department'),
        ('operations', 'Operations Department'),
        ('sales', 'Sales Department'),
        ('all', 'All Departments'),
    ], string='Department', help='Target department for this service')
    
    # ============================================================================
    # DOCUMENT REQUIREMENTS (From unified_documents)
    # ============================================================================
    
    document_required_count = fields.Integer(
        string='Required Documents',
        compute='_compute_document_counts',
        store=True,
        help='Number of documents required from client',
    )
    
    document_deliverable_count = fields.Integer(
        string='Deliverable Documents',
        compute='_compute_document_counts',
        store=True,
        help='Number of documents to deliver to client',
    )
    
    has_compliance_docs = fields.Boolean(
        string='Requires Compliance Documents',
        compute='_compute_has_compliance',
        store=True,
    )
    
    # ============================================================================
    # PRICING & OPTIONS
    # ============================================================================
    
    has_multiyear_pricing = fields.Boolean(
        string='Multi-Year Options Available',
        help='This service has multi-year pricing options',
    )
    
    price_tier_ids = fields.One2many(
        'product.price.tier',
        'product_id',
        string='Price Tiers',
        help='Different pricing tiers (1-year, 3-year, 5-year, etc.)',
    )
    
    # ============================================================================
    # SEARCH & CATEGORIZATION
    # ============================================================================
    
    search_tags = fields.Char(
        string='Search Keywords',
        help='Comma-separated keywords for advanced search',
    )
    
    freezoner_reference = fields.Char(
        string='Freezoner Reference Code',
        help='Original reference code from Freezoner database',
        index=True,
    )
    
    # ============================================================================
    # QUICK FILTER FLAGS (Stored for Performance)
    # ============================================================================
    
    is_visa_service = fields.Boolean(
        string='Visa Service',
        compute='_compute_service_flags',
        store=True,
        index=True,
    )
    
    is_accounting_service = fields.Boolean(
        string='Accounting Service',
        compute='_compute_service_flags',
        store=True,
        index=True,
    )
    
    is_banking_service = fields.Boolean(
        string='Banking Service',
        compute='_compute_service_flags',
        store=True,
        index=True,
    )
    
    is_setup_service = fields.Boolean(
        string='Setup Service',
        compute='_compute_service_flags',
        store=True,
        index=True,
    )
    
    is_value_added_service = fields.Boolean(
        string='Value Added Service',
        compute='_compute_service_flags',
        store=True,
        index=True,
    )
    
    requires_high_compliance = fields.Boolean(
        string='High Compliance Required',
        compute='_compute_compliance_flag',
        store=True,
        index=True,
    )
    
    # ============================================================================
    # STATISTICS & USAGE
    # ============================================================================
    
    usage_count = fields.Integer(
        string='Times Sold',
        default=0,
        help='Number of times this product has been sold',
    )
    
    avg_project_duration = fields.Float(
        string='Avg Project Duration (days)',
        help='Average duration of projects using this product',
    )
    
    last_sold_date = fields.Date(
        string='Last Sold Date',
        help='Date when this product was last sold',
    )
    
    # ============================================================================
    # COMPUTED METHODS
    # ============================================================================
    
    def _compute_document_counts(self):
        """Compute document counts from unified_documents"""
        for product in self:
            if hasattr(product, 'document_required_type_ids'):
                product.document_required_count = len(product.document_required_type_ids)
            else:
                product.document_required_count = 0
            
            if hasattr(product, 'document_deliverable_type_ids'):
                product.document_deliverable_count = len(product.document_deliverable_type_ids)
            else:
                product.document_deliverable_count = 0
    
    def _compute_has_compliance(self):
        """Check if product requires compliance documents"""
        for product in self:
            if hasattr(product, 'document_required_type_ids'):
                # Check for common compliance documents
                compliance_keywords = ['passport', 'emirates_id', 'business_plan', 
                                     'bank_statement', 'source_of_funds', 'pep']
                doc_types = product.document_required_type_ids.mapped('name')
                product.has_compliance_docs = any(
                    keyword in doc_type.lower() 
                    for keyword in compliance_keywords 
                    for doc_type in doc_types
                )
            else:
                product.has_compliance_docs = False
    
    @api.depends('service_type_id', 'service_type_id.code', 'categ_id')
    def _compute_service_flags(self):
        """Compute service type flags for quick filtering"""
        for product in self:
            service_code = product.service_type_id.code if product.service_type_id else ''
            categ_name = product.categ_id.name.lower() if product.categ_id else ''
            product_name = product.name.lower() if product.name else ''
            
            # Visa services
            product.is_visa_service = (
                'VISA' in service_code or
                'visa' in categ_name or
                'visa' in product_name
            )
            
            # Accounting services
            product.is_accounting_service = (
                'ACCT' in service_code or
                'TAX' in service_code or
                'accounting' in categ_name or
                'tax' in categ_name or
                'audit' in product_name
            )
            
            # Banking services
            product.is_banking_service = (
                'BANK' in service_code or
                'banking' in categ_name or
                'bank' in product_name
            )
            
            # Setup services
            product.is_setup_service = (
                'SETUP' in service_code or
                'setup' in categ_name or
                'formation' in product_name or
                'incorporation' in product_name
            )
            
            # Value added services
            product.is_value_added_service = (
                'VALUE' in service_code or
                'value added' in categ_name
            )
    
    @api.depends('categ_id', 'categ_id.compliance_level', 'has_compliance_docs')
    def _compute_compliance_flag(self):
        """Compute if product requires high compliance"""
        for product in self:
            category_high = product.categ_id.compliance_level == 'high' if product.categ_id else False
            product.requires_high_compliance = category_high or product.has_compliance_docs
    
    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_documents(self):
        """Open documents for this product"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Documents'),
            'res_model': 'documents.document',
            'view_mode': 'kanban,tree,form',
            'domain': [
                ('res_model', '=', 'product.template'),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': 'product.template',
                'default_res_id': self.id,
            },
        }
    
    def action_create_quotation(self):
        """Quick action to create quotation"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Quotation'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_line': [(0, 0, {
                    'product_id': self.product_variant_id.id,
                    'product_uom_qty': 1,
                })],
            },
        }
    
    def action_advanced_search(self):
        """Open advanced search wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Advanced Product Search'),
            'res_model': 'product.search.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_service_type_id': self.service_type_id.id,
            },
        }
    
    # ============================================================================
    # SEARCH & FILTERING METHODS
    # ============================================================================
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enhanced search including freezoner reference and search tags"""
        args = args or []
        if name:
            domain = [
                '|', '|', '|',
                ('name', operator, name),
                ('default_code', operator, name),
                ('freezoner_reference', operator, name),
                ('search_tags', operator, name),
            ]
            return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name, args, operator, limit, name_get_uid)


class ProductPriceTier(models.Model):
    """Price Tiers for Multi-Year Pricing Options"""
    _name = 'product.price.tier'
    _description = 'Product Price Tier'
    _order = 'duration_years'
    
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    
    name = fields.Char(
        string='Tier Name',
        required=True,
        help='E.g., "1 Year", "3 Years", "5 Years"',
    )
    
    duration_years = fields.Integer(
        string='Duration (Years)',
        required=True,
        help='Contract duration in years',
    )
    
    price = fields.Monetary(
        string='Price',
        required=True,
        currency_field='currency_id',
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='product_id.currency_id',
        store=True,
    )
    
    savings_percent = fields.Float(
        string='Savings %',
        compute='_compute_savings',
        help='Percentage savings compared to 1-year price',
    )
    
    @api.depends('price', 'duration_years', 'product_id.list_price')
    def _compute_savings(self):
        """Compute savings percentage"""
        for tier in self:
            if tier.product_id.list_price and tier.duration_years > 1:
                annual_cost = tier.price / tier.duration_years
                base_annual = tier.product_id.list_price
                if base_annual:
                    tier.savings_percent = ((base_annual - annual_cost) / base_annual) * 100
                else:
                    tier.savings_percent = 0.0
            else:
                tier.savings_percent = 0.0
