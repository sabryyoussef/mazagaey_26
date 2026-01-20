# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class ProductSearchPreset(models.Model):
    """Saved Search Filters for Quick Product Access"""
    _name = 'product.search.preset'
    _description = 'Product Search Preset'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Filter Name',
        required=True,
        translate=True,
    )
    
    description = fields.Text(
        string='Description',
        translate=True,
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        required=True,
    )
    
    is_public = fields.Boolean(
        string='Public Filter',
        default=False,
        help='Make this filter available to all users',
    )
    
    is_global = fields.Boolean(
        string='Global (System)',
        default=False,
        help='System-wide preset available to all users',
    )
    
    # Filter Configuration
    search_domain = fields.Text(
        string='Search Domain',
        required=True,
        help='JSON-encoded search domain',
    )
    
    filter_criteria = fields.Text(
        string='Filter Criteria',
        help='JSON-encoded filter criteria for wizard reconstruction',
    )
    
    sort_order = fields.Char(
        string='Sort Order',
        help='Field to sort results by',
    )
    
    # Statistics
    usage_count = fields.Integer(
        string='Times Used',
        default=0,
        help='Number of times this filter has been used',
    )
    
    last_used = fields.Datetime(
        string='Last Used',
        help='When this filter was last used',
    )
    
    # Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    
    active = fields.Boolean(
        default=True,
    )
    
    # Computed
    result_count = fields.Integer(
        string='Current Results',
        compute='_compute_result_count',
        help='Current number of products matching this filter',
    )
    
    @api.depends('search_domain')
    def _compute_result_count(self):
        """Compute current result count for this filter"""
        for preset in self:
            try:
                domain = json.loads(preset.search_domain)
                preset.result_count = self.env['product.template'].search_count(domain)
            except (json.JSONDecodeError, ValueError):
                preset.result_count = 0
    
    def action_execute_search(self):
        """Execute this search and show results"""
        self.ensure_one()
        
        # Update usage statistics
        self.write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now(),
        })
        
        # Parse domain
        try:
            domain = json.loads(self.search_domain)
        except (json.JSONDecodeError, ValueError):
            domain = []
        
        # Build action
        action = {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'product.template',
            'view_mode': 'kanban,tree,form',
            'domain': domain,
            'context': {
                'search_default_group_by_service_type': 1,
            },
        }
        
        # Apply sort order if specified
        if self.sort_order:
            action['context']['order'] = self.sort_order
        
        return action
    
    def action_duplicate(self):
        """Duplicate this filter"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Copy of {self.name}',
            'res_model': 'product.search.preset',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f'{self.name} (Copy)',
                'default_description': self.description,
                'default_search_domain': self.search_domain,
                'default_sort_order': self.sort_order,
                'default_is_public': False,
            },
        }
