# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductServiceType(models.Model):
    """Service Type Taxonomy for Product Classification"""
    _name = 'product.service.type'
    _description = 'Product Service Type'
    _order = 'sequence, name'
    _parent_name = 'parent_id'
    _parent_store = True
    
    name = fields.Char(
        string='Service Type Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for this service type (e.g., VISA, ACCT, BANK)',
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    parent_id = fields.Many2one(
        'product.service.type',
        string='Parent Service Type',
        ondelete='restrict',
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'product.service.type',
        'parent_id',
        string='Child Service Types',
    )
    
    # Display
    icon = fields.Char(
        string='Icon Class',
        help='Font Awesome icon class (e.g., fa-id-card)',
        default='fa-cube',
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color index for Kanban view (0-11)',
    )
    
    # Statistics
    product_ids = fields.One2many(
        'product.template',
        'service_type_id',
        string='Products',
    )
    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
        store=True,
    )
    
    # Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order service types',
    )
    active = fields.Boolean(
        default=True,
    )
    
    # Computed fields
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )
    
    _sql_constraints = [
        ('code_uniq', 'UNIQUE (code)', 'Service type code must be unique!'),
    ]
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Compute total product count including children"""
        for service_type in self:
            if service_type.child_ids:
                # Include products from all children
                all_children = service_type.search([
                    ('id', 'child_of', service_type.id)
                ])
                service_type.product_count = self.env['product.template'].search_count([
                    ('service_type_id', 'in', all_children.ids)
                ])
            else:
                service_type.product_count = len(service_type.product_ids)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        """Compute complete hierarchical name"""
        for service_type in self:
            if service_type.parent_id:
                service_type.complete_name = '%s / %s' % (
                    service_type.parent_id.complete_name,
                    service_type.name
                )
            else:
                service_type.complete_name = service_type.name
    
    def name_get(self):
        """Display complete name in selectors"""
        result = []
        for service_type in self:
            name = service_type.complete_name or service_type.name
            result.append((service_type.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Search by code or name"""
        args = args or []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
            if operator in ('=', '!='):
                domain = ['|'] + domain + [('complete_name', operator, name)]
            return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name, args, operator, limit, name_get_uid)
    
    def action_view_products(self):
        """Open products for this service type"""
        self.ensure_one()
        
        # Get all children service types
        all_service_types = self.search([('id', 'child_of', self.id)])
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Products',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('service_type_id', 'in', all_service_types.ids)],
            'context': {
                'default_service_type_id': self.id,
                'search_default_group_by_categ': 1,
            },
        }
