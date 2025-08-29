# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FSMWorkflowCreateWizard(models.TransientModel):
    _name = 'fsm.workflow.create.wizard'
    _description = 'Create FSM + Project from Workflow Template'

    # Mode selection
    creation_mode = fields.Selection([
        ('existing', 'Use Existing Template'),
        ('create', 'Create New Template'),
    ], string='Creation Mode', default='existing', required=True)
    
    # Existing template fields
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    template_id = fields.Many2one('workflow.template', string='Workflow Template', required=False)
    project_name = fields.Char(string='Project Name', required=True)
    pricing_policy = fields.Selection([
        ('tm', 'Time & Materials'),
        ('fixed', 'Fixed Price'),
        ('hybrid', 'Hybrid'),
    ], string='Pricing Policy', default='tm', required=True)
    
    # New template creation fields
    template_name = fields.Char(string='Template Name')
    template_description = fields.Text(string='Template Description')
    template_category = fields.Selection([
        ('fsm', 'Field Service'),
        ('project', 'Project Management'),
        ('maintenance', 'Maintenance'),
        ('installation', 'Installation'),
        ('other', 'Other'),
    ], string='Template Category', default='fsm')
    
    # These fields are kept for potential future use but not displayed in the UI
    include_task_templates = fields.Boolean(string='Include Task Templates', default=True)
    include_milestone_templates = fields.Boolean(string='Include Milestone Templates', default=True)
    include_checkpoint_templates = fields.Boolean(string='Include Checkpoint Templates', default=True)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Auto-fill project name based on template"""
        if self.template_id and not self.project_name:
            self.project_name = f"{self.template_id.name} - {self.partner_id.name if self.partner_id else 'New Project'}"
    
    @api.onchange('creation_mode')
    def _onchange_creation_mode(self):
        """Clear fields when switching modes"""
        if self.creation_mode == 'create':
            self.template_id = False
        else:
            self.template_name = False
            self.template_description = False
    
    @api.onchange('template_name', 'partner_id')
    def _onchange_template_name(self):
        """Auto-fill project name based on template name"""
        if self.creation_mode == 'create' and self.template_name and not self.project_name:
            self.project_name = f"{self.template_name} - {self.partner_id.name if self.partner_id else 'New Project'}"
    
    def action_create_template(self):
        """Open workflow template creation wizard"""
        self.ensure_one()
        
        # Prepare context with default values from FSM wizard
        context = {
            'default_product_name': self.template_name or f'FSM Template - {self.partner_id.name if self.partner_id else "New"}',
            'default_product_description': self.template_description or 'FSM workflow template created from wizard',
            'default_product_category': self.template_category,
            'default_workflow_name': self.template_name or f'FSM Workflow - {self.partner_id.name if self.partner_id else "New"}',
            'default_workflow_description': self.template_description or 'FSM workflow template',
            'fsm_wizard_id': self.id,  # Pass FSM wizard ID for callback
            'is_fsm_template': True,  # Flag to indicate this is from FSM
        }
        
        # Open the comprehensive workflow template creation wizard
        return {
            'name': _('Create Workflow Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
    
    def action_template_created_callback(self, template_id):
        """Callback when template is created from the workflow template wizard"""
        self.ensure_one()
        
        # Set the created template as selected and switch to existing mode
        self.write({
            'template_id': template_id,
            'creation_mode': 'existing',
        })
        
        # Return action to reopen this wizard with the template selected
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create FSM from Workflow Template'),
            'res_model': 'fsm.workflow.create.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'template_created_success': True,
                'created_template_id': template_id,
            }
        }

    def action_create(self):
        """Create FSM workflow instance from template"""
        self.ensure_one()
        
        # Create project
        project_vals = {
            'name': self.project_name,
            'allow_timesheets': True,
            'partner_id': self.partner_id.id,
        }
        project = self.env['project.project'].create(project_vals)

        # Create FSM order if the model exists (optional)
        fsm_order_ref = None
        if 'fsm.order' in self.env:
            try:
                fsm_vals = {
                    'name': self.project_name,
                    'partner_id': self.partner_id.id,
                }
                fsm_order = self.env['fsm.order'].create(fsm_vals)
                fsm_order_ref = fsm_order.name
            except Exception:
                # FSM order creation failed, continue without it
                pass

        # Generate tasks from template if available
        if self.template_id:
            try:
                # Use the task generation service from project_templates_basic
                service = self.env['project.task.generation.service'].sudo()
                task_templates = self.template_id.selected_task_template_ids or self.template_id.task_template_ids
                if task_templates:
                    service.generate_tasks_from_project_template(project, task_templates, options=None)
            except Exception:
                # Task generation failed, continue without tasks
                pass

        # Create checkpoints from template if available
        if self.template_id:
            try:
                # Look for checkpoint templates associated with the workflow template
                checkpoint_templates = self.env['project.task.checkpoint.template'].search([
                    ('name', 'ilike', self.template_id.name)
                ])
                
                for checkpoint_template in checkpoint_templates:
                    # Create checkpoints for the project
                    for line in checkpoint_template.line_ids:
                        self.env['project.task.checkpoint'].create({
                            'name': line.name,
                            'compliance_project_id': project.id,
                            'sequence': line.sequence,
                            'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                            'notes': line.notes or '',
                        })
            except Exception:
                # Checkpoint creation failed, continue without checkpoints
                pass

        # Create workflow instance
        template_name = self.template_id.name if self.template_id else 'No Template'
        instance = self.env['fsm.workflow.instance'].create({
            'name': f'{template_name} / {self.project_name}',
            'template_id': self.template_id.id if self.template_id else False,
            'project_id': project.id,
            'partner_id': self.partner_id.id,
            'fsm_order_id': fsm_order_ref,
            'pricing_policy': self.pricing_policy,
            'state': 'running',
        })

        # Link project to instance (if field exists)
        try:
            project.write({'fsm_workflow_instance_id': instance.id})
        except Exception:
            # Field might not exist, ignore
            pass

        # Return action to open the created instance
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.workflow.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'target': 'current',
        }
