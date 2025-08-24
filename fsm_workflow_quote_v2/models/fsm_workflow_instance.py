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
