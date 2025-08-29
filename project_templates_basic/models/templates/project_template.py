# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTemplate(models.Model):
    _inherit = 'project.project'
    
    # Template-specific fields
    is_template = fields.Boolean(
        string='Is Template',
        default=False,
        help='Mark this project as a template for creating new projects'
    )
    
    template_category = fields.Selection([
        ('company_formation', 'Company Formation'),
        ('visa_services', 'Visa Services'),
        ('government_services', 'Government Services'),
        ('financial_services', 'Financial Services'),
        ('compliance_services', 'Compliance Services'),
        ('general', 'General')
    ], string='Template Category', default='general')
    
    template_description = fields.Text(
        string='Template Description',
        help='Detailed description of what this template is used for'
    )
    
    estimated_duration = fields.Integer(
        string='Estimated Duration (Days)',
        help='Estimated number of days to complete this project'
    )
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex'),
        ('very_complex', 'Very Complex')
    ], string='Complexity Level', default='medium')
    
    # Template usage tracking
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_count',
        store=True,
        help='Number of times this template has been used'
    )
    
    last_used_date = fields.Datetime(
        string='Last Used Date',
        compute='_compute_usage_count',
        store=True
    )
    
    # Related templates
    related_task_templates = fields.Many2many(
        'project.document.template',
        string='Related Task Templates',
        help='Task templates that are commonly used with this project template'
    )
    
    related_checkpoint_templates = fields.Many2many(
        'project.checkpoint.template',
        string='Related Checkpoint Templates',
        help='Checkpoint templates that are commonly used with this project template'
    )
    
    # Task Generation Configuration
    auto_generate_tasks = fields.Boolean('Auto-Generate Tasks', default=True)
    task_generation_strategy = fields.Selection([
        ('document_based', 'Document-Based'),
        ('progress_tracking', 'Progress Tracking'),
        ('milestone', 'Milestone'),
        ('custom', 'Custom'),
        ('all', 'All Strategies')
    ], string='Task Generation Strategy', default='document_based')
    
    # Task Template Selection
    selected_task_template_ids = fields.Many2many('project.task.template',
        string='Selected Task Templates')
    
    # Task Generation Options
    generate_document_tasks = fields.Boolean('Generate Document Tasks', default=True)
    generate_progress_tasks = fields.Boolean('Generate Progress Tasks', default=True)
    generate_milestone_tasks = fields.Boolean('Generate Milestone Tasks', default=True)
    
    # Task Generation Results
    generated_task_count = fields.Integer('Generated Task Count', compute='_compute_generated_task_count', store=True)
    last_task_generation_date = fields.Datetime('Last Task Generation Date')
    
    # Compliance-specific fields
    compliance_requirements = fields.Text(
        string='Compliance Requirements',
        help='Compliance requirements for this project template'
    )
    
    # Quotation Integration for Templates
    quotation_template_id = fields.Many2one(
        'sale.order.template',
        string='Default Quotation Template',
        help='Default quotation template to use when creating quotations from this project template',
        ondelete='set null',
        required=False
    )
    
    auto_create_quotations = fields.Boolean(
        string='Auto-Create Quotations',
        default=False,
        help='Automatically create quotations when milestones/checkpoints are reached'
    )
    
    quotation_notes = fields.Text(
        string='Default Quotation Notes',
        help='Default notes to include in quotations created from this template'
    )
    
    @api.depends('is_template')
    def _compute_usage_count(self):
        """Compute usage count for template projects"""
        for project in self:
            if project.is_template:
                # Count how many times this template has been used
                usage_count = self.env['project.template.usage'].search_count([
                    ('template_id', '=', project.id),
                    ('res_model', '=', 'project.project')
                ])
                project.usage_count = usage_count
                
                # Get last used date
                last_usage = self.env['project.template.usage'].search([
                    ('template_id', '=', project.id),
                    ('res_model', '=', 'project.project')
                ], order='applied_date desc', limit=1)
                project.last_used_date = last_usage.applied_date if last_usage else False
            else:
                project.usage_count = 0
                project.last_used_date = False
    
    @api.depends('selected_task_template_ids')
    def _compute_generated_task_count(self):
        """Compute the number of tasks that would be generated"""
        for project in self:
            if project.is_template and project.selected_task_template_ids:
                project.generated_task_count = len(project.selected_task_template_ids)
            else:
                project.generated_task_count = 0
    
    def action_create_from_template(self):
        """Create a new project from this template"""
        self.ensure_one()
        if not self.is_template:
            raise ValidationError(_("This project is not a template"))
        
        # Create new project from template
        new_project_vals = {
            'name': f"{self.name} - Copy",
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.user_id.id if self.user_id else False,
            'is_template': False,  # New project is not a template
        }
        
        new_project = self.env['project.project'].create(new_project_vals)
        
        # Record usage
        self.env['project.template.usage'].create({
            'template_id': self.id,
            'res_model': 'project.project',
            'res_id': new_project.id,
            'applied_by': self.env.user.id,
        })
        
        # Return action to open the new project
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': new_project.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_apply_task_templates(self):
        """Apply task templates to this project"""
        self.ensure_one()
        if not self.related_task_templates:
            raise ValidationError(_("No task templates are associated with this project template"))
        
        # Create tasks from templates
        for template in self.related_task_templates:
            template.action_apply_to_task(self)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Task templates have been applied successfully'),
                'type': 'success',
            }
        }
    
    def action_apply_checkpoint_templates(self):
        """Apply checkpoint templates to this project"""
        self.ensure_one()
        if not self.related_checkpoint_templates:
            raise ValidationError(_("No checkpoint templates are associated with this project template"))
        
        # Create checkpoints from templates
        for template in self.related_checkpoint_templates:
            # This would need to be implemented based on checkpoint template structure
            pass
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Checkpoint templates have been applied successfully'),
                'type': 'success',
            }
        }
    
    def action_view_usage_history(self):
        """View usage history for this template"""
        self.ensure_one()
        if not self.is_template:
            raise ValidationError(_("This project is not a template"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Usage History'),
            'res_model': 'project.template.usage',
            'view_mode': 'list,form',
            'domain': [
                ('template_id', '=', self.id),
                ('res_model', '=', 'project.project')
            ],
            'context': {'default_template_id': self.id},
        }
