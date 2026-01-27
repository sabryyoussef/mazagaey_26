# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductBulkCategorize(models.TransientModel):
    """
    Bulk Categorization Wizard
    
    Apply service types and departments to multiple products at once,
    with auto-detection based on product name patterns.
    """
    _name = 'product.bulk.categorize'
    _description = 'Product Bulk Categorize'
    
    name = fields.Char(
        string='Operation Name',
        default=lambda self: _('Bulk Categorize - %s') % fields.Date.today(),
    )
    
    # === Selection Mode ===
    selection_mode = fields.Selection([
        ('selected', 'Selected Products'),
        ('all_uncategorized', 'All Uncategorized Products'),
        ('by_filter', 'Products Matching Filter'),
    ], default='selected', string='Apply To', required=True)
    
    # === Products ===
    product_ids = fields.Many2many(
        'product.template',
        string='Products to Categorize',
    )
    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
    )
    
    # === Filter Options ===
    filter_name = fields.Char(
        string='Name Contains',
        help='Filter products by name (case insensitive)',
    )
    filter_category_id = fields.Many2one(
        'product.category',
        string='In Category',
    )
    
    # === Categorization Options ===
    action_type = fields.Selection([
        ('auto', 'Auto-Detect from Name'),
        ('manual', 'Set Specific Values'),
        ('clear', 'Clear Categorization'),
    ], default='auto', string='Action', required=True)
    
    # Manual values
    service_type_id = fields.Many2one(
        'product.service.type',
        string='Service Type',
    )
    department_id = fields.Many2one(
        'product.department',
        string='Department',
    )
    
    # === What to Update ===
    update_service_type = fields.Boolean(
        string='Update Service Type',
        default=True,
    )
    update_department = fields.Boolean(
        string='Update Department',
        default=True,
    )
    overwrite_existing = fields.Boolean(
        string='Overwrite Existing Values',
        default=False,
        help='If unchecked, only update products that have no value set',
    )
    
    # === Results ===
    result_log = fields.Text(
        string='Result Log',
        readonly=True,
    )
    processed_count = fields.Integer(
        string='Processed',
        readonly=True,
    )
    updated_count = fields.Integer(
        string='Updated',
        readonly=True,
    )
    skipped_count = fields.Integer(
        string='Skipped',
        readonly=True,
    )
    state = fields.Selection([
        ('config', 'Configure'),
        ('done', 'Done'),
    ], default='config', string='State')
    
    @api.depends('selection_mode', 'product_ids', 'filter_name', 'filter_category_id')
    def _compute_product_count(self):
        for wizard in self:
            if wizard.selection_mode == 'selected':
                wizard.product_count = len(wizard.product_ids)
            elif wizard.selection_mode == 'all_uncategorized':
                wizard.product_count = self.env['product.template'].search_count([
                    '|',
                    ('service_type_id', '=', False),
                    ('product_department_id', '=', False),
                ])
            else:
                domain = wizard._build_filter_domain()
                wizard.product_count = self.env['product.template'].search_count(domain)
    
    def _build_filter_domain(self):
        """Build domain based on filter options"""
        domain = []
        if self.filter_name:
            domain.append(('name', 'ilike', self.filter_name))
        if self.filter_category_id:
            domain.append(('categ_id', 'child_of', self.filter_category_id.id))
        return domain
    
    def _get_products_to_process(self):
        """Get products based on selection mode"""
        if self.selection_mode == 'selected':
            return self.product_ids
        elif self.selection_mode == 'all_uncategorized':
            return self.env['product.template'].search([
                '|',
                ('service_type_id', '=', False),
                ('product_department_id', '=', False),
            ])
        else:
            return self.env['product.template'].search(self._build_filter_domain())
    
    def _detect_service_type(self, product_name):
        """Auto-detect service type based on product name patterns"""
        name_lower = product_name.lower()
        
        patterns = {
            'VISA': ['visa', 'employment visa', 'investor visa', 'golden visa', 'dependent visa', 'maid visa', 'emirate id', 'eid'],
            'ACCT': ['accounting', 'bookkeeping', 'audit', 'tax', 'vat', 'corporate tax', 'ct registration', 'financial'],
            'BANK': ['banking', 'bank account', 'mortgage', 'digital banking'],
            'SETUP': ['business setup', 'company formation', 'license issuance', 'pre-approval', 'fzco', 'setup'],
            'RENEW': ['renewal', 'license renewal', 'renew'],
            'LIQUID': ['liquidation', 'cancellation', 'cancel license', 'wind up'],
            'ADMIN': ['amendment', 'add activity', 'remove activity', 'shareholder', 'management change', 'name change'],
            'VALUE': ['pro', 'ejari', 'attestation', 'notary', 'medical', 'typing', 'tasheel'],
            'DOCUMENT': ['certificate', 'letter', 'clearance', 'approval', 'permit'],
        }
        
        ServiceType = self.env['product.service.type']
        
        for code, keywords in patterns.items():
            for keyword in keywords:
                if keyword in name_lower:
                    service_type = ServiceType.search([('code', '=like', code + '%')], limit=1, order='sequence')
                    if service_type:
                        return service_type
        
        return False
    
    def _detect_department(self, product_name):
        """Auto-detect department based on product name patterns"""
        name_lower = product_name.lower()
        
        Department = self.env['product.department']
        
        if any(x in name_lower for x in ['- accounts', 'accounting', 'finance', 'tax', 'audit']):
            return Department.search([('code', '=', 'ACCT')], limit=1)
        
        if any(x in name_lower for x in ['- operations', 'ops', 'processing']):
            return Department.search([('code', '=', 'OPS')], limit=1)
        
        if any(x in name_lower for x in ['- sales', 'sale', 'quotation']):
            return Department.search([('code', '=', 'SALES')], limit=1)
        
        if any(x in name_lower for x in ['pro', 'typing', 'admin', 'tasheel', 'amer']):
            return Department.search([('code', '=', 'PRO')], limit=1)
        
        return False
    
    def action_preview(self):
        """Show preview of changes before applying"""
        self.ensure_one()
        
        products = self._get_products_to_process()
        
        if not products:
            raise UserError(_('No products found matching the criteria.'))
        
        preview_lines = []
        for product in products[:50]:  # Limit preview to 50
            current_service = product.service_type_id.name if product.service_type_id else '-'
            current_dept = product.product_department_id.name if product.product_department_id else '-'
            
            if self.action_type == 'auto':
                new_service = self._detect_service_type(product.name)
                new_dept = self._detect_department(product.name)
                new_service_name = new_service.name if new_service else '(not detected)'
                new_dept_name = new_dept.name if new_dept else '(not detected)'
            elif self.action_type == 'manual':
                new_service_name = self.service_type_id.name if self.service_type_id else '(unchanged)'
                new_dept_name = self.department_id.name if self.department_id else '(unchanged)'
            else:
                new_service_name = '(cleared)'
                new_dept_name = '(cleared)'
            
            preview_lines.append(
                f"• {product.name}\n"
                f"  Service: {current_service} → {new_service_name}\n"
                f"  Dept: {current_dept} → {new_dept_name}"
            )
        
        if len(products) > 50:
            preview_lines.append(f"\n... and {len(products) - 50} more products")
        
        self.result_log = '\n'.join(preview_lines)
        
        return self._reopen_wizard()
    
    def action_apply(self):
        """Apply categorization to products"""
        self.ensure_one()
        
        products = self._get_products_to_process()
        
        if not products:
            raise UserError(_('No products found matching the criteria.'))
        
        processed = 0
        updated = 0
        skipped = 0
        log_lines = []
        
        for product in products:
            processed += 1
            updates = {}
            
            if self.action_type == 'auto':
                # Auto-detect values
                if self.update_service_type:
                    if self.overwrite_existing or not product.service_type_id:
                        detected = self._detect_service_type(product.name)
                        if detected:
                            updates['service_type_id'] = detected.id
                
                if self.update_department:
                    if self.overwrite_existing or not product.product_department_id:
                        detected = self._detect_department(product.name)
                        if detected:
                            updates['product_department_id'] = detected.id
                            
            elif self.action_type == 'manual':
                # Set specific values
                if self.update_service_type and self.service_type_id:
                    if self.overwrite_existing or not product.service_type_id:
                        updates['service_type_id'] = self.service_type_id.id
                
                if self.update_department and self.department_id:
                    if self.overwrite_existing or not product.product_department_id:
                        updates['product_department_id'] = self.department_id.id
                        
            else:  # clear
                if self.update_service_type:
                    updates['service_type_id'] = False
                if self.update_department:
                    updates['product_department_id'] = False
            
            if updates:
                product.write(updates)
                updated += 1
                log_lines.append(f"✓ {product.name}")
            else:
                skipped += 1
        
        self.processed_count = processed
        self.updated_count = updated
        self.skipped_count = skipped
        self.result_log = (
            f"RESULTS\n"
            f"========\n"
            f"Processed: {processed}\n"
            f"Updated: {updated}\n"
            f"Skipped: {skipped}\n\n"
            f"UPDATED PRODUCTS:\n" + '\n'.join(log_lines[-50:])
        )
        self.state = 'done'
        
        return self._reopen_wizard()
    
    def action_back(self):
        """Go back to configuration"""
        self.state = 'config'
        self.result_log = False
        return self._reopen_wizard()
    
    def _reopen_wizard(self):
        """Reopen wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.bulk.categorize',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_view_products(self):
        """View affected products"""
        products = self._get_products_to_process()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Products'),
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', products.ids)],
        }
