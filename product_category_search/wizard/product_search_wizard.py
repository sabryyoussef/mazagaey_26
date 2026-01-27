# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductSearchWizard(models.TransientModel):
    _name = 'product.search.wizard'
    _description = 'Advanced Product Search Wizard'
    
    # Search Criteria
    name = fields.Char('Search Name', help="Name this search to save as preset")
    
    # Service Type & Department Filters
    service_type_ids = fields.Many2many(
        'product.service.type',
        string='Service Types',
        help="Filter by service types (Visa, Accounting, Banking, etc.)"
    )
    department_ids = fields.Many2many(
        'product.department',
        string='Departments',
        help="Filter by departments (Accounts, Operations, Sales)"
    )
    
    # Category Filter
    category_ids = fields.Many2many(
        'product.category',
        string='Product Categories',
        help="Filter by product categories"
    )
    
    # Price Range
    price_min = fields.Float('Minimum Price', default=0.0)
    price_max = fields.Float('Maximum Price', default=0.0)
    
    # Quick Service Filters
    is_visa_service = fields.Boolean('Visa Services Only')
    is_accounting_service = fields.Boolean('Accounting Services Only')
    is_banking_service = fields.Boolean('Banking Services Only')
    is_business_setup = fields.Boolean('Business Setup Only')
    is_value_added = fields.Boolean('Value Added Services Only')
    
    # Document & Compliance Filters
    has_documents = fields.Boolean('Has Document Requirements')
    compliance_level = fields.Selection([
        ('none', 'No Compliance'),
        ('low', 'Low Compliance'),
        ('medium', 'Medium Compliance'),
        ('high', 'High Compliance')
    ], string='Compliance Level')
    
    # Status Filters
    active_only = fields.Boolean('Active Products Only', default=True)
    can_be_sold = fields.Boolean('Can Be Sold', default=True)
    
    # Search Preset
    search_preset_id = fields.Many2one(
        'product.search.preset',
        string='Load Saved Search',
        help="Load criteria from a saved search preset"
    )
    save_as_preset = fields.Boolean('Save as Preset')
    preset_is_global = fields.Boolean('Make Global (All Users)')
    
    # Results
    result_count = fields.Integer('Results Found', compute='_compute_result_count', store=False)
    product_ids = fields.Many2many(
        'product.template',
        string='Search Results',
        compute='_compute_search_results',
        store=False
    )
    
    @api.depends('service_type_ids', 'department_ids', 'category_ids', 'price_min', 'price_max',
                 'is_visa_service', 'is_accounting_service', 'is_banking_service',
                 'is_business_setup', 'is_value_added', 'has_documents', 'compliance_level',
                 'active_only', 'can_be_sold')
    def _compute_search_results(self):
        """Compute search results based on criteria"""
        for wizard in self:
            domain = wizard._build_search_domain()
            wizard.product_ids = self.env['product.template'].search(domain)
    
    @api.depends('product_ids')
    def _compute_result_count(self):
        """Count search results"""
        for wizard in self:
            wizard.result_count = len(wizard.product_ids)
    
    @api.onchange('search_preset_id')
    def _onchange_search_preset(self):
        """Load criteria from selected preset"""
        if self.search_preset_id:
            preset = self.search_preset_id
            
            # Load saved domain and criteria
            if preset.filter_criteria:
                try:
                    import json
                    criteria = json.loads(preset.filter_criteria)
                    
                    # Apply criteria
                    if 'service_type_ids' in criteria:
                        self.service_type_ids = [(6, 0, criteria['service_type_ids'])]
                    if 'department_ids' in criteria:
                        self.department_ids = [(6, 0, criteria['department_ids'])]
                    if 'category_ids' in criteria:
                        self.category_ids = [(6, 0, criteria['category_ids'])]
                    if 'price_min' in criteria:
                        self.price_min = criteria['price_min']
                    if 'price_max' in criteria:
                        self.price_max = criteria['price_max']
                    if 'has_documents' in criteria:
                        self.has_documents = criteria['has_documents']
                    if 'compliance_level' in criteria:
                        self.compliance_level = criteria['compliance_level']
                        
                except Exception as e:
                    pass
    
    def _build_search_domain(self):
        """Build Odoo domain from search criteria"""
        self.ensure_one()
        domain = []
        
        # Service Type Filter
        if self.service_type_ids:
            domain.append(('service_type_id', 'in', self.service_type_ids.ids))
        
        # Department Filter
        if self.department_ids:
            domain.append(('product_department_id', 'in', self.department_ids.ids))
        
        # Category Filter
        if self.category_ids:
            domain.append(('categ_id', 'child_of', self.category_ids.ids))
        
        # Price Range
        if self.price_min > 0:
            domain.append(('list_price', '>=', self.price_min))
        if self.price_max > 0:
            domain.append(('list_price', '<=', self.price_max))
        
        # Quick Service Filters
        if self.is_visa_service:
            domain.append(('is_visa_service', '=', True))
        if self.is_accounting_service:
            domain.append(('is_accounting_service', '=', True))
        if self.is_banking_service:
            domain.append(('is_banking_service', '=', True))
        if self.is_business_setup:
            domain.append(('is_business_setup', '=', True))
        if self.is_value_added:
            domain.append(('is_value_added', '=', True))
        
        # Document & Compliance
        if self.has_documents:
            domain.append(('has_documents', '=', True))
        if self.compliance_level:
            domain.append(('compliance_level', '=', self.compliance_level))
        
        # Status Filters
        if self.active_only:
            domain.append(('active', '=', True))
        if self.can_be_sold:
            domain.append(('sale_ok', '=', True))
        
        return domain
    
    def action_search(self):
        """Execute search and show results"""
        self.ensure_one()
        
        # Save as preset if requested
        if self.save_as_preset:
            self._save_search_preset()
        
        # Build domain
        domain = self._build_search_domain()
        
        # Return action to show results
        return {
            'name': 'Search Results (%d found)' % self.result_count,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'context': {
                'search_default_service_type': True,
                'search_default_department': True,
            },
            'target': 'current',
        }
    
    def action_export_results(self):
        """Export search results to CSV"""
        self.ensure_one()
        
        if not self.product_ids:
            raise UserError('No products found. Please adjust your search criteria.')
        
        # Build export data
        export_data = []
        for product in self.product_ids:
            export_data.append({
                'name': product.name,
                'default_code': product.default_code or '',
                'service_type': product.service_type_id.name if product.service_type_id else '',
                'department': product.product_department_id.name if product.product_department_id else '',
                'category': product.categ_id.complete_name,
                'list_price': product.list_price,
                'active': product.active,
            })
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=product.search.wizard&id=%d&field=export_file' % self.id,
            'target': 'self',
        }
    
    def _save_search_preset(self):
        """Save current search criteria as preset"""
        self.ensure_one()
        
        if not self.name:
            raise UserError('Please provide a name to save this search preset.')
        
        # Build criteria dict
        import json
        criteria = {
            'service_type_ids': self.service_type_ids.ids,
            'department_ids': self.department_ids.ids,
            'category_ids': self.category_ids.ids,
            'price_min': self.price_min,
            'price_max': self.price_max,
            'is_visa_service': self.is_visa_service,
            'is_accounting_service': self.is_accounting_service,
            'is_banking_service': self.is_banking_service,
            'is_business_setup': self.is_business_setup,
            'is_value_added': self.is_value_added,
            'has_documents': self.has_documents,
            'compliance_level': self.compliance_level,
            'active_only': self.active_only,
            'can_be_sold': self.can_be_sold,
        }
        
        # Create preset
        domain = self._build_search_domain()
        preset_vals = {
            'name': self.name,
            'domain': str(domain),
            'filter_criteria': json.dumps(criteria),
            'result_count': self.result_count,
            'is_global': self.preset_is_global,
        }
        
        preset = self.env['product.search.preset'].create(preset_vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Search Saved',
                'message': 'Search preset "%s" saved successfully!' % preset.name,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_clear_filters(self):
        """Clear all search filters"""
        self.ensure_one()
        self.write({
            'service_type_ids': [(5, 0, 0)],
            'department_ids': [(5, 0, 0)],
            'category_ids': [(5, 0, 0)],
            'price_min': 0.0,
            'price_max': 0.0,
            'is_visa_service': False,
            'is_accounting_service': False,
            'is_banking_service': False,
            'is_business_setup': False,
            'is_value_added': False,
            'has_documents': False,
            'compliance_level': False,
            'active_only': True,
            'can_be_sold': True,
            'search_preset_id': False,
        })
        
        return {'type': 'ir.actions.do_nothing'}
