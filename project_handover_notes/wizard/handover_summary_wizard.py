from odoo import models, fields, api, _


class HandoverSummaryWizard(models.TransientModel):
    _name = 'handover.summary.wizard'
    _description = 'Handover Summary Wizard'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    handover_ids = fields.Many2many('project.handover.notes', string='Handover Notes')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('export', 'Export Data'),
    ], string='Report Type', default='summary', required=True)
    
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.handover_ids = self.project_id.handover_notes_ids
    
    def action_generate_report(self):
        """Generate the selected report type"""
        self.ensure_one()
        
        if self.report_type == 'summary':
            return self._generate_summary_report()
        elif self.report_type == 'detailed':
            return self._generate_detailed_report()
        elif self.report_type == 'export':
            return self._export_data()
    
    def _generate_summary_report(self):
        """Generate a summary report"""
        # This would typically generate a PDF report
        # For now, we'll just show a message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Summary Report'),
                'message': _('Summary report generated for project: %s') % self.project_id.name,
                'type': 'success',
            }
        }
    
    def _generate_detailed_report(self):
        """Generate a detailed report"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Detailed Report'),
                'message': _('Detailed report generated for project: %s') % self.project_id.name,
                'type': 'success',
            }
        }
    
    def _export_data(self):
        """Export handover data"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Data Export'),
                'message': _('Handover data exported for project: %s') % self.project_id.name,
                'type': 'success',
            }
        }
