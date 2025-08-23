from odoo import models, fields, api, _


class ReturnHandoverWizard(models.TransientModel):
    _name = 'return.handover.wizard'
    _description = 'Return Handover Wizard'

    handover_id = fields.Many2one('project.handover.notes', string='Handover Notes', required=True)
    return_reason = fields.Text(string='Return Reason', required=True)
    
    def action_return_handover(self):
        """Return the handover with the specified reason"""
        self.ensure_one()
        
        if self.handover_id:
            self.handover_id.is_complete_return_hand = True
            self.handover_id.handover_status = 'returned'
            self.handover_id.message_post(
                body=_("Handover Returned. Reason: %s") % self.return_reason
            )
            
            # Notify project manager
            if self.handover_id.project_id.user_id:
                self.handover_id.project_id.message_post(
                    body=_("Handover for project %s has been returned. Reason: %s") % (
                        self.handover_id.project_id.name, self.return_reason
                    ),
                    partner_ids=[(4, self.handover_id.project_id.user_id.partner_id.id)]
                )
        
        return {'type': 'ir.actions.act_window_close'}
