# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTemplateUserPreferences(models.Model):
    _name = 'smart.template.user.preferences'
    _description = 'Smart Template User Preferences'
    _rec_name = 'user_id'
    
    # Core fields
    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        required=True, 
        ondelete='cascade',
        default=lambda self: self.env.user
    )
    
    # Suggestion behavior preferences
    suggestion_level = fields.Selection([
        ('passive', 'Passive - Show options only'),
        ('active', 'Active - Suggest and recommend'),
        ('smart', 'Smart - Auto-link based on patterns')
    ], string='Suggestion Level', default='active', required=True,
       help='How aggressive should template suggestions be?')
    
    trigger_behavior = fields.Selection([
        ('manual', 'Manual - User must select'),
        ('auto', 'Auto - Apply based on context'),
        ('hybrid', 'Hybrid - Suggest with confirmation')
    ], string='Trigger Behavior', default='hybrid', required=True,
       help='How should templates be applied?')
    
    preferred_start_template = fields.Selection([
        ('project', 'Project Template'),
        ('workflow', 'Workflow Template')
    ], string='Preferred Start Template', default='project', required=True,
       help='Which template type should be the default starting point?')
    
    # Advanced preferences
    enable_learning = fields.Boolean(
        string='Enable Learning', 
        default=True,
        help='Allow system to learn from your usage patterns'
    )
    
    show_compatibility_warnings = fields.Boolean(
        string='Show Compatibility Warnings', 
        default=True,
        help='Show warnings when templates may not be compatible'
    )
    
    auto_save_preferences = fields.Boolean(
        string='Auto-save Preferences', 
        default=True,
        help='Automatically save preference changes'
    )
    
    # Computed fields
    is_default = fields.Boolean(
        string='Is Default', 
        compute='_compute_is_default',
        store=True
    )
    
    @api.depends('user_id')
    def _compute_is_default(self):
        for record in self:
            record.is_default = record.user_id == self.env.user
    
    # Constraints
    _sql_constraints = [
        ('unique_user_preferences', 
         'UNIQUE(user_id)', 
         'Each user can only have one set of preferences!')
    ]
    
    # Methods
    @api.model
    def get_user_preferences(self, user_id=None):
        """Get preferences for a specific user or current user"""
        if not user_id:
            user_id = self.env.user.id
        
        preferences = self.search([('user_id', '=', user_id)], limit=1)
        if not preferences:
            # Create default preferences if none exist
            preferences = self.create({
                'user_id': user_id,
                'suggestion_level': 'active',
                'trigger_behavior': 'hybrid',
                'preferred_start_template': 'project',
            })
        
        return preferences
    
    def apply_preferences(self, context=None):
        """Apply user preferences to a given context"""
        if not context:
            context = {}
        
        return {
            'suggestion_level': self.suggestion_level,
            'trigger_behavior': self.trigger_behavior,
            'preferred_start_template': self.preferred_start_template,
            'enable_learning': self.enable_learning,
            'show_compatibility_warnings': self.show_compatibility_warnings,
        }


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    smart_template_preferences_ids = fields.One2many(
        'smart.template.user.preferences',
        'user_id',
        string='Smart Template Preferences'
    )
    
    def get_smart_template_preferences(self):
        """Get smart template preferences for this user"""
        return self.env['smart.template.user.preferences'].get_user_preferences(self.id)
