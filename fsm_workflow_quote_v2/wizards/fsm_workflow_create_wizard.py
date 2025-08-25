# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class FSMWorkflowCreateWizard(models.TransientModel):
    _name = 'fsm.workflow.create.wizard'
    _description = 'FSM Workflow Creation Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    template_id = fields.Many2one('workflow.template', string='Workflow Template')
    project_name = fields.Char(string='Project Name', required=True)
    
    # Pricing and Quotation
    pricing_policy = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('time_material', 'Time & Material'),
        ('hourly', 'Hourly Rate'),
    ], string='Pricing Policy', default='fixed', required=True)
    estimated_hours = fields.Float(string='Estimated Hours', default=0.0)
    hourly_rate = fields.Monetary(string='Hourly Rate', default=0.0)
    fixed_price = fields.Monetary(string='Fixed Price', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    
    # Quotation Options
    create_quotation = fields.Boolean(string='Create Quotation', default=True)
    quotation_notes = fields.Text(string='Quotation Notes')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Auto-fill project name and pricing from template"""
        if self.template_id:
            self.project_name = self.template_id.name
            
            # Set default pricing based on template
            if hasattr(self.template_id, 'pricing_policy'):
                self.pricing_policy = self.template_id.pricing_policy
            if hasattr(self.template_id, 'estimated_hours'):
                self.estimated_hours = self.template_id.estimated_hours
            if hasattr(self.template_id, 'hourly_rate'):
                self.hourly_rate = self.template_id.hourly_rate
            if hasattr(self.template_id, 'fixed_price'):
                self.fixed_price = self.template_id.fixed_price

    @api.onchange('pricing_policy')
    def _onchange_pricing_policy(self):
        """Update fields when pricing policy changes"""
        if self.pricing_policy == 'fixed':
            self.hourly_rate = 0.0
        elif self.pricing_policy == 'hourly':
            self.fixed_price = 0.0
        elif self.pricing_policy == 'time_material':
            self.fixed_price = 0.0

    def action_create(self):
        """Create workflow instance with project, tasks, and optional quotation"""
        self.ensure_one()
        
        # Create project
        project_vals = {
            'name': self.project_name,
            'partner_id': self.partner_id.id,
            'user_id': self.env.user.id,
        }
        project = self.env['project.project'].create(project_vals)
        
        # Create FSM order if FSM module is available
        fsm_order_ref = None
        if 'fsm.order' in self.env:
            try:
                fsm_order = self.env['fsm.order'].create({
                    'name': f'FSM-{self.project_name}',
                    'partner_id': self.partner_id.id,
                    'project_id': project.id,
                })
                fsm_order_ref = fsm_order.name
            except Exception as e:
                _logger.warning(f"Failed to create FSM order: {e}")
                pass
        
        # Generate tasks from template
        if self.template_id and self.template_id.task_template_ids:
            for task_template in self.template_id.task_template_ids:
                # Map priority from template to task (template: 0=Low, 1=Normal, 2=High, 3=Critical)
                # Task: 0=Low, 1=High
                priority_mapping = {
                    '0': '0',  # Low -> Low
                    '1': '0',  # Normal -> Low
                    '2': '1',  # High -> High
                    '3': '1',  # Critical -> High
                }
                task_priority = priority_mapping.get(task_template.priority, '0')
                
                task_vals = {
                    'name': task_template.name,
                    'project_id': project.id,
                    'description': task_template.description or '',
                    'priority': task_priority,
                    'allocated_hours': task_template.estimated_hours,
                }
                self.env['project.task'].create(task_vals)
        
        # Create checkpoints from template if available
        if self.template_id and 'project.task.checkpoint.template' in self.env:
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
                            'project_id': project.id,
                            'sequence': line.sequence,
                            'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                            'notes': line.notes or '',
                        })
            except Exception as e:
                _logger.warning(f"Checkpoint creation failed: {e}")
                # Checkpoint creation failed, continue without checkpoints
                pass
        
        # Create quotation if requested
        sale_order = None
        if self.create_quotation:
            sale_order = self._create_quotation(project)
        
        # Create workflow instance
        template_name = self.template_id.name if self.template_id else 'No Template'
        workflow_vals = {
            'name': f'{template_name} - {self.partner_id.name}',
            'partner_id': self.partner_id.id,
            'template_id': self.template_id.id if self.template_id else False,
            'project_id': project.id,
            'fsm_order_id': fsm_order_ref,
            'sale_order_id': sale_order.id if sale_order else False,
            'pricing_policy': self.pricing_policy,
            'estimated_hours': self.estimated_hours,
            'hourly_rate': self.hourly_rate,
            'fixed_price': self.fixed_price,
            'state': 'in_progress',  # Set initial state
        }
        
        workflow_instance = self.env['fsm.workflow.instance'].create(workflow_vals)
        
        # Return action to open the created workflow instance
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.workflow.instance',
            'res_id': workflow_instance.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_quotation(self, project):
        """Create quotation from workflow template"""
        # Create sale order
        sale_order_vals = {
            'partner_id': self.partner_id.id,
            'project_id': project.id,
            'origin': f'FSM Workflow: {self.project_name}',
            'note': self.quotation_notes or f'Generated from FSM Workflow: {self.project_name}',
        }
        
        sale_order = self.env['sale.order'].create(sale_order_vals)
        
        # Add quotation lines based on template and pricing policy
        if self.template_id:
            self._create_quotation_lines_from_template(sale_order)
        else:
            self._create_default_quotation_line(sale_order)
        
        return sale_order

    def _create_quotation_lines_from_template(self, sale_order):
        """Create quotation lines from workflow template"""
        if not self.template_id:
            return
        
        # Create lines from template tasks
        for task_template in self.template_id.task_template_ids:
            try:
                product = self._get_product_for_task(task_template)
                if product:
                    line_vals = {
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'name': task_template.name,
                        'product_uom_qty': self._calculate_quantity(task_template),
                        'price_unit': self._calculate_price_unit(product, task_template),
                    }
                    self.env['sale.order.line'].create(line_vals)
            except Exception as e:
                _logger.warning(f"Failed to create quotation line for task template {task_template.name}: {e}")
                continue

    def _create_default_quotation_line(self, sale_order):
        """Create a default quotation line"""
        # Get default service product
        default_product = self.env['product.product'].search([
            ('type', '=', 'service'),
            ('sale_ok', '=', True)
        ], limit=1)
        
        if not default_product:
            return
        
        line_vals = {
            'order_id': sale_order.id,
            'product_id': default_product.id,
            'name': f'Workflow Services - {self.project_name}',
            'product_uom_qty': self.estimated_hours or 1.0,
            'price_unit': self.hourly_rate or default_product.list_price,
        }
        self.env['sale.order.line'].create(line_vals)

    def _get_product_for_task(self, task_template):
        """Get appropriate product for task template"""
        # Try to find product by name
        product = self.env['product.product'].search([
            ('name', 'ilike', task_template.name),
            ('type', '=', 'service'),
            ('sale_ok', '=', True)
        ], limit=1)
        
        if not product:
            # Get default service product
            product = self.env['product.product'].search([
                ('type', '=', 'service'),
                ('sale_ok', '=', True)
            ], limit=1)
        
        return product

    def _calculate_quantity(self, task_template):
        """Calculate quantity for quotation line"""
        if self.pricing_policy == 'hourly':
            return self.estimated_hours or 1.0
        elif self.pricing_policy == 'time_material':
            return 1.0  # Time and material typically billed per task
        else:  # fixed
            return 1.0

    def _calculate_price_unit(self, product, task_template):
        """Calculate price unit for quotation line"""
        if self.pricing_policy == 'hourly':
            return self.hourly_rate or product.list_price
        elif self.pricing_policy == 'time_material':
            return product.list_price
        else:  # fixed
            return self.fixed_price or product.list_price
