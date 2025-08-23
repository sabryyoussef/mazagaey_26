from odoo import models, fields, api, _


class ReturnComplianceWizard(models.TransientModel):
    _name = 'return.compliance.wizard'
    _description = 'Return Compliance Wizard'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    return_reason = fields.Text(string='Return Reason', required=True)
    
    def action_return_compliance(self):
        """Return the compliance with the specified reason"""
        self.ensure_one()
        
        if self.project_id:
            self.project_id.is_complete_return_compliance = True
            self.project_id.message_post(
                body=_("Compliance Returned. Reason: %s") % self.return_reason
            )
            
            # Notify project manager
            if self.project_id.user_id:
                self.project_id.message_post(
                    body=_("Compliance for project %s has been returned. Reason: %s") % (
                        self.project_id.name, self.return_reason
                    ),
                    partner_ids=[(4, self.project_id.user_id.partner_id.id)]
                )
        
        return {'type': 'ir.actions.act_window_close'}
