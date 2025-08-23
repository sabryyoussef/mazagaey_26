from odoo import models, fields, api, _


class ProjectTaskCheckpoint(models.Model):
    _inherit = 'project.task.checkpoint'

    # Handover integration
    handover_notes_ids = fields.Many2many('project.handover.notes', string='Related Handovers')
    requires_handover = fields.Boolean('Requires Handover', default=False, tracking=True)
    handover_template_id = fields.Many2one('project.project', string='Handover Template', tracking=True, domain=[('is_template', '=', True)])
    
    # Computed fields
    handover_count = fields.Integer(compute='_compute_handover_count', store=True)
    handover_status = fields.Selection([
        ('no_handover', 'No Handover'),
        ('draft', 'Draft'),
        ('complete', 'Complete'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('updated', 'Updated'),
    ], compute='_compute_handover_status', store=True)
    
    @api.depends('handover_notes_ids')
    def _compute_handover_count(self):
        for record in self:
            record.handover_count = len(record.handover_notes_ids)
    
    @api.depends('handover_notes_ids.handover_status')
    def _compute_handover_status(self):
        for record in self:
            if not record.handover_notes_ids:
                record.handover_status = 'no_handover'
            elif any(h.handover_status == 'confirmed' for h in record.handover_notes_ids):
                record.handover_status = 'confirmed'
            elif any(h.handover_status == 'complete' for h in record.handover_notes_ids):
                record.handover_status = 'complete'
            elif any(h.handover_status == 'returned' for h in record.handover_notes_ids):
                record.handover_status = 'returned'
            else:
                record.handover_status = 'draft'
    
    def action_create_handover(self):
        """Create handover from checkpoint"""
        self.ensure_one()
        if not self.requires_handover:
            return False
            
        handover_vals = {
            'project_id': self.task_id.project_id.id if self.task_id else False,
            'template_id': self.handover_template_id.id if self.handover_template_id else False,
            'checkpoint_ids': [(4, self.id)],
        }
        
        handover = self.env['project.handover.notes'].create(handover_vals)
        
        return {
            'name': _('Handover Notes'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.handover.notes',
            'res_id': handover.id,
            'target': 'current',
        }
    
    def action_view_handovers(self):
        """View related handovers"""
        self.ensure_one()
        action = self.env.ref('project_handover_notes.action_project_handover_notes').read()[0]
        action['domain'] = [('checkpoint_ids', 'in', self.id)]
        action['context'] = {
            'default_project_id': self.task_id.project_id.id if self.task_id else False,
            'default_checkpoint_ids': [(4, self.id)],
        }
        return action
