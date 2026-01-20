# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductDepartment(models.Model):
    """Department Taxonomy for Product Organization"""
    _name = 'product.department'
    _description = 'Product Department'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Department Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for this department (e.g., ACCT, OPS, SALES)',
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    
    # Relationships
    manager_id = fields.Many2one(
        'res.users',
        string='Department Manager',
        help='Responsible person for this department',
    )
    member_ids = fields.Many2many(
        'res.users',
        'product_department_users_rel',
        'department_id',
        'user_id',
        string='Team Members',
    )
    
    # Products
    product_ids = fields.One2many(
        'product.template',
        'product_department_id',
        string='Products',
    )
    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
        store=True,
    )
    
    # Statistics
    total_products_value = fields.Monetary(
        string='Total Products Value',
        compute='_compute_statistics',
        currency_field='currency_id',
    )
    avg_product_price = fields.Monetary(
        string='Average Product Price',
        compute='_compute_statistics',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    
    # Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        default=True,
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
    )
    
    _sql_constraints = [
        ('code_uniq', 'UNIQUE (code)', 'Department code must be unique!'),
    ]
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Compute product count"""
        for dept in self:
            dept.product_count = len(dept.product_ids)
    
    @api.depends('product_ids', 'product_ids.list_price')
    def _compute_statistics(self):
        """Compute department product statistics"""
        for dept in self:
            products = dept.product_ids
            if products:
                dept.total_products_value = sum(products.mapped('list_price'))
                dept.avg_product_price = dept.total_products_value / len(products)
            else:
                dept.total_products_value = 0.0
                dept.avg_product_price = 0.0
    
    def action_view_products(self):
        """Open products for this department"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Products',
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': [('product_department_id', '=', self.id)],
            'context': {
                'default_product_department_id': self.id,
                'search_default_group_by_service_type': 1,
            },
        }
