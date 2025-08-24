# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class WorkflowTemplateWizard(models.TransientModel):
    _name = 'workflow.template.wizard'
    _description = 'Workflow Template Creation Wizard'

    # Step tracking
    current_step = fields.Selection([
        ('product', 'Product Template'),
        ('project', 'Project Template'),
        ('checkpoints', 'Checkpoint Templates'),
        ('tasks', 'Task Templates'),
        ('review', 'Review & Create')
    ], string='Current Step', default='product', required=True)

    # Progress tracking
    progress = fields.Float('Progress', compute='_compute_progress', store=True)
    step_count = fields.Integer('Total Steps', default=5)
    completed_steps = fields.Integer('Completed Steps', compute='_compute_progress', store=True)
    
    @api.model
    def create(self, vals):
        """Ensure wizard always starts from step 1"""
        vals['current_step'] = 'product'
        return super().create(vals)
    
    @api.model
    def default_get(self, fields_list):
        """Set default values when wizard is opened"""
        defaults = super().default_get(fields_list)
        defaults['current_step'] = 'product'
        return defaults

    # Product Template Section
    product_name = fields.Char('Product Template Name')
    product_description = fields.Text('Product Description')
    product_category = fields.Many2one('product.category', string='Product Category')
    product_type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Product'),
        ('consu', 'Consumable')
    ], string='Product Type', default='service', required=True)
    
    # Product Template Selection
    existing_product_template_id = fields.Many2one('product.template', string='Select Existing Product Template')
    use_existing_product = fields.Boolean('Use Existing Product Template', default=False)

    # Project Template Section
    project_name = fields.Char('Project Template Name')
    project_description = fields.Text('Project Description')
    project_duration = fields.Integer('Estimated Duration (Days)', default=30)
    project_complexity = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Project Complexity', default='medium')
    auto_generate_tasks = fields.Boolean('Auto-Generate Tasks', default=True)
    task_generation_strategy = fields.Selection([
        ('document_based', 'Document-Based'),
        ('progress_tracking', 'Progress Tracking'),
        ('milestone', 'Milestone-Based'),
        ('custom', 'Custom')
    ], string='Task Generation Strategy', default='document_based')
    
    # Project Template Selection
    existing_project_template_id = fields.Many2one('project.project', string='Select Existing Project Template', domain="[('is_template', '=', True)]")
    use_existing_project = fields.Boolean('Use Existing Project Template', default=False)

    # Checkpoint Templates Section
    checkpoint_template_ids = fields.One2many('workflow.checkpoint.template.wizard', 'wizard_id', string='Checkpoint Templates')
    create_default_checkpoints = fields.Boolean('Create Default Checkpoint Templates', default=True)
    
    # Checkpoint Template Selection
    existing_checkpoint_template_ids = fields.Many2many('project.checkpoint.template', string='Select Existing Checkpoint Templates')
    use_existing_checkpoints = fields.Boolean('Use Existing Checkpoint Templates', default=False)

    # Task Templates Section
    task_template_ids = fields.One2many('workflow.task.template.wizard', 'wizard_id', string='Task Templates')
    create_default_tasks = fields.Boolean('Create Default Task Templates', default=True)
    
    # Task Template Selection
    existing_task_template_ids = fields.Many2many('project.task.template', string='Select Existing Task Templates')
    use_existing_tasks = fields.Boolean('Use Existing Task Templates', default=False)

    # Review Section
    summary_product = fields.Text('Product Template Summary', readonly=True)
    summary_project = fields.Text('Project Template Summary', readonly=True)
    summary_tasks = fields.Text('Task Templates Summary', readonly=True)

    @api.depends('current_step')
    def _compute_progress(self):
        for wizard in self:
            step_mapping = {
                'product': 1,
                'project': 2,
                'checkpoints': 3,
                'tasks': 4,
                'review': 5
            }
            wizard.completed_steps = step_mapping.get(wizard.current_step, 0)
            wizard.progress = (wizard.completed_steps / wizard.step_count) * 100

    @api.onchange('product_name')
    def _onchange_product_name(self):
        """Auto-generate project name from product name"""
        if self.product_name and not self.project_name:
            self.project_name = f"Project: {self.product_name}"

    @api.onchange('create_default_tasks')
    def _onchange_create_default_tasks(self):
        """Create default task templates when checkbox is checked"""
        if self.create_default_tasks and not self.task_template_ids and not self.use_existing_tasks:
            self._create_default_task_templates()

    @api.onchange('use_existing_product', 'existing_product_template_id')
    def _onchange_existing_product(self):
        """Update fields when existing product template is selected"""
        if self.use_existing_product and self.existing_product_template_id:
            self.product_name = self.existing_product_template_id.name
            self.product_description = self.existing_product_template_id.description or ''
            self.product_category = self.existing_product_template_id.categ_id
            self.product_type = self.existing_product_template_id.type
        elif not self.use_existing_product:
            # Clear the existing product template selection
            self.existing_product_template_id = False

    @api.onchange('use_existing_project', 'existing_project_template_id')
    def _onchange_existing_project(self):
        """Update fields when existing project template is selected"""
        if self.use_existing_project and self.existing_project_template_id:
            self.project_name = self.existing_project_template_id.name
            self.project_description = self.existing_project_template_id.description or ''
            # Note: project_duration and project_complexity might not exist on standard project.project
            # We'll keep the default values or add custom fields if needed
        elif not self.use_existing_project:
            # Clear the existing project template selection
            self.existing_project_template_id = False

    @api.onchange('use_existing_tasks', 'existing_task_template_ids')
    def _onchange_existing_tasks(self):
        """Update fields when existing task templates are selected"""
        if self.use_existing_tasks and self.existing_task_template_ids:
            # Clear the default task templates when using existing ones
            self.task_template_ids = [(5, 0, 0)]
            self.create_default_tasks = False
        elif not self.use_existing_tasks:
            # Clear the existing task template selection
            self.existing_task_template_ids = [(5, 0, 0)]

    @api.onchange('use_existing_checkpoints', 'existing_checkpoint_template_ids')
    def _onchange_existing_checkpoints(self):
        """Update fields when existing checkpoint templates are selected"""
        if self.use_existing_checkpoints and self.existing_checkpoint_template_ids:
            # Clear the default checkpoint templates when using existing ones
            self.checkpoint_template_ids = [(5, 0, 0)]
            self.create_default_checkpoints = False
        elif not self.use_existing_checkpoints:
            # Clear the existing checkpoint template selection
            self.existing_checkpoint_template_ids = [(5, 0, 0)]

    def _create_default_task_templates(self):
        """Create default task templates based on the strategy"""
        default_tasks = []
        
        if self.task_generation_strategy == 'document_based':
            default_tasks = [
                {'name': 'Requirements Gathering', 'template_type': 'document_based', 'document_category': 'required'},
                {'name': 'Design & Planning', 'template_type': 'document_based', 'document_category': 'deliverable'},
                {'name': 'Development & Testing', 'template_type': 'document_based', 'document_category': 'deliverable'},
                {'name': 'Documentation', 'template_type': 'document_based', 'document_category': 'reference'},
            ]
        elif self.task_generation_strategy == 'progress_tracking':
            default_tasks = [
                {'name': 'Project Initiation', 'template_type': 'progress_tracking', 'document_category': 'all'},
                {'name': 'Planning Phase', 'template_type': 'progress_tracking', 'document_category': 'all'},
                {'name': 'Execution Phase', 'template_type': 'progress_tracking', 'document_category': 'all'},
                {'name': 'Monitoring & Control', 'template_type': 'progress_tracking', 'document_category': 'all'},
                {'name': 'Project Closure', 'template_type': 'progress_tracking', 'document_category': 'all'},
            ]
        elif self.task_generation_strategy == 'milestone':
            default_tasks = [
                {'name': 'Project Kickoff', 'template_type': 'milestone', 'document_category': 'all'},
                {'name': 'Requirements Complete', 'template_type': 'milestone', 'document_category': 'all'},
                {'name': 'Design Complete', 'template_type': 'milestone', 'document_category': 'all'},
                {'name': 'Development Complete', 'template_type': 'milestone', 'document_category': 'all'},
                {'name': 'Testing Complete', 'template_type': 'milestone', 'document_category': 'all'},
                {'name': 'Project Delivery', 'template_type': 'milestone', 'document_category': 'all'},
            ]

        # Clear existing task templates
        self.task_template_ids = [(5, 0, 0)]
        
        # Create new default task templates
        for i, task_data in enumerate(default_tasks):
            task_vals = {
                'sequence': (i + 1) * 10,
                'name': task_data['name'],
                'template_type': task_data['template_type'],
                'document_category': task_data['document_category'],
                'priority': '1',
                'estimated_hours': 8.0,
                'description': f"Default {task_data['template_type']} task for {self.project_name or 'project'}",
            }
            self.task_template_ids = [(0, 0, task_vals)]

    def _create_default_checkpoint_templates(self):
        """Create default checkpoint templates based on the project complexity"""
        default_checkpoints = []
        
        if self.project_complexity == 'simple':
            default_checkpoints = [
                {'name': 'Project Initiation', 'description': 'Project kickoff and team setup', 'checkpoint_type': 'milestone'},
                {'name': 'Requirements Review', 'description': 'Review and approve project requirements', 'checkpoint_type': 'review'},
                {'name': 'Project Completion', 'description': 'Final delivery and project closure', 'checkpoint_type': 'milestone'},
            ]
        elif self.project_complexity == 'medium':
            default_checkpoints = [
                {'name': 'Project Initiation', 'description': 'Project kickoff and team setup', 'checkpoint_type': 'milestone'},
                {'name': 'Requirements Review', 'description': 'Review and approve project requirements', 'checkpoint_type': 'review'},
                {'name': 'Design Approval', 'description': 'Approve design and architecture', 'checkpoint_type': 'review'},
                {'name': 'Development Progress', 'description': 'Mid-development progress review', 'checkpoint_type': 'progress'},
                {'name': 'Testing Phase', 'description': 'Testing and quality assurance', 'checkpoint_type': 'milestone'},
                {'name': 'Project Completion', 'description': 'Final delivery and project closure', 'checkpoint_type': 'milestone'},
            ]
        else:  # complex
            default_checkpoints = [
                {'name': 'Project Initiation', 'description': 'Project kickoff and team setup', 'checkpoint_type': 'milestone'},
                {'name': 'Requirements Review', 'description': 'Review and approve project requirements', 'checkpoint_type': 'review'},
                {'name': 'Architecture Design', 'description': 'System architecture and design approval', 'checkpoint_type': 'review'},
                {'name': 'Detailed Design', 'description': 'Detailed design and specifications', 'checkpoint_type': 'review'},
                {'name': 'Development Phase 1', 'description': 'First development phase review', 'checkpoint_type': 'progress'},
                {'name': 'Development Phase 2', 'description': 'Second development phase review', 'checkpoint_type': 'progress'},
                {'name': 'Integration Testing', 'description': 'Integration and system testing', 'checkpoint_type': 'milestone'},
                {'name': 'User Acceptance Testing', 'description': 'UAT and stakeholder approval', 'checkpoint_type': 'milestone'},
                {'name': 'Project Completion', 'description': 'Final delivery and project closure', 'checkpoint_type': 'milestone'},
            ]

        # Clear existing checkpoint templates
        self.checkpoint_template_ids = [(5, 0, 0)]
        
        # Create new default checkpoint templates
        for i, checkpoint_data in enumerate(default_checkpoints):
            checkpoint_vals = {
                'sequence': (i + 1) * 10,
                'name': checkpoint_data['name'],
                'description': checkpoint_data['description'],
                'checkpoint_type': checkpoint_data['checkpoint_type'],
                'is_mandatory': True,
                'estimated_days': 1,
            }
            self.checkpoint_template_ids = [(0, 0, checkpoint_vals)]

    def action_next_step(self):
        """Move to the next step"""
        if self.current_step == 'product':
            # Only validate if not using existing product template
            if not self.use_existing_product and not self.product_name:
                raise ValidationError(_('Please enter a product template name or select an existing product template.'))
            self.current_step = 'project'
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_project').id
        elif self.current_step == 'project':
            # Only validate if not using existing project template
            if not self.use_existing_project and not self.project_name:
                raise ValidationError(_('Please enter a project template name or select an existing project template.'))
            self.current_step = 'checkpoints'
            self._create_default_checkpoint_templates()
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_checkpoints').id
        elif self.current_step == 'checkpoints':
            self.current_step = 'tasks'
            self._create_default_task_templates()
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_tasks').id
        elif self.current_step == 'tasks':
            self.current_step = 'review'
            self._generate_summaries()
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_review').id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.template.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }

    def action_previous_step(self):
        """Move to the previous step"""
        if self.current_step == 'project':
            self.current_step = 'product'
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_product').id
        elif self.current_step == 'checkpoints':
            self.current_step = 'project'
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_project').id
        elif self.current_step == 'tasks':
            self.current_step = 'checkpoints'
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_checkpoints').id
        elif self.current_step == 'review':
            self.current_step = 'tasks'
            view_id = self.env.ref('project_templates_basic.view_workflow_template_wizard_tasks').id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.template.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }

    def action_view_product_templates(self):
        """Open product templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'default_type': 'service',
                'search_default_service': 1,
            }
        }

    def action_create_product_template(self):
        """Open product template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_type': 'service',
                'default_name': self.product_name or 'New Product Template',
                'default_description': self.product_description or '',
                'default_categ_id': self.product_category.id if self.product_category else False,
            }
        }

    def action_view_project_templates(self):
        """Open project templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'target': 'new',
            'domain': [('is_template', '=', True)],
            'context': {
                'default_is_template': True,
                'search_default_templates': 1,
            }
        }

    def action_create_project_template(self):
        """Open project template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_is_template': True,
                'default_name': self.project_name or 'New Project Template',
                'default_description': self.project_description or '',
                'default_use_documents': False,
            }
        }

    def action_view_task_templates(self):
        """Open task templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'search_default_active': 1,
            }
        }

    def action_create_task_template(self):
        """Open task template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_type': 'document_based',
                'default_document_category': 'required',
                'default_priority': 1,
                'default_estimated_hours': 1.0,
            }
        }

    def action_view_checkpoint_templates(self):
        """Open checkpoint templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'search_default_active': 1,
            }
        }

    def action_create_checkpoint_template(self):
        """Open checkpoint template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_checkpoint_type': 'milestone',
                'default_is_mandatory': True,
                'default_estimated_days': 1,
            }
        }

    def _generate_summaries(self):
        """Generate summary text for review step"""
        # Product template summary
        if self.use_existing_product and self.existing_product_template_id:
            product_name = self.existing_product_template_id.name
            product_type = self.existing_product_template_id.type
            product_category = self.existing_product_template_id.categ_id.name if self.existing_product_template_id.categ_id else 'Not specified'
            product_description = self.existing_product_template_id.description or 'No description provided'
        else:
            product_name = self.product_name or 'Not specified'
            product_type = self.product_type
            product_category = self.product_category.name if self.product_category else 'Not specified'
            product_description = self.product_description or 'No description provided'
        
        self.summary_product = f"""
Product Template: {product_name}
Type: {product_type}
Category: {product_category}
Description: {product_description}
        """.strip()

        # Project template summary
        if self.use_existing_project and self.existing_project_template_id:
            project_name = self.existing_project_template_id.name
            project_description = self.existing_project_template_id.description or 'No description provided'
        else:
            project_name = self.project_name or 'Not specified'
            project_description = self.project_description or 'No description provided'
        
        self.summary_project = f"""
Project Template: {project_name}
Duration: {self.project_duration} days
Complexity: {self.project_complexity}
Auto-Generate Tasks: {'Yes' if self.auto_generate_tasks else 'No'}
Task Strategy: {self.task_generation_strategy}
Description: {project_description}
        """.strip()

        # Task templates summary
        if self.use_existing_tasks and self.existing_task_template_ids:
            task_count = len(self.existing_task_template_ids)
            task_summary = f"Total Existing Tasks: {task_count}\n"
            task_summary += "Using existing task templates"
        else:
            task_count = len(self.task_template_ids)
            task_types = {}
            for task in self.task_template_ids:
                task_types[task.template_type] = task_types.get(task.template_type, 0) + 1
            
            task_summary = f"Total Tasks: {task_count}\n"
            for task_type, count in task_types.items():
                task_summary += f"{task_type.title()}: {count}\n"
        
        self.summary_tasks = task_summary.strip()

    def action_create_workflow(self):
        """Create the complete workflow template"""
        try:
            # 1. Create Product Template
            product_template = self._create_product_template()
            
            # 2. Create Project Template
            project_template = self._create_project_template()
            
            # 3. Create Checkpoint Templates
            checkpoint_templates = self._create_checkpoint_templates()
            
            # 4. Create Task Templates
            task_templates = self._create_task_templates()
            
            # 5. Link everything together
            self._link_templates(product_template, project_template, task_templates, checkpoint_templates)
            
            # 6. Create Workflow Template Record
            workflow_template = self._create_workflow_template_record(product_template, project_template, task_templates, checkpoint_templates)
            
            # 6. Show success message and return to templates
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Template Created!'),
                    'message': _('Successfully created:\n- Product Template: %s\n- Project Template: %s\n- %d Task Templates\n- Workflow Template: %s') % (
                        product_template.name, project_template.name, len(task_templates), workflow_template.name
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise ValidationError(_('Error creating workflow template: %s') % str(e))

    def _create_product_template(self):
        """Create or use existing product template"""
        if self.use_existing_product and self.existing_product_template_id:
            # Use existing product template
            return self.existing_product_template_id
        else:
            # Create new product template
            if not self.product_name:
                raise ValidationError(_('Product template name is required when not using an existing template.'))
            
            product_vals = {
                'name': self.product_name,
                'description': self.product_description,
                'categ_id': self.product_category.id if self.product_category else False,
                'type': self.product_type,
                'service_tracking': 'project_only',  # Changed from 'task_global_project'
            }
            
            product_template = self.env['product.template'].create(product_vals)
            return product_template

    def _create_project_template(self):
        """Create or use existing project template"""
        if self.use_existing_project and self.existing_project_template_id:
            # Use existing project template
            return self.existing_project_template_id
        else:
            # Create new project template
            if not self.project_name:
                raise ValidationError(_('Project template name is required when not using an existing template.'))
            
            project_vals = {
                'name': self.project_name,
                'description': self.project_description,
                'is_template': True,
                'use_documents': False,  # Templates don't use documents
                'auto_generate_tasks': self.auto_generate_tasks,
                'task_generation_strategy': self.task_generation_strategy,
                'generate_document_tasks': self.task_generation_strategy == 'document_based',
                'generate_progress_tasks': self.task_generation_strategy == 'progress_tracking',
                'generate_milestone_tasks': self.task_generation_strategy == 'milestone',
            }
            
            project_template = self.env['project.project'].create(project_vals)
            return project_template

    def _create_task_templates(self):
        """Create or use existing task templates"""
        if self.use_existing_tasks and self.existing_task_template_ids:
            # Use existing task templates
            return list(self.existing_task_template_ids)
        else:
            # Create new task templates from wizard data
            task_templates = []
            
            for task_wizard in self.task_template_ids:
                task_vals = {
                    'name': task_wizard.name,
                    'template_type': task_wizard.template_type,
                    'document_category': task_wizard.document_category,
                    'task_name_pattern': task_wizard.task_name_pattern,
                    'task_description_pattern': task_wizard.task_description_pattern,
                    'priority': task_wizard.priority,
                    'estimated_hours': task_wizard.estimated_hours,
                    'description': task_wizard.description,
                    'sequence': task_wizard.sequence,
                }
                
                task_template = self.env['project.task.template'].create(task_vals)
                task_templates.append(task_template)
            
            return task_templates

    def _create_checkpoint_templates(self):
        """Create or use existing checkpoint templates"""
        if self.use_existing_checkpoints and self.existing_checkpoint_template_ids:
            # Use existing checkpoint templates
            return list(self.existing_checkpoint_template_ids)
        else:
            # Create new checkpoint templates from wizard data
            checkpoint_templates = []
            
            for checkpoint_wizard in self.checkpoint_template_ids:
                checkpoint_vals = {
                    'name': checkpoint_wizard.name,
                    'description': checkpoint_wizard.description,
                    'checkpoint_type': checkpoint_wizard.checkpoint_type,
                    'is_mandatory': checkpoint_wizard.is_mandatory,
                    'estimated_days': checkpoint_wizard.estimated_days,
                    'sequence': checkpoint_wizard.sequence,
                }
                
                checkpoint_template = self.env['project.checkpoint.template'].create(checkpoint_vals)
                checkpoint_templates.append(checkpoint_template)
            
            return checkpoint_templates

    def _link_templates(self, product_template, project_template, task_templates, checkpoint_templates):
        """Link the created templates together"""
        # Link project template to product template
        if hasattr(product_template, 'project_template_id'):
            product_template.write({
                'project_template_id': project_template.id
            })
        
        # Link task templates to project template
        if task_templates and hasattr(project_template, 'selected_task_template_ids'):
            project_template.write({
                'selected_task_template_ids': [(6, 0, [task.id for task in task_templates])]
            })
        
        # Link checkpoint templates to project template
        if checkpoint_templates and hasattr(project_template, 'checkpoint_template_ids'):
            project_template.write({
                'checkpoint_template_ids': [(6, 0, [checkpoint.id for checkpoint in checkpoint_templates])]
            })

    def _create_workflow_template_record(self, product_template, project_template, task_templates, checkpoint_templates):
        """Create a workflow template record"""
        # Get product name
        if self.use_existing_product and self.existing_product_template_id:
            product_name = self.existing_product_template_id.name
        else:
            product_name = self.product_name or 'Unnamed Product'
        
        # Get project name
        if self.use_existing_project and self.existing_project_template_id:
            project_name = self.existing_project_template_id.name
        else:
            project_name = self.project_name or 'Unnamed Project'
        
        workflow_vals = {
            'name': f"Workflow: {product_name}",
            'description': f"Workflow template for {product_name}",
            'product_name': product_name,
            'product_description': self.product_description,
            'product_category_id': self.product_category.id if self.product_category else False,
            'product_type': self.product_type,
            'project_name': project_name,
            'project_description': self.project_description,
            'project_duration': self.project_duration,
            'project_complexity': self.project_complexity,
            'auto_generate_tasks': self.auto_generate_tasks,
            'task_generation_strategy': self.task_generation_strategy,
            'product_template_id': product_template.id,
            'project_template_id': project_template.id,
            'task_template_ids': [(6, 0, [task.id for task in task_templates])],
            'checkpoint_template_ids': [(6, 0, [checkpoint.id for checkpoint in checkpoint_templates])],
        }
        
        workflow_template = self.env['workflow.template'].create(workflow_vals)
        return workflow_template


class WorkflowCheckpointTemplateWizard(models.TransientModel):
    _name = 'workflow.checkpoint.template.wizard'
    _description = 'Workflow Checkpoint Template Wizard'
    _order = 'sequence'

    wizard_id = fields.Many2one('workflow.template.wizard', string='Wizard')
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Checkpoint Name', required=True)
    description = fields.Text('Description')
    checkpoint_type = fields.Selection([
        ('milestone', 'Milestone'),
        ('review', 'Review'),
        ('progress', 'Progress'),
        ('approval', 'Approval'),
        ('delivery', 'Delivery')
    ], string='Checkpoint Type', default='milestone', required=True)
    is_mandatory = fields.Boolean('Mandatory', default=True)
    estimated_days = fields.Integer('Estimated Days', default=1)


class WorkflowTaskTemplateWizard(models.TransientModel):
    _name = 'workflow.task.template.wizard'
    _description = 'Workflow Task Template Wizard'
    _order = 'sequence'

    wizard_id = fields.Many2one('workflow.template.wizard', string='Wizard', required=True, ondelete='cascade')
    
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Task Name', required=True)
    template_type = fields.Selection([
        ('document_based', 'Document-Based'),
        ('progress_tracking', 'Progress Tracking'),
        ('milestone', 'Milestone'),
        ('custom', 'Custom')
    ], string='Template Type', required=True, default='document_based')
    
    document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance'),
        ('all', 'All Documents')
    ], string='Document Category', default='all')
    
    task_name_pattern = fields.Char('Task Name Pattern', 
                                   help='Pattern for task names. Use {category}, {count}, {project} as placeholders')
    task_description_pattern = fields.Text('Task Description Pattern',
                                          help='Pattern for task descriptions. Use {category}, {count}, {project} as placeholders')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    
    estimated_hours = fields.Float('Estimated Hours', default=8.0)
    description = fields.Text('Description')
