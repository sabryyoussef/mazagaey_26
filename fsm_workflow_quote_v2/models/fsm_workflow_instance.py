# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class FSMWorkflowInstance(models.Model):
    _name = 'fsm.workflow.instance'
    _description = 'FSM Workflow Instance'
    _order = 'create_date desc'

    name = fields.Char(string='Workflow Name', required=True, copy=False, readonly=True, 
                      default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, 
                                ondelete='restrict', copy=False)
    template_id = fields.Many2one('workflow.template', string='Workflow Template', 
                                 ondelete='set null', copy=False)
    
    # Project Integration
    project_id = fields.Many2one('project.project', string='Project', ondelete='set null', copy=False)
    timesheet_hours = fields.Float(string='Timesheet Hours', compute='_compute_hours', store=True)
    
    # FSM Integration (Optional)
    fsm_order_id = fields.Char(string='FSM Order Reference', 
                              help='FSM order reference if FSM module is installed')
    
    # Sales Integration
    sale_order_id = fields.Many2one('sale.order', string='Quotation', ondelete='set null', copy=False)
    quotation_state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Quotation Status', related='sale_order_id.state', store=True, readonly=True)
    quotation_amount = fields.Monetary(string='Quotation Amount', related='sale_order_id.amount_total', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='sale_order_id.currency_id', readonly=True)
    
    # Checkpoint Integration (Optional) - Temporarily disabled to fix loading issues
    # checkpoint_ids = fields.One2many('project.task.checkpoint', 'compliance_project_id', 
    #                                 string='Checkpoints', readonly=True)
    total_checkpoints = fields.Integer(string='Total Checkpoints', default=0)
    completed_checkpoints = fields.Integer(string='Completed Checkpoints', default=0)
    checkpoint_progress = fields.Float(string='Checkpoint Progress (%)', default=0.0)
    
    # Quotation Details
    pricing_policy = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('time_material', 'Time & Material'),
        ('hourly', 'Hourly Rate'),
    ], string='Pricing Policy', default='fixed', required=True)
    estimated_hours = fields.Float(string='Estimated Hours', default=0.0)
    hourly_rate = fields.Monetary(string='Hourly Rate', default=0.0)
    fixed_price = fields.Monetary(string='Fixed Price', default=0.0)
    
    # System Fields
    active = fields.Boolean(default=True)
    create_date = fields.Datetime(string='Created on', readonly=True)
    write_date = fields.Datetime(string='Last Updated on', readonly=True)
    
    # Workflow State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Workflow State', default='draft', required=True)

    def create(self, vals_list):
        """Override create to set automatic sequence"""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fsm.workflow.instance') or _('New')
        
        return super(FSMWorkflowInstance, self).create(vals_list)

    @api.depends('project_id.timesheet_ids.unit_amount')
    def _compute_hours(self):
        for record in self:
            if record.project_id:
                try:
                    timesheet_data = self.env['account.analytic.line'].read_group(
                        [('project_id', '=', record.project_id.id)],
                        ['unit_amount:sum'],
                        ['project_id']
                    )
                    record.timesheet_hours = timesheet_data[0]['unit_amount'] if timesheet_data else 0.0
                except Exception as e:
                    _logger.warning(f"Error computing timesheet hours for workflow {record.id}: {e}")
                    record.timesheet_hours = 0.0
            else:
                record.timesheet_hours = 0.0

    # Temporarily disabled compute method to fix loading issues
    # @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    # def _compute_checkpoint_stats(self):
    #     for record in self:
    #         try:
    #             if record.checkpoint_ids:
    #                 total = len(record.checkpoint_ids)
    #                 completed = len(record.checkpoint_ids.filtered(lambda c: c.is_reached))
    #                 record.total_checkpoints = total
    #                 record.completed_checkpoints = completed
    #                 record.checkpoint_progress = (completed / total * 100) if total > 0 else 0.0
    #             else:
    #                 record.total_checkpoints = 0
    #                 record.completed_checkpoints = 0
    #                 record.checkpoint_progress = 0.0
    #         except Exception as e:
    #             _logger.warning(f"Error computing checkpoint stats for workflow {record.id}: {e}")
    #             record.total_checkpoints = 0
    #             record.completed_checkpoints = 0
    #             record.checkpoint_progress = 0.0

    def action_open_project(self):
        """Open the linked project"""
        self.ensure_one()
        if not self.project_id:
            return {}
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_fsm(self):
        """Open the linked FSM order"""
        self.ensure_one()
        if not self.fsm_order_id or 'fsm.order' not in self.env:
            return {}
        
        try:
            fsm_order = self.env['fsm.order'].search([('name', '=', self.fsm_order_id)], limit=1)
            if fsm_order:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'fsm.order',
                    'res_id': fsm_order.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
        except Exception as e:
            _logger.warning(f"Error opening FSM order: {e}")
        
        return {}

    def action_open_sale(self):
        """Open the linked sale order"""
        self.ensure_one()
        if not self.sale_order_id:
            return {}
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_checkpoints(self):
        """Open checkpoints for this workflow instance"""
        self.ensure_one()
        if not self.project_id or 'project.task.checkpoint' not in self.env:
            return {}
        
        try:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task.checkpoint',
                'view_mode': 'list,form',
                'domain': [('compliance_project_id', '=', self.project_id.id)],
                'context': {'default_compliance_project_id': self.project_id.id},
                'target': 'current',
            }
        except Exception as e:
            _logger.warning(f"Error opening checkpoints: {e}")
            return {}

    def action_create_checkpoint(self):
        """Create a new checkpoint for this workflow instance"""
        self.ensure_one()
        if not self.project_id or 'project.task.checkpoint' not in self.env:
            return {}
        
        try:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task.checkpoint',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_compliance_project_id': self.project_id.id,
                    'default_name': 'New Checkpoint',
                },
            }
        except Exception as e:
            _logger.warning(f"Error creating checkpoint: {e}")
            return {}

    def action_create_handover(self):
        """Create handover notes for this workflow instance"""
        self.ensure_one()
        if not self.project_id or not self.partner_id:
            return {}
        
        # Check if project_handover_notes module is available
        if 'project.handover.notes' not in self.env:
            return {}
        
        try:
            return {
                'name': _('Create Handover Notes'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'project.handover.notes',
                'context': {
                    'default_project_id': self.project_id.id,
                    'default_hand_partner_id': self.partner_id.id,
                    'default_name': f'Handover - {self.name}',
                },
                'target': 'new',
            }
        except Exception:
            return {}

    def action_create_quotation(self):
        """Create a quotation from this workflow instance"""
        self.ensure_one()
        if self.sale_order_id:
            return self.action_open_sale()
        
        # Create sale order
        sale_order_vals = {
            'partner_id': self.partner_id.id,
            'project_id': self.project_id.id if self.project_id else False,
            'origin': self.name,
            'note': f'Generated from FSM Workflow: {self.name}',
        }
        
        sale_order = self.env['sale.order'].create(sale_order_vals)
        
        # Add quotation lines based on template and pricing policy
        if self.template_id:
            self._create_quotation_lines_from_template(sale_order)
        else:
            self._create_default_quotation_line(sale_order)
        
        # Update workflow instance
        self.sale_order_id = sale_order.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

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
            'name': f'Workflow Services - {self.name}',
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

    def action_send_quotation(self):
        """Send quotation to customer"""
        self.ensure_one()
        if not self.sale_order_id:
            return self.action_create_quotation()
        
        return self.sale_order_id.action_quotation_send()

    def action_confirm_quotation(self):
        """Confirm quotation and create sales order"""
        self.ensure_one()
        if not self.sale_order_id:
            return self.action_create_quotation()
        
        return self.sale_order_id.action_confirm()

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Update fields when template changes"""
        if self.template_id:
            self.name = f"{self.template_id.name} - {self.partner_id.name if self.partner_id else 'New'}"
            
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
