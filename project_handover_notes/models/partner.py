from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Handover Notes Integration
    handover_notes_ids = fields.One2many('project.handover.notes', 'hand_partner_id', string='Handover Notes')
    handover_notes_count = fields.Integer(compute='_compute_handover_notes_count', string='Handover Notes Count')
    
    # Additional fields for handover functionality
    hand_legal_type = fields.Selection([
        ('fzco', 'FZCO'),
        ('fze', 'FZE'),
        ('llc', 'LLC'),
    ], string='Legal Entity/Type')
    
    hand_legal_type_id = fields.Many2one('hand.legal.type', string='Legal Entity/Type', ondelete='set null')
    visa_eligibility = fields.Float(string='Visa Eligibility')
    hand_country_ids = fields.Many2many('res.country', string='Top 5 Countries of Operation')
    channel_plan_id = fields.Many2one('channel.partner.plan', string='Channel Partner Plan', ondelete='set null')
    
    @api.depends('handover_notes_ids')
    def _compute_handover_notes_count(self):
        for record in self:
            record.handover_notes_count = len(record.handover_notes_ids)
    
    def action_view_handover_notes(self):
        """Smart button to view handover notes for this partner"""
        self.ensure_one()
        action = self.env.ref('project_handover_notes.action_project_handover_notes').read()[0]
        action['domain'] = [('hand_partner_id', '=', self.id)]
        action['context'] = {
            'default_hand_partner_id': self.id,
        }
        return action
