from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _valid_field_parameter(self, field, name):
        return name in ('tracking',) or super()._valid_field_parameter(field, name)

    # Compliance Integration
    compliance_shareholder_ids = fields.One2many('res.partner.business.shareholder', 'partner_id', string='Compliance Shareholders')
    compliance_shareholder_count = fields.Integer(compute='_compute_compliance_shareholder_count', string='Compliance Shareholders Count')
    
    @api.depends('compliance_shareholder_ids')
    def _compute_compliance_shareholder_count(self):
        for record in self:
            record.compliance_shareholder_count = len(record.compliance_shareholder_ids)
    
    def action_view_compliance_shareholders(self):
        """Smart button to view compliance shareholders for this partner"""
        self.ensure_one()
        action = self.env.ref('project_compliance.action_business_shareholder').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {
            'default_partner_id': self.id,
        }
        return action
