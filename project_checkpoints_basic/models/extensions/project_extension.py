# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Quotation Integration
    create_quotation_on_completion = fields.Boolean(
        string='Create Quotation on Completion',
        default=False,
        help='Automatically create a quotation when this project is completed'
    )
    quotation_template_id = fields.Many2one(
        'sale.order.template',
        string='Quotation Template',
        help='Template to use when creating quotation from this project',
        ondelete='set null',
        required=False
    )
    quotation_notes = fields.Text(
        string='Quotation Notes',
        help='Additional notes to include in the quotation'
    )
    
    # Project completion tracking
    is_completed = fields.Boolean(
        string='Project Completed',
        compute='_compute_project_completion',
        store=False,
        help='Indicates if the project is completed'
    )
    
    @api.depends('tasks', 'tasks.stage_id')
    def _compute_project_completion(self):
        """Compute if project is completed based on task stages"""
        for project in self:
            if not project.tasks:
                project.is_completed = False
                continue
            
            # Check if all tasks are in completion stages
            completion_stages = ['done', 'completed', 'finished', 'closed']
            all_tasks_completed = all(
                task.stage_id.name.lower() in completion_stages 
                for task in project.tasks
            )
            
            project.is_completed = all_tasks_completed
    
    def write(self, vals):
        """Override write to handle project completion quotation creation"""
        result = super().write(vals)
        
        # Check if project completion should trigger quotation
        for project in self:
            if project.is_completed and project.create_quotation_on_completion:
                project._create_quotation_on_completion()
        
        return result
    
    def _create_quotation_on_completion(self):
        """Create quotation when project is completed"""
        self.ensure_one()
        
        # Find the workflow instance for this project
        workflow_instance = None
        if 'fsm.workflow.instance' in self.env:
            workflow_instance = self.env['fsm.workflow.instance'].search([
                ('project_id', '=', self.id)
            ], limit=1)
        
        if not workflow_instance:
            _logger.warning(f"No workflow instance found for project {self.name} - FSM workflow module may not be installed")
            return False
        
        # Create context for quotation creation
        context = {
            'default_workflow_instance_id': workflow_instance.id,
            'project_trigger': True,
            'project_name': self.name,
        }
        
        # Create quotation using workflow instance method
        sale_order = workflow_instance.with_context(context).create_milestone_quotation(
            milestone_name=None,
            checkpoint_name=None,
            task_name=None
        )
        
        if sale_order:
            # Update quotation name to reflect project completion
            sale_order.name = f'Project Quotation - {self.name} - {workflow_instance.name}'
            
            # Add project notes if available
            if self.quotation_notes:
                sale_order.message_post(
                    body=f"📝 **Project Notes**: {self.quotation_notes}",
                    subject=f"Project Notes - {self.name}"
                )
            
            # Apply quotation template if available
            if self.quotation_template_id and 'sale.order.template' in self.env:
                try:
                    if hasattr(self.quotation_template_id, '_generate_quotation_lines'):
                        self.quotation_template_id._generate_quotation_lines(sale_order)
                    else:
                        for line in self.quotation_template_id.sale_order_template_line_ids:
                            self.env['sale.order.line'].create({
                                'order_id': sale_order.id,
                                'name': line.name,
                                'product_id': line.product_id.id if line.product_id else False,
                                'product_uom_qty': line.product_uom_qty,
                                'price_unit': line.price_unit,
                            })
                except Exception as e:
                    _logger.error(f"Error applying quotation template: {e}")
                    # Fallback: create a basic line
                    try:
                        self.env['sale.order.line'].create({
                            'order_id': sale_order.id,
                            'name': f'Project: {self.name}',
                            'product_uom_qty': 1.0,
                            'price_unit': 2000.0,
                        })
                    except Exception as fallback_error:
                        _logger.error(f"Error in fallback template application: {fallback_error}")
            
            _logger.info(f"Quotation created for project {self.name}: {sale_order.name}")
            return sale_order
        
        return False
