from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    # Compliance fields
    compliance_shareholder_ids = fields.One2many(
        'res.partner.business.shareholder', 'project_id', string='Compliance Shareholders'
    )
    compliance_shareholder_count = fields.Integer(
        compute='_compute_compliance_shareholder_count', string='Compliance Shareholders Count'
    )
    
    # Compliance status fields
    is_complete_return_compliance = fields.Boolean(string="Compliance Complete", copy=False, tracking=True)
    is_confirm_compliance = fields.Boolean(string="Compliance Confirm", copy=False, tracking=True)
    is_update_compliance = fields.Boolean(string="Update Compliance", copy=False, tracking=True)
    is_complete_compliance = fields.Boolean(string="Complete Compliance", copy=False, tracking=True)
    is_second_complete_compliance_check = fields.Integer(
        string="Second Complete Compliance Check", copy=False, default=0, tracking=True
    )
    
    # Computed fields for UI
    is_update_compliance_check = fields.Boolean(compute='_compute_is_update_compliance_check', store=False)
    is_current_user_project_manager = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_admin = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_task_assignee = fields.Boolean(compute='_compute_user_permissions', store=False)
    
    # Shareholding total
    shareholding_total = fields.Float(compute='_compute_shareholding_total', string='Total Shareholding (%)')

    @api.depends('compliance_shareholder_ids')
    def _compute_compliance_shareholder_count(self):
        for record in self:
            record.compliance_shareholder_count = len(record.compliance_shareholder_ids)

    @api.depends('compliance_shareholder_ids.shareholding')
    def _compute_shareholding_total(self):
        for record in self:
            total = sum(record.compliance_shareholder_ids.mapped('shareholding'))
            record.shareholding_total = total

    @api.depends('is_complete_return_compliance', 'is_complete_compliance', 'is_confirm_compliance')
    def _compute_is_update_compliance_check(self):
        for record in self:
            try:
                if (record.is_complete_return_compliance and 
                    not record.is_complete_compliance and 
                    not record.is_confirm_compliance and
                    (record.is_current_user_project_manager or record.is_current_user_project_admin)):
                    record.is_update_compliance_check = True
                else:
                    record.is_update_compliance_check = False
            except Exception:
                record.is_update_compliance_check = False

    def _compute_user_permissions(self):
        current_user = self.env.user
        for record in self:
            try:
                record.is_current_user_project_manager = record.user_id == current_user if record.user_id else False
                record.is_current_user_project_admin = current_user.has_group('project.group_project_manager')
                # Check if current user is assigned to any tasks in this project
                if record.task_ids:
                    task_users = record.task_ids.mapped('user_ids')
                    record.is_current_user_project_task_assignee = current_user in task_users if task_users else False
                else:
                    record.is_current_user_project_task_assignee = False
            except Exception:
                record.is_current_user_project_manager = False
                record.is_current_user_project_admin = False
                record.is_current_user_project_task_assignee = False

    def _check_compliance_shareholder_ids(self):
        """Validate compliance shareholder data"""
        for record in self:
            if record.compliance_shareholder_ids:
                # Filter out shareholders with no shareholding value
                shareholders_with_shareholding = record.compliance_shareholder_ids.filtered(lambda s: s.shareholding and s.shareholding > 0)
                
                if not shareholders_with_shareholding:
                    raise UserError(_('Please set shareholding percentages for compliance shareholders.'))
                
                total_shareholding = sum(shareholders_with_shareholding.mapped('shareholding'))
                if abs(total_shareholding - 100.0) > 0.01:  # Allow small floating point differences
                    raise UserError(_('Total shareholding must equal 100%%. Current total: %.2f%%') % total_shareholding)

    def _check_shareholding(self):
        """Check shareholding totals"""
        for record in self:
            if record.compliance_shareholder_ids:
                record._check_compliance_shareholder_ids()

    # Compliance Action Methods
    def action_complete_compliance(self):
        """Complete compliance process"""
        for record in self:
            if not (record.is_current_user_project_manager or record.is_current_user_project_admin):
                raise UserError(_("Only project managers or admins can complete compliance."))
            
            # Check if there are compliance shareholders
            if not record.compliance_shareholder_ids:
                raise UserError(_("Please add at least one compliance shareholder before completing compliance."))
            
            # Check shareholding validation only if there are shareholders
            try:
                record._check_compliance_shareholder_ids()
                record._check_shareholding()
            except UserError as e:
                raise UserError(_("Compliance validation failed: %s") % str(e))
            except Exception as e:
                raise UserError(_("An error occurred during compliance validation: %s") % str(e))
            
            record.is_complete_compliance = True
            record.message_post(body=_("Compliance Completed"))
            
        return True

    def action_confirm_compliance(self):
        """Confirm compliance"""
        for record in self:
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can confirm compliance."))
            
            record.is_confirm_compliance = True
            record.message_post(body=_("Compliance Confirmed"))
            
        return True

    def action_return_compliance(self):
        """Return compliance for revision"""
        for record in self:
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can return compliance."))
            
            return {
                'name': _('Return Compliance'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'return.compliance.wizard',
                'context': {
                    'default_project_id': record.id,
                },
                'target': 'new',
            }

    def action_update_compliance(self):
        """Update compliance after return"""
        for record in self:
            if not (record.is_current_user_project_manager or record.is_current_user_project_admin):
                raise UserError(_("Only project managers or admins can update compliance."))
            
            record.is_complete_return_compliance = False
            record.is_complete_compliance = True
            record.is_second_complete_compliance_check = 2
            record._check_compliance_shareholder_ids()
            record.message_post(body=_("Compliance Updated"))
            
        return True

    def action_repeat_compliance(self):
        """Repeat compliance process"""
        for record in self:
            if not record.is_current_user_project_admin:
                raise UserError(_("Only admins can repeat compliance."))
            
            record.is_complete_compliance = False
            record.is_confirm_compliance = False
            record.is_complete_return_compliance = False
            record.is_update_compliance = False
            record.is_second_complete_compliance_check = 0
            record.message_post(body=_("Compliance Process Repeated"))
            
        return True

    def action_view_compliance_shareholders(self):
        """Smart button to view compliance shareholders"""
        self.ensure_one()
        action = self.env.ref('project_compliance.action_business_shareholder').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id if self.partner_id else False,
        }
        return action
