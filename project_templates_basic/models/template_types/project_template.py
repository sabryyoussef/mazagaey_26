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
    
    shareholder_requirements = fields.Text(
        string='Shareholder Requirements',
        help='Shareholder requirements for compliance'
    )
    
    ubo_requirements = fields.Text(
        string='UBO Requirements',
        help='Ultimate Beneficial Owner requirements'
    )
    
    document_requirements = fields.Text(
        string='Document Requirements',
        help='Required documents for compliance'
    )
    
    @api.depends('task_ids')
    def _compute_usage_count(self):
        """Compute usage count and last used date"""
        for project in self:
            if project.is_template:
                # Count how many projects were created from this template
                # This would need to be tracked when templates are applied
                project.usage_count = 0  # Placeholder - implement tracking logic
                project.last_used_date = False  # Placeholder
            else:
                project.usage_count = 0
                project.last_used_date = False
    
    @api.model
    def create(self, vals):
        """Override create to handle template-specific behavior"""
        # For templates, disable document folder creation
        if vals.get('is_template'):
            vals['use_documents'] = False
        
        result = super().create(vals)
        return result
    
    def action_create_from_template(self):
        """Create a new project from this template"""
        self.ensure_one()
        if not self.is_template:
            raise ValidationError(_('This project is not marked as a template.'))
        
        # Create new project with template data
        new_project_vals = {
            'name': f"{self.name} - Copy",
            'description': self.description,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.user_id.id if self.user_id else False,
            'is_template': False,  # New project is not a template
        }
        
        new_project = self.env['project.project'].create(new_project_vals)
        
        # Copy tasks from template
        for task in self.task_ids:
            task_vals = {
                'name': task.name,
                'description': task.description,
                'project_id': new_project.id,
                'user_ids': [(6, 0, task.user_ids.ids)] if task.user_ids else False,
                'priority': task.priority,
                'sequence': task.sequence,
            }
            self.env['project.task'].create(task_vals)
        
        # Increment usage count
        self.usage_count += 1
        self.last_used_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': new_project.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_apply_task_templates(self):
        """Apply related task templates to this project"""
        self.ensure_one()
        
        if not self.related_task_templates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Templates'),
                    'message': _('No task templates are linked to this project template.'),
                    'type': 'warning',
                }
            }
        
        created_tasks = []
        for task_template in self.related_task_templates:
            task_vals = {
                'name': task_template.name,
                'description': task_template.description,
                'project_id': self.id,
                'priority': task_template.priority,
                'sequence': task_template.sequence,
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Templates Applied'),
                'message': _('Applied %d task templates to the project.') % len(created_tasks),
                'type': 'success',
            }
        }
    
    def action_apply_checkpoint_templates(self):
        """Apply related checkpoint templates to this project"""
        self.ensure_one()
        
        if not self.related_checkpoint_templates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Checkpoint Templates'),
                    'message': _('No checkpoint templates are linked to this project template.'),
                    'type': 'warning',
                }
            }
        
        created_checkpoints = []
        # Get the first task in the project to attach checkpoints to
        first_task = self.task_ids and self.task_ids[0] or False
        
        if first_task:
            for checkpoint_template in self.related_checkpoint_templates:
                checkpoint_vals = {
                    'name': checkpoint_template.name,
                    'notes': checkpoint_template.notes,
                    'task_id': first_task.id,
                    'sequence': checkpoint_template.sequence,
                }
                checkpoint = self.env['project.task.checkpoint'].create(checkpoint_vals)
                created_checkpoints.append(checkpoint)
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Tasks'),
                    'message': _('This project has no tasks to attach checkpoints to.'),
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Checkpoint Templates Applied'),
                'message': _('Applied %d checkpoint templates to the project.') % len(created_checkpoints),
                'type': 'success',
            }
        }
    
    def action_view_usage_history(self):
        """View usage history of this template"""
        self.ensure_one()
        
        # This would open a view showing projects created from this template
        return {
            'name': _('Template Usage History - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'domain': [
                ('is_template', '=', False),
                # Add domain to filter projects created from this template
                # This would need additional tracking fields
            ],
            'context': {
                'default_is_template': False,
            },
        }
    
    @api.depends('task_ids')
    def _compute_generated_task_count(self):
        """Compute the number of tasks generated from templates"""
        for project in self:
            if project.is_template:
                # Count tasks that were generated from templates
                generated_tasks = project.task_ids.filtered(lambda t: t.is_generated_from_template)
                project.generated_task_count = len(generated_tasks)
            else:
                project.generated_task_count = 0
    
    def action_generate_tasks_from_template(self):
        """Generate tasks from this project template"""
        self.ensure_one()
        
        if not self.is_template:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Not a Template'),
                    'message': _('This project is not marked as a template.'),
                    'type': 'warning',
                }
            }
        
        try:
            # Get task generation service
            task_service = self.env['project.task.generation.service']
            
            # Get task templates based on strategy
            task_templates = self._get_task_templates_for_strategy()
            
            if not task_templates:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('No Task Templates'),
                        'message': _('No task templates found for the selected strategy.'),
                        'type': 'warning',
                    }
                }
            
            # Prepare generation options
            options = {
                'generate_document_tasks': self.generate_document_tasks,
                'generate_progress_tasks': self.generate_progress_tasks,
                'generate_milestone_tasks': self.generate_milestone_tasks,
                'generate_overall_progress': True,
                'generate_category_progress': True,
                'set_dependencies': True,
                'assign_users': False,
            }
            
            # Generate tasks
            result = task_service.generate_tasks_from_project_template(
                self, task_templates, options
            )
            
            if result['success']:
                # Update generation date
                self.last_task_generation_date = fields.Datetime.now()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Tasks Generated Successfully'),
                        'message': result['message'],
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Task Generation Failed'),
                        'message': result['message'],
                        'type': 'error',
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error generating tasks from project template: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('An error occurred while generating tasks: %s') % str(e),
                    'type': 'error',
                }
            }
    
    def action_configure_task_generation(self):
        """Configure task generation settings"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configure Task Generation'),
            'res_model': 'project.project',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_is_template': True,
                'form_view_initial_mode': 'edit',
            },
        }
    
    def action_preview_generated_tasks(self):
        """Preview tasks that would be generated"""
        self.ensure_one()
        
        if not self.is_template:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Not a Template'),
                    'message': _('This project is not marked as a template.'),
                    'type': 'warning',
                }
            }
        
        # Get task templates for preview
        task_templates = self._get_task_templates_for_strategy()
        
        if not task_templates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Templates'),
                    'message': _('No task templates found for preview.'),
                    'type': 'warning',
                }
            }
        
        # Create preview data
        preview_data = []
        for template in task_templates:
            preview_data.append({
                'template_name': template.name,
                'template_type': template.template_type,
                'document_category': template.document_category,
                'estimated_hours': template.estimated_hours,
                'priority': template.priority,
                'task_name': template.get_task_name({
                    'category': template.document_category,
                    'count': 5,  # Example count
                    'project_name': self.name
                }),
                'task_description': template.get_task_description({
                    'category': template.document_category,
                    'count': 5,  # Example count
                    'project_name': self.name
                })
            })
        
        # Return preview action (this would need a custom wizard or view)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Preview'),
                'message': _('Would generate %d tasks from %d templates.') % (len(preview_data), len(task_templates)),
                'type': 'info',
            }
        }
    
    def _get_task_templates_for_strategy(self):
        """Get task templates based on the selected strategy"""
        domain = [('active', '=', True)]
        
        if self.task_generation_strategy == 'document_based':
            domain.append(('template_type', '=', 'document_based'))
        elif self.task_generation_strategy == 'progress_tracking':
            domain.append(('template_type', '=', 'progress_tracking'))
        elif self.task_generation_strategy == 'milestone':
            domain.append(('template_type', '=', 'milestone'))
        elif self.task_generation_strategy == 'custom':
            domain.append(('template_type', '=', 'custom'))
        elif self.task_generation_strategy == 'all':
            # No additional filter - get all types
            pass
        
        # If specific templates are selected, use those
        if self.selected_task_template_ids:
            return self.selected_task_template_ids
        
        return self.env['project.task.template'].search(domain)
