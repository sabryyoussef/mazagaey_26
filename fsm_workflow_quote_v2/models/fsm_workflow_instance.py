# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class FSMWorkflowInstance(models.Model):
    _name = 'fsm.workflow.instance'
    _description = 'FSM Workflow Instance'
    _order = 'id desc'

    name = fields.Char(required=True, default=lambda self: _('FSM Workflow Instance'))
    project_id = fields.Many2one('project.project', string='Project', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    pricing_policy = fields.Selection([
        ('tm', 'Time & Materials'),
        ('fixed', 'Fixed Price'),
        ('hybrid', 'Hybrid'),
    ], string='Pricing Policy', default='tm', required=True)

    state = fields.Selection([
        ('running', 'Running'),
        ('quoted', 'Quoted'),
        ('closed', 'Closed'),
    ], default='running', string='State')

    sale_order_id = fields.Many2one('sale.order', string='Last Quotation', copy=False)
    timesheet_hours = fields.Float(string='Total Timesheet Hours', compute='_compute_hours', store=False)

    # Optional fields from our modules
    template_id = fields.Many2one('workflow.template', string='Workflow Template', required=False, copy=False)
    fsm_order_id = fields.Char(string='FSM Order Reference', required=False, copy=False, help='Reference to FSM Order (if FSM module is installed)')

    # Checkpoint Integration
    checkpoint_ids = fields.One2many('project.task.checkpoint', 'compliance_project_id', string='Project Checkpoints', domain=[('compliance_project_id', '!=', False)])
    total_checkpoints = fields.Integer(string='Total Checkpoints', compute='_compute_checkpoint_stats', store=False)
    completed_checkpoints = fields.Integer(string='Completed Checkpoints', compute='_compute_checkpoint_stats', store=False)
    checkpoint_progress = fields.Float(string='Checkpoint Progress (%)', compute='_compute_checkpoint_stats', store=False)

    @api.depends('project_id')
    def _compute_hours(self):
        for rec in self:
            if rec.project_id:
                try:
                    aal = self.env['account.analytic.line'].read_group(
                        domain=[('project_id', '=', rec.project_id.id), ('unit_amount', '>', 0)],
                        fields=['unit_amount:sum'],
                        groupby=[]
                    )
                    rec.timesheet_hours = (aal and aal[0].get('unit_amount_sum') or 0.0)
                except:
                    rec.timesheet_hours = 0.0
            else:
                rec.timesheet_hours = 0.0

    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    def _compute_checkpoint_stats(self):
        """Compute checkpoint statistics"""
        for rec in self:
            if rec.checkpoint_ids:
                rec.total_checkpoints = len(rec.checkpoint_ids)
                rec.completed_checkpoints = len(rec.checkpoint_ids.filtered(lambda c: c.is_reached))
                rec.checkpoint_progress = (rec.completed_checkpoints / rec.total_checkpoints * 100) if rec.total_checkpoints > 0 else 0.0
            else:
                rec.total_checkpoints = 0
                rec.completed_checkpoints = 0
                rec.checkpoint_progress = 0.0

    def action_open_project(self):
        self.ensure_one()
        if not self.project_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
        }

    def action_open_fsm(self):
        self.ensure_one()
        if not self.fsm_order_id or 'fsm.order' not in self.env:
            return {}
        # Try to find the FSM order by reference
        try:
            fsm_order = self.env['fsm.order'].search([('name', '=', self.fsm_order_id)], limit=1)
            if fsm_order:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'fsm.order',
                    'res_id': fsm_order.id,
                    'view_mode': 'form',
                }
        except:
            pass
        return {}

    def action_open_sale(self):
        self.ensure_one()
        if not self.sale_order_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
        }

    def action_open_checkpoints(self):
        """Open checkpoints view for this workflow instance"""
        self.ensure_one()
        if not self.checkpoint_ids:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.checkpoint',
            'view_mode': 'list,form',
            'domain': [('compliance_project_id', '=', self.project_id.id)],
            'context': {
                'default_compliance_project_id': self.project_id.id,
                'default_name': 'New Checkpoint',
            },
            'name': f'Checkpoints - {self.name}',
        }

    def action_create_checkpoint(self):
        """Create a new checkpoint for this workflow instance"""
        self.ensure_one()
        if not self.project_id:
            return {}
        
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
        """Create a new quotation for this workflow instance"""
        self.ensure_one()
        if not self.partner_id:
            return {}
        
        return {
            'name': _('Create Quotation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_workflow_instance_id': self.id,
                'default_name': f'Quotation - {self.name}',
            },
            'target': 'new',
        }

    def create_milestone_quotation(self, milestone_name=None, checkpoint_name=None, task_name=None, project_name=None):
        """
        Create a quotation triggered by milestone, checkpoint, task, or project completion
        
        Args:
            milestone_name (str): Name of the milestone that triggered the quotation
            checkpoint_name (str): Name of the checkpoint that triggered the quotation
            task_name (str): Name of the task that triggered the quotation
            project_name (str): Name of the project that triggered the quotation
        """
        self.ensure_one()
        if not self.partner_id:
            return False
        
        # Create quotation name based on trigger
        if milestone_name:
            quotation_name = f'Milestone Quotation - {milestone_name} - {self.name}'
        elif checkpoint_name:
            quotation_name = f'Checkpoint Quotation - {checkpoint_name} - {self.name}'
        elif task_name:
            quotation_name = f'Task Quotation - {task_name} - {self.name}'
        elif project_name:
            quotation_name = f'Project Quotation - {project_name} - {self.name}'
        else:
            quotation_name = f'Workflow Quotation - {self.name}'
        
        # Create the sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'workflow_instance_id': self.id,
            'name': quotation_name,
            'date_order': fields.Datetime.now(),
            'pricelist_id': self.partner_id.property_product_pricelist.id if self.partner_id.property_product_pricelist else False,
        })
        
        # Update the workflow instance with the new quotation
        self.sale_order_id = sale_order.id
        
        # Log the quotation creation
        trigger_type = 'Milestone: ' + milestone_name if milestone_name else 'Checkpoint: ' + checkpoint_name if checkpoint_name else 'Task: ' + task_name if task_name else 'Project: ' + project_name if project_name else 'Manual'
        self.message_post(
            body=f"📋 **Quotation Created**: {quotation_name}<br/>"
                 f"<strong>Trigger:</strong> {trigger_type}<br/>"
                 f"<strong>Quotation:</strong> {sale_order.name}<br/>"
                 f"<strong>Amount:</strong> {sale_order.currency_id.symbol}{sale_order.amount_total:.2f}",
            subject=f"Quotation Created - {quotation_name}"
        )
        
        return sale_order

    def action_open_quotations(self):
        """Open all quotations for this workflow instance"""
        self.ensure_one()
        
        # Find all quotations related to this workflow instance
        quotations = self.env['sale.order'].search([
            ('workflow_instance_id', '=', self.id)
        ])
        
        if not quotations:
            return {}
        
        return {
            'name': _('Workflow Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', quotations.ids)],
            'context': {
                'default_workflow_instance_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
            },
        }
