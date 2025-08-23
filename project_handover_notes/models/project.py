from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.project'

    # Handover Notes Integration

    # Integration Fields
    handover_template_id = fields.Many2one('project.project', string='Default Handover Template', tracking=True, domain=[('is_template', '=', True)])
    handover_checkpoint_ids = fields.Many2many('project.task.checkpoint', string='Handover Checkpoints', tracking=True)
    
    # Integration Computed Fields
    handover_status = fields.Selection([
        ('no_handover', 'No Handover'),
        ('draft', 'Draft'),
        ('complete', 'Complete'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('updated', 'Updated'),
    ], compute='_compute_handover_status', store=True)
    pending_handovers = fields.Integer(compute='_compute_pending_handovers', store=True)
    handover_notes_ids = fields.One2many('project.handover.notes', 'project_id', string='Handover Notes')
    handover_notes_count = fields.Integer(compute='_compute_handover_notes_count', string='Handover Notes Count')
    
    # Legacy handover fields for backward compatibility
    is_complete_hand = fields.Boolean(string="Handover Complete", copy=False)
    is_confirm_hand = fields.Boolean(string="Handover Confirm", copy=False)
    is_complete_return_hand = fields.Boolean(string="Handover Returned", copy=False)
    is_update_hand = fields.Boolean(string="Update Handover", copy=False)
    is_second_complete_hand_check = fields.Integer(string="Second Complete Handover Check", copy=False, default=0)
    
    # Computed fields for UI
    is_update_hand_check = fields.Boolean(compute='_compute_is_update_hand_check', store=False)
    is_current_user_project_manager = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_admin = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_task_assignee = fields.Boolean(compute='_compute_user_permissions', store=False)
    
    @api.depends('handover_notes_ids')
    def _compute_handover_notes_count(self):
        for record in self:
            record.handover_notes_count = len(record.handover_notes_ids)
    
    @api.depends('is_complete_return_hand', 'is_complete_hand', 'is_confirm_hand')
    def _compute_is_update_hand_check(self):
        for record in self:
            if (record.is_complete_return_hand and 
                not record.is_complete_hand and 
                not record.is_confirm_hand and
                (record.is_current_user_project_manager or record.is_current_user_project_admin)):
                record.is_update_hand_check = True
            else:
                record.is_update_hand_check = False
    
    def _compute_user_permissions(self):
        current_user = self.env.user
        for record in self:
            record.is_current_user_project_manager = record.user_id == current_user
            record.is_current_user_project_admin = current_user.has_group('project.group_project_manager')
            # Check if current user is assigned to any tasks in this project
            task_users = record.task_ids.mapped('user_ids')
            record.is_current_user_project_task_assignee = current_user in task_users if task_users else False
    
    def action_view_handover_notes(self):
        """Smart button to view handover notes"""
        self.ensure_one()
        action = self.env.ref('project_handover_notes.action_project_handover_notes').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'default_hand_partner_id': self.partner_id.id if self.partner_id else False,
        }
        return action
    
    def action_create_handover_notes(self):
        """Create new handover notes for the project"""
        self.ensure_one()
        return {
            'name': _('Create Handover Notes'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.handover.notes',
            'context': {
                'default_project_id': self.id,
                'default_hand_partner_id': self.partner_id.id if self.partner_id else False,
            },
            'target': 'new',
        }
    
    # Legacy action methods for backward compatibility
    def action_complete_hand(self):
        """Legacy method - now delegates to handover notes"""
        self.ensure_one()
        if not self.handover_notes_ids:
            # Create a new handover note if none exists
            handover_note = self.env['project.handover.notes'].create({
                'project_id': self.id,
                'hand_partner_id': self.partner_id.id if self.partner_id else False,
            })
        else:
            handover_note = self.handover_notes_ids[0]
        
        return handover_note.action_complete_hand()
    
    def action_confirm_hand(self):
        """Legacy method - now delegates to handover notes"""
        self.ensure_one()
        if self.handover_notes_ids:
            return self.handover_notes_ids[0].action_confirm_hand()
        return False
    
    def action_return_hand(self):
        """Legacy method - now delegates to handover notes"""
        self.ensure_one()
        if self.handover_notes_ids:
            return self.handover_notes_ids[0].action_return_hand()
        return False
    
    def action_update_hand(self):
        """Legacy method - now delegates to handover notes"""
        self.ensure_one()
        if self.handover_notes_ids:
            return self.handover_notes_ids[0].action_update_hand()
        return False
    
    def action_repeat_hand(self):
        """Legacy method - now delegates to handover notes"""
        self.ensure_one()
        if self.handover_notes_ids:
            return self.handover_notes_ids[0].action_repeat_hand()
        return False

    @api.depends("handover_notes_ids.handover_status")
    def _compute_handover_status(self):
        for record in self:
            if not record.handover_notes_ids:
                record.handover_status = "no_handover"
            elif any(h.handover_status == "confirmed" for h in record.handover_notes_ids):
                record.handover_status = "confirmed"
            elif any(h.handover_status == "complete" for h in record.handover_notes_ids):
                record.handover_status = "complete"
            elif any(h.handover_status == "returned" for h in record.handover_notes_ids):
                record.handover_status = "returned"
            else:
                record.handover_status = "draft"
    
    @api.depends("handover_notes_ids.handover_status")
    def _compute_pending_handovers(self):
        for record in self:
            pending = record.handover_notes_ids.filtered(lambda h: h.handover_status in ["draft", "complete"])
            record.pending_handovers = len(pending)
    
    def create_handover_from_checkpoint(self, checkpoint_id):
        """Create handover from checkpoint completion"""
        checkpoint = self.env["project.checkpoint"].browse(checkpoint_id)
        if checkpoint.requires_handover and checkpoint.handover_template_id:
            handover_vals = {
                "project_id": self.id,
                "template_id": checkpoint.handover_template_id.id,
                "checkpoint_ids": [(4, checkpoint_id)],
            }
            return self.env["project.handover.notes"].create(handover_vals)
