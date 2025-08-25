from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    def _valid_field_parameter(self, field, name):
        return name in ('tracking',) or super()._valid_field_parameter(field, name)

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
    
    # Workflow State
    compliance_workflow_state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('updated', 'Updated'),
    ], compute='_compute_compliance_workflow_state', store=True, string='Compliance Workflow State')
    
    # Automation Settings
    auto_create_handover = fields.Boolean(string='Auto Create Handover', default=True, tracking=True)
    auto_copy_documents = fields.Boolean(string='Auto Copy Documents', default=True, tracking=True)
    auto_notify_stakeholders = fields.Boolean(string='Auto Notify Stakeholders', default=True, tracking=True)
    
    # Shareholding total
    shareholding_total = fields.Float(compute='_compute_shareholding_total', string='Total Shareholding (%)')
    
    # Handover Integration - Temporarily disabled to fix loading issues
    # handover_compliance_ids = fields.One2many('project.handover.notes', 'compliance_project_id', string='Compliance Handovers')
    handover_compliance_count = fields.Integer(string='Compliance Handovers Count', default=0)
    
    # Document Integration
    compliance_document_ids = fields.Many2many('ir.attachment', string='Compliance Documents', tracking=True)
    compliance_document_count = fields.Integer(compute='_compute_compliance_document_count', string='Compliance Documents Count')
    
    # Document Automation Integration
    compliance_document_automation_ids = fields.Many2many('unified.document.copy.automation', string='Compliance Document Automations', tracking=True)
    auto_copy_compliance_documents = fields.Boolean(string='Auto Copy Compliance Documents', default=True, tracking=True)
    
    # Template Integration
    compliance_template_id = fields.Many2one('project.project', string='Compliance Template', 
                                           domain=[('is_template', '=', True), ('template_category', '=', 'compliance_services')], 
                                           tracking=True)
    compliance_template_type = fields.Selection(related='compliance_template_id.template_category', readonly=True, store=True)
    compliance_template_description = fields.Text(related='compliance_template_id.template_description', readonly=True)

    # Checkpoint Integration - Temporarily disabled to fix loading issues
    # compliance_checkpoint_ids = fields.One2many(
    #     'project.task.checkpoint',
    #     'compliance_project_id',
    #     string='Compliance Checkpoints',
    #     help='Compliance-specific checkpoints for this project'
    # )
    compliance_checkpoint_count = fields.Integer(
        string='Compliance Checkpoints Count',
        default=0
    )
    compliance_checkpoint_reached_count = fields.Integer(
        string='Reached Compliance Checkpoints Count',
        default=0
    )
    compliance_checkpoint_progress = fields.Float(
        string='Compliance Checkpoint Progress (%)',
        default=0.0
    )

    @api.depends('compliance_shareholder_ids')
    def _compute_compliance_shareholder_count(self):
        for record in self:
            record.compliance_shareholder_count = len(record.compliance_shareholder_ids)

    @api.depends('compliance_shareholder_ids.shareholding')
    def _compute_shareholding_total(self):
        for record in self:
            total = sum(record.compliance_shareholder_ids.mapped('shareholding'))
            record.shareholding_total = total

    # Temporarily disabled compute method to fix loading issues
    # @api.depends('handover_compliance_ids')
    # def _compute_handover_compliance_count(self):
    #     for record in self:
    #         record.handover_compliance_count = len(record.handover_compliance_ids)

    @api.depends('compliance_document_ids')
    def _compute_compliance_document_count(self):
        for record in self:
            record.compliance_document_count = len(record.compliance_document_ids)

    # Temporarily disabled compute method to fix loading issues
    # @api.depends('compliance_checkpoint_ids', 'compliance_checkpoint_ids.is_reached')
    # def _compute_compliance_checkpoint_count(self):
    #     """Compute compliance checkpoint counts and progress"""
    #     for record in self:
    #         total_checkpoints = len(record.compliance_checkpoint_ids)
    #         reached_checkpoints = len(record.compliance_checkpoint_ids.filtered(lambda c: c.is_reached))
    #         
    #         record.compliance_checkpoint_count = total_checkpoints
    #         record.compliance_checkpoint_reached_count = reached_checkpoints
    #         
    #         if total_checkpoints > 0:
    #             record.compliance_checkpoint_progress = (reached_checkpoints / total_checkpoints) * 100
    #         else:
    #             record.compliance_checkpoint_progress = 0.0

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

    @api.depends('is_complete_return_compliance', 'is_complete_compliance', 'is_confirm_compliance', 'is_update_compliance')
    def _compute_compliance_workflow_state(self):
        """Compute the current workflow state based on compliance flags"""
        for record in self:
            try:
                if record.is_complete_return_compliance and not record.is_complete_compliance:
                    record.compliance_workflow_state = 'returned'
                elif record.is_complete_compliance and record.is_confirm_compliance:
                    record.compliance_workflow_state = 'confirmed'
                elif record.is_complete_compliance:
                    record.compliance_workflow_state = 'complete'
                elif record.is_update_compliance:
                    record.compliance_workflow_state = 'updated'
                elif record.compliance_shareholder_ids:
                    record.compliance_workflow_state = 'in_progress'
                else:
                    record.compliance_workflow_state = 'draft'
            except Exception:
                record.compliance_workflow_state = 'draft'

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
            
            # Trigger automation
            record._trigger_compliance_automation('complete')
            
        return True

    def action_confirm_compliance(self):
        """Confirm compliance"""
        for record in self:
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can confirm compliance."))
            
            record.is_confirm_compliance = True
            record.message_post(body=_("Compliance Confirmed"))
            
            # Trigger automation
            record._trigger_compliance_automation('confirm')
            
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
            
            # Trigger automation
            record._trigger_compliance_automation('update')
            
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
            
            # Trigger automation
            record._trigger_compliance_automation('repeat')
            
        return True

    def _trigger_compliance_automation(self, trigger_type):
        """Trigger compliance automation based on workflow state changes"""
        self.ensure_one()
        
        try:
            if trigger_type == 'complete' and self.auto_create_handover:
                self._create_compliance_handover()
            
            if trigger_type in ['complete', 'confirm'] and self.auto_copy_documents:
                self._copy_compliance_documents()
            
            if trigger_type in ['complete', 'confirm', 'return'] and self.auto_notify_stakeholders:
                self._notify_compliance_stakeholders(trigger_type)
                
        except Exception as e:
            self.message_post(body=_("Automation error: %s") % str(e))

    def _create_compliance_handover(self):
        """Create compliance handover automatically"""
        self.ensure_one()
        
        if not self.handover_compliance_ids.filtered(lambda h: h.handover_type == 'compliance'):
            handover_vals = {
                'name': f'Compliance Handover - {self.name}',
                'project_id': self.id,
                'compliance_project_id': self.id,
                'hand_partner_id': self.partner_id.id if self.partner_id else False,
                'handover_type': 'compliance',
                'compliance_status': 'pending',
                'handover_notes': f'Automatic compliance handover created for project {self.name}',
                'compliance_shareholder_ids': [(6, 0, self.compliance_shareholder_ids.ids)],
            }
            
            handover = self.env['project.handover.notes'].create(handover_vals)
            self.message_post(body=_("Compliance handover created: %s") % handover.name)

    def _copy_compliance_documents(self):
        """Copy compliance documents using automation rules"""
        self.ensure_one()
        
        if self.compliance_document_automation_ids:
            for automation in self.compliance_document_automation_ids:
                try:
                    automation.copy_documents_to_target(self)
                    self.message_post(body=_("Documents copied using automation: %s") % automation.name)
                except Exception as e:
                    self.message_post(body=_("Document automation failed: %s") % str(e))

    def _notify_compliance_stakeholders(self, trigger_type):
        """Notify stakeholders about compliance status changes"""
        self.ensure_one()
        
        # Get stakeholders to notify
        stakeholders = []
        if self.user_id:
            stakeholders.append(self.user_id)
        if self.partner_id:
            stakeholders.append(self.partner_id)
        
        # Add compliance shareholders
        for shareholder in self.compliance_shareholder_ids:
            if shareholder.contact_id:
                stakeholders.append(shareholder.contact_id)
        
        # Create notification message
        status_messages = {
            'complete': 'Compliance has been completed',
            'confirm': 'Compliance has been confirmed',
            'return': 'Compliance has been returned for revision',
            'update': 'Compliance has been updated',
            'repeat': 'Compliance process has been repeated'
        }
        
        message = status_messages.get(trigger_type, f'Compliance status changed to {trigger_type}')
        
        # Post message to project
        self.message_post(
            body=_(message),
            partner_ids=[(6, 0, [s.id for s in stakeholders if hasattr(s, 'id')])]
        )
        
        # Send email notifications if enabled
        if self.auto_notify_stakeholders:
            self._send_compliance_email_notification(trigger_type, stakeholders)

    def _send_compliance_email_notification(self, trigger_type, stakeholders):
        """Send email notifications to stakeholders"""
        self.ensure_one()
        
        try:
            # Get email template
            template = self._get_compliance_email_template(trigger_type)
            if not template:
                return
            
            # Prepare email context
            email_context = {
                'project_name': self.name,
                'compliance_status': trigger_type,
                'shareholder_count': len(self.compliance_shareholder_ids),
                'total_shareholding': self.shareholding_total,
                'project_url': f'/web#id={self.id}&model=project.project&view_type=form',
            }
            
            # Send emails to stakeholders
            for stakeholder in stakeholders:
                if hasattr(stakeholder, 'email') and stakeholder.email:
                    try:
                        template.with_context(email_context).send_mail(
                            stakeholder.id, 
                            force_send=True,
                            email_values={'email_to': stakeholder.email}
                        )
                        self.message_post(body=_("Email notification sent to %s") % stakeholder.name)
                    except Exception as e:
                        self.message_post(body=_("Failed to send email to %s: %s") % (stakeholder.name, str(e)))
                        
        except Exception as e:
            self.message_post(body=_("Email notification error: %s") % str(e))

    def _get_compliance_email_template(self, trigger_type):
        """Get appropriate email template for compliance notifications"""
        template_refs = {
            'complete': 'project_compliance.email_template_compliance_complete',
            'confirm': 'project_compliance.email_template_compliance_confirm',
            'return': 'project_compliance.email_template_compliance_return',
            'update': 'project_compliance.email_template_compliance_update',
        }
        
        template_ref = template_refs.get(trigger_type)
        if template_ref:
            return self.env.ref(template_ref, raise_if_not_found=False)
        
        return None

    def _create_compliance_activity(self, activity_type, summary, note=None):
        """Create compliance activity for tracking"""
        self.ensure_one()
        
        try:
            activity_vals = {
                'activity_type_id': self._get_compliance_activity_type(activity_type),
                'summary': summary,
                'note': note or summary,
                'res_id': self.id,
                'res_model_id': self.env['ir.model']._get('project.project').id,
                'user_id': self.env.user.id,
            }
            
            activity = self.env['mail.activity'].create(activity_vals)
            self.message_post(body=_("Compliance activity created: %s") % summary)
            return activity
            
        except Exception as e:
            self.message_post(body=_("Failed to create compliance activity: %s") % str(e))
            return None

    def _get_compliance_activity_type(self, activity_type):
        """Get compliance activity type ID"""
        activity_types = {
            'compliance_review': 'Compliance Review',
            'shareholder_validation': 'Shareholder Validation',
            'document_verification': 'Document Verification',
            'compliance_approval': 'Compliance Approval',
            'handover_preparation': 'Handover Preparation',
        }
        
        activity_name = activity_types.get(activity_type, 'Compliance Task')
        
        # Find or create activity type
        activity_type_record = self.env['mail.activity.type'].search([
            ('name', '=', activity_name)
        ], limit=1)
        
        if not activity_type_record:
            activity_type_record = self.env['mail.activity.type'].create({
                'name': activity_name,
                'category': 'default',
            })
        
        return activity_type_record.id

    def action_schedule_compliance_review(self):
        """Schedule compliance review activity"""
        self.ensure_one()
        
        if not self.compliance_shareholder_ids:
            raise UserError(_("Please add compliance shareholders before scheduling review"))
        
        activity = self._create_compliance_activity(
            'compliance_review',
            f'Compliance Review for {self.name}',
            f'Review compliance shareholders and documents for project {self.name}'
        )
        
        if activity:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.activity',
                'res_id': activity.id,
                'target': 'current',
            }
        
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

    def action_view_compliance_handovers(self):
        """Smart button to view compliance handovers"""
        self.ensure_one()
        action = self.env.ref('project_handover_notes.action_project_handover_notes').read()[0]
        action['domain'] = [('compliance_project_id', '=', self.id)]
        action['context'] = {
            'default_compliance_project_id': self.id,
            'default_handover_type': 'compliance',
        }
        return action

    def action_view_compliance_documents(self):
        """Smart button to view compliance documents"""
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', self.compliance_document_ids.ids)]
        action['context'] = {
            'default_res_model': 'project.project',
            'default_res_id': self.id,
        }
        return action

    def action_apply_compliance_template(self):
        """Apply compliance template to project"""
        self.ensure_one()
        if self.compliance_template_id:
            template = self.compliance_template_id
            
            # Apply template requirements
            if template.compliance_requirements:
                self.message_post(body=_("Compliance template applied: %s") % template.compliance_requirements)
            
            # Apply shareholder requirements
            if template.shareholder_requirements:
                self.message_post(body=_("Shareholder requirements: %s") % template.shareholder_requirements)
            
            # Apply UBO requirements
            if template.ubo_requirements:
                self.message_post(body=_("UBO requirements: %s") % template.ubo_requirements)
            
            # Apply document requirements
            if template.document_requirements:
                self.message_post(body=_("Document requirements: %s") % template.document_requirements)
            
            # Apply related checkpoint templates if available
            if template.related_checkpoint_templates:
                # Create checkpoints from template
                for checkpoint_template in template.related_checkpoint_templates:
                    checkpoint_vals = {
                        'name': checkpoint_template.name,
                        'project_id': self.id,
                        'sequence': checkpoint_template.sequence,
                        'notes': checkpoint_template.notes,
                        'auto_advance_stage': True,  # Default value for compliance checkpoints
                    }
                    
                    self.env['project.task.checkpoint'].create(checkpoint_vals)
            
            self.message_post(body=_("Compliance template '%s' successfully applied to project") % template.name)
        else:
            raise UserError(_("Please select a compliance template to apply"))
        return True

    def action_create_compliance_template(self):
        """Create compliance template from project"""
        self.ensure_one()
        
        # Create a new project template from this project
        template_vals = {
            'name': f'Compliance Template - {self.name}',
            'description': f'Compliance template created from project {self.name}',
            'is_template': True,
            'template_category': 'compliance_services',
            'template_description': f'Compliance template created from project {self.name}',
            'compliance_requirements': f'Compliance requirements from project {self.name}',
            'shareholder_requirements': 'Shareholder requirements based on project structure',
            'ubo_requirements': 'UBO requirements based on project structure',
            'document_requirements': 'Document requirements based on project structure',
        }
        
        template = self.env['project.project'].create(template_vals)
        
        self.message_post(body=_("Compliance template '%s' created successfully") % template.name)
        
        return {
            'name': _('Compliance Template Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': template.id,
            'target': 'current',
        }

    def action_copy_compliance_documents(self):
        """Copy compliance documents using automation rules"""
        self.ensure_one()
        if self.auto_copy_compliance_documents and self.compliance_document_automation_ids:
            for automation in self.compliance_document_automation_ids:
                try:
                    automation.copy_documents_to_target(self)
                    self.message_post(body=_("Compliance documents copied using automation '%s'") % automation.name)
                except Exception as e:
                    self.message_post(body=_("Failed to copy compliance documents: %s") % str(e))
        return True

    def action_create_compliance_document_automation(self):
        """Create compliance document automation rule"""
        self.ensure_one()
        return {
            'name': _('Create Compliance Document Automation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'unified.document.copy.automation',
            'context': {
                'default_name': f'Compliance Automation - {self.name}',
                'default_target_model': 'project.project',
                'default_target_domain': f"[('id', '=', {self.id})]",
            },
            'target': 'new',
        }

    # Checkpoint Management Methods
    def action_view_compliance_checkpoints(self):
        """Smart button to view compliance checkpoints"""
        self.ensure_one()
        action = self.env.ref('project_checkpoints_basic.action_project_task_checkpoint').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'default_name': f'Compliance Checkpoint - {self.name}',
        }
        return action

    def action_apply_compliance_checkpoint_templates(self):
        """Apply compliance checkpoint templates to project"""
        self.ensure_one()
        if self.compliance_template_id and self.compliance_template_id.related_checkpoint_templates:
            for template in self.compliance_template_id.related_checkpoint_templates:
                # Create checkpoint from template
                checkpoint_vals = {
                    'name': template.name,
                    'project_id': self.id,
                    'sequence': template.sequence,
                    'notes': template.notes,
                    'auto_advance_stage': True,  # Default value for compliance checkpoints
                }
                
                self.env['project.task.checkpoint'].create(checkpoint_vals)
            
            self.message_post(body=_("Applied %d compliance checkpoint templates") % len(self.compliance_template_id.related_checkpoint_templates))
        else:
            raise UserError(_("No compliance checkpoint templates available in the selected template"))
        return True

    def action_create_compliance_checkpoint(self):
        """Create a new compliance checkpoint"""
        self.ensure_one()
        return {
            'name': _('Create Compliance Checkpoint'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.task.checkpoint',
            'context': {
                'default_project_id': self.id,
                'default_name': f'Compliance Checkpoint - {self.name}',
            },
            'target': 'new',
        }

    def action_auto_create_compliance_checkpoints(self):
        """Automatically create compliance checkpoints based on workflow state"""
        self.ensure_one()
        
        # Define compliance workflow checkpoints
        compliance_checkpoints = [
            {
                'name': 'Initial Compliance Review',
                'sequence': 10,
                'notes': 'Initial review of compliance requirements and documentation',
                'auto_advance_stage': True,
            },
            {
                'name': 'Shareholder Verification',
                'sequence': 20,
                'notes': 'Verify all shareholder information and documentation',
                'auto_advance_stage': True,
            },
            {
                'name': 'UBO Identification',
                'sequence': 30,
                'notes': 'Identify and verify Ultimate Beneficial Owners',
                'auto_advance_stage': True,
            },
            {
                'name': 'Document Collection',
                'sequence': 40,
                'notes': 'Collect all required compliance documents',
                'auto_advance_stage': True,
            },
            {
                'name': 'Compliance Assessment',
                'sequence': 50,
                'notes': 'Complete compliance assessment and validation',
                'auto_advance_stage': True,
            },
            {
                'name': 'Final Approval',
                'sequence': 60,
                'notes': 'Final compliance approval and sign-off',
                'auto_advance_stage': True,
            }
        ]
        
        # Create checkpoints
        for checkpoint_data in compliance_checkpoints:
            checkpoint_vals = {
                'name': checkpoint_data['name'],
                'project_id': self.id,
                'sequence': checkpoint_data['sequence'],
                'notes': checkpoint_data['notes'],
                'auto_advance_stage': checkpoint_data['auto_advance_stage'],
            }
            self.env['project.task.checkpoint'].create(checkpoint_vals)
        
        self.message_post(body=_("Created %d compliance checkpoints automatically") % len(compliance_checkpoints))
        return True
