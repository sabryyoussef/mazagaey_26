from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class LicenseActivity(models.Model):
    _name = 'license.activity'
    _description = 'License Activity'
    _order = 'sequence, name'

    name = fields.Char(string='Activity Name', required=True)
    code = fields.Char(string='Activity Code', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)


class ProjectHandoverNotes(models.Model):
    _name = 'project.handover.notes'
    _description = 'Project Handover Notes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(string='Handover Reference', required=True, copy=False, 
                      readonly=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', string='Project', required=True, 
                                ondelete='cascade', tracking=True)
    hand_partner_id = fields.Many2one('res.partner', string='Client/Partner', 
                                     required=True, tracking=True, ondelete='cascade')
    
    # Status Fields
    handover_status = fields.Selection([
        ('draft', 'Draft'),
        ('complete', 'Complete'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('updated', 'Updated'),
    ], string='Handover Status', default='draft', tracking=True)
    
    is_complete_hand = fields.Boolean(string="Handover Complete", copy=False, tracking=True)
    is_confirm_hand = fields.Boolean(string="Handover Confirm", copy=False, tracking=True)
    is_complete_return_hand = fields.Boolean(string="Handover Returned", copy=False, tracking=True)
    is_update_hand = fields.Boolean(string="Update Handover", copy=False, tracking=True)
    is_second_complete_hand_check = fields.Integer(string="Second Complete Handover Check", 
                                                  copy=False, default=0, tracking=True)
    
    # Handover Details
    handover_date = fields.Date(string='Handover Date', tracking=True)
    handover_by = fields.Many2one('res.users', string='Handover By', tracking=True)
    handover_notes = fields.Html(string='Handover Notes', tracking=True)
    
    # Partner Information
    hand_partner_company_type = fields.Selection([
        ('person', 'Individual'),
        ('company', 'Company'),
    ], string='Contact Type', default='company', tracking=True)
    
    hand_partner_first_name = fields.Char(string='First Name', tracking=True)
    hand_partner_middle_name = fields.Char(string='Middle Name', tracking=True)
    hand_partner_last_name = fields.Char(string='Last Name', tracking=True)
    hand_partner_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', tracking=True)
    hand_partner_nationality_id = fields.Many2one('res.country', string='Nationality', tracking=True, ondelete='set null')
    hand_partner_place_of_birth = fields.Many2one('res.country', string='Place Of Birth', tracking=True, ondelete='set null')
    
    # Contact Information
    correspondence_email_address = fields.Char(string='Correspondence Email Address', tracking=True)
    preferred_mobile_number = fields.Char(string='Preferred Mobile Number', tracking=True)
    
    # Company Formation
    initial_company_info = fields.Boolean(string="Initial Company Formation", default=True, copy=False, tracking=True)
    proposed_name1 = fields.Char(string='Proposed Name 1', tracking=True)
    proposed_name2 = fields.Char(string='Proposed Name 2', tracking=True)
    proposed_name3 = fields.Char(string='Proposed Name 3', tracking=True)
    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True, tracking=True)
    
    # Legal Information
    hand_legal_type = fields.Selection([
        ('fzco', 'FZCO'),
        ('fze', 'FZE'),
        ('llc', 'LLC'),
    ], string='Legal Entity/Type', tracking=True)
    license_authority_id = fields.Char(string='License Authority', tracking=True)
    license_validity = fields.Selection([
        ('1', '1 Year'),
        ('2', '2 Years'),
        ('3', '3 Years'),
        ('4', '4 Years'),
        ('5', '5 Years'),
        ('6', '6 Years'),
        ('7', '7 Years'),
        ('8', '8 Years'),
        ('9', '9 Years'),
        ('10', '10 Years'),
    ], string='License Validity', tracking=True)
    license_activity_ids = fields.Many2many('license.activity', string='License Activities', tracking=True)
    hand_country_ids = fields.Many2many('res.country', string='Top 5 Countries of Operation', tracking=True)
    channel_plan_id = fields.Char(string='Channel Partner Plan', tracking=True)
    
    # Compliance Integration
    project_id = fields.Many2one('project.project', string='Compliance Project', tracking=True)
    handover_type = fields.Selection([
        ('general', 'General'),
        ('compliance', 'Compliance'),
        ('technical', 'Technical'),
        ('financial', 'Financial'),
    ], string='Handover Type', default='general', tracking=True)
    
    # Compliance-specific fields
    compliance_shareholder_ids = fields.Many2many('res.partner.business.shareholder', string='Compliance Shareholders', tracking=True)
    compliance_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
        ('verified', 'Verified'),
    ], string='Compliance Status', default='pending', tracking=True)
    compliance_notes = fields.Html(string='Compliance Notes', tracking=True)
    
    # Compliance Automation
    auto_update_compliance_project = fields.Boolean(string='Auto Update Compliance Project', default=True, tracking=True)
    auto_transfer_shareholders = fields.Boolean(string='Auto Transfer Shareholders', default=True, tracking=True)
    visa_eligibility = fields.Float(string='Visa Eligibility', tracking=True)
    
    # Share Information
    price_per_share = fields.Float(string='Price Per Share', tracking=True)
    total_number_shares = fields.Float(string='Total Number Of Shares', tracking=True)
    total_share_value = fields.Monetary(string='Total Share Value', compute='_compute_share_value', 
                                      currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id, ondelete='set null')
    
    # Visa Information
    is_visa_application = fields.Boolean(string="Is Visa Application", copy=False, tracking=True)
    apply_visa = fields.Boolean(string="Apply Visa", copy=False, tracking=True)
    
    # Computed Fields

    # Integration Fields
    template_id = fields.Many2one('project.project', string='Handover Template', tracking=True, domain=[('is_template', '=', True)])
    checkpoint_ids = fields.Many2many('project.task.checkpoint', string='Related Checkpoints', tracking=True)
    document_ids = fields.Many2many('documents.document', string='Handover Documents', tracking=True)
    automation_ids = fields.Many2many('unified.document.copy.automation', string='Document Automations', tracking=True)
    
    # Integration Computed Fields
    template_category = fields.Selection(related='template_id.template_category', readonly=True, store=True)
    checkpoint_count = fields.Integer(compute='_compute_checkpoint_count', store=True)
    document_count = fields.Integer(compute='_compute_document_count', store=True)
    is_update_hand_check = fields.Boolean(compute='_compute_is_update_hand_check', store=False)
    is_current_user_project_manager = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_admin = fields.Boolean(compute='_compute_user_permissions', store=False)
    is_current_user_project_task_assignee = fields.Boolean(compute='_compute_user_permissions', store=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.handover.notes') or _('New')
        return super().create(vals)
    
    @api.depends('proposed_name1', 'proposed_name2', 'proposed_name3', 'initial_company_info')
    def _compute_full_name(self):
        for record in self:
            if record.initial_company_info:
                names = [name for name in [record.proposed_name1, record.proposed_name2, record.proposed_name3] if name]
                record.full_name = ' - '.join(names) if names else ''
            else:
                names = [name for name in [record.hand_partner_first_name, record.hand_partner_middle_name, record.hand_partner_last_name] if name]
                record.full_name = ' '.join(names) if names else ''
    
    @api.depends('price_per_share', 'total_number_shares')
    def _compute_share_value(self):
        for record in self:
            try:
                record.total_share_value = (record.price_per_share or 0.0) * (record.total_number_shares or 0.0)
            except Exception:
                record.total_share_value = 0.0
    
    @api.depends('is_complete_return_hand', 'is_complete_hand', 'is_confirm_hand')
    def _compute_is_update_hand_check(self):
        for record in self:
            try:
                if (record.is_complete_return_hand and 
                    not record.is_complete_hand and 
                    not record.is_confirm_hand and
                    (record.is_current_user_project_manager or record.is_current_user_project_admin)):
                    record.is_update_hand_check = True
                else:
                    record.is_update_hand_check = False
            except Exception:
                record.is_update_hand_check = False
    
    def _compute_user_permissions(self):
        current_user = self.env.user
        for record in self:
            try:
                record.is_current_user_project_manager = record.project_id.user_id == current_user if record.project_id else False
                record.is_current_user_project_admin = current_user.has_group('project.group_project_manager')
                # Check if current user is assigned to any tasks in this project
                if record.project_id and record.project_id.task_ids:
                    task_users = record.project_id.task_ids.mapped('user_ids')
                    record.is_current_user_project_task_assignee = current_user in task_users if task_users else False
                else:
                    record.is_current_user_project_task_assignee = False
            except Exception:
                record.is_current_user_project_manager = False
                record.is_current_user_project_admin = False
                record.is_current_user_project_task_assignee = False
    
    # Action Methods
    def action_complete_hand(self):
        for record in self:
            if not (record.is_current_user_project_manager or record.is_current_user_project_admin):
                raise UserError(_("Only project managers or admins can complete handover."))
            
            record.is_complete_hand = True
            record.handover_status = 'complete'
            record.handover_date = fields.Date.today()
            record.handover_by = self.env.user.id
            record.message_post(body=_("Handover Completed"))
    
    def action_confirm_hand(self):
        for record in self:
            if not record.is_complete_hand:
                raise UserError(_("Handover must be completed before confirmation."))
            
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can confirm handover."))
            
            record.is_confirm_hand = True
            record.handover_status = 'confirmed'
            record.message_post(body=_("Handover Confirmed"))
    
    def action_return_hand(self):
        for record in self:
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can return handover."))
            
            return {
                'name': _("Return Handover"),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'return.handover.wizard',
                'context': {'default_handover_id': record.id},
                'target': 'new',
            }
    
    def action_update_hand(self):
        for record in self:
            if not (record.is_current_user_project_manager or record.is_current_user_project_admin):
                raise UserError(_("Only project managers or admins can update handover."))
            
            record.is_update_hand = True
            record.handover_status = 'updated'
            record.is_complete_return_hand = False
            record.message_post(body=_("Handover Updated"))
    
    def action_repeat_hand(self):
        for record in self:
            if not record.is_current_user_project_admin:
                raise UserError(_("Only admins can repeat handover."))
            
            record.is_complete_hand = False
            record.is_confirm_hand = False
            record.is_complete_return_hand = False
            record.is_update_hand = False
            record.handover_status = 'draft'
            record.message_post(body=_("Handover Repeated"))
    
    @api.onchange('hand_partner_id')
    def _onchange_hand_partner_id(self):
        if self.hand_partner_id:
            self.hand_partner_company_type = 'company' if self.hand_partner_id.is_company else 'person'
            self.correspondence_email_address = self.hand_partner_id.email
            self.preferred_mobile_number = self.hand_partner_id.mobile
            if not self.hand_partner_id.is_company:
                # Use standard partner fields
                self.hand_partner_first_name = getattr(self.hand_partner_id, 'first_name', '')
                self.hand_partner_middle_name = getattr(self.hand_partner_id, 'middle_name', '')
                self.hand_partner_last_name = getattr(self.hand_partner_id, 'last_name', '')
                self.hand_partner_gender = getattr(self.hand_partner_id, 'gender', False)
                self.hand_partner_nationality_id = getattr(self.hand_partner_id, 'nationality_id', False)
                self.hand_partner_place_of_birth = getattr(self.hand_partner_id, 'place_of_birth', False)

    @api.depends("checkpoint_ids")
    def _compute_checkpoint_count(self):
        for record in self:
            record.checkpoint_count = len(record.checkpoint_ids)
    
    @api.depends("document_ids")
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    def copy_documents_to_handover(self):
        """Copy relevant documents to handover based on automation rules"""
        for handover in self:
            automations = handover.automation_ids
            for automation in automations:
                automation.copy_documents_to_target(handover)
    
    def apply_handover_template(self):
        """Apply template structure to handover"""
        if self.template_id:
            # Apply template description as default notes
            if self.template_id.template_description:
                self.handover_notes = self.template_id.template_description

    # Compliance Integration Methods
    def action_complete_compliance_handover(self):
        """Complete compliance handover"""
        for record in self:
            if record.handover_type != 'compliance':
                raise UserError(_("This action is only available for compliance handovers."))
            
            if not (record.is_current_user_project_manager or record.is_current_user_project_admin):
                raise UserError(_("Only project managers or admins can complete compliance handover."))
            
            record.compliance_status = 'complete'
            record.handover_status = 'complete'
            record.message_post(body=_("Compliance Handover Completed"))
            
            # Trigger compliance automation
            record._trigger_compliance_handover_automation('complete')

    def action_verify_compliance_handover(self):
        """Verify compliance handover"""
        for record in self:
            if record.handover_type != 'compliance':
                raise UserError(_("This action is only available for compliance handovers."))
            
            if not (record.is_current_user_project_task_assignee or record.is_current_user_project_admin):
                raise UserError(_("Only task assignees or admins can verify compliance handover."))
            
            record.compliance_status = 'verified'
            record.message_post(body=_("Compliance Handover Verified"))
            
            # Trigger compliance automation
            record._trigger_compliance_handover_automation('verify')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update compliance shareholders when compliance project changes"""
        if self.project_id:
            self.compliance_shareholder_ids = self.project_id.compliance_shareholder_ids

    def _trigger_compliance_handover_automation(self, trigger_type):
        """Trigger compliance handover automation"""
        self.ensure_one()
        
        try:
            if trigger_type == 'complete' and self.auto_update_compliance_project:
                self._update_compliance_project_status()
            
            if trigger_type in ['complete', 'verify'] and self.auto_transfer_shareholders:
                self._transfer_compliance_shareholders()
                
        except Exception as e:
            self.message_post(body=_("Compliance automation error: %s") % str(e))

    def _update_compliance_project_status(self):
        """Update the linked compliance project status"""
        self.ensure_one()
        
        if self.project_id:
            project = self.project_id
            if self.compliance_status == 'complete':
                project.is_complete_compliance = True
                project.message_post(body=_("Compliance status updated via handover: %s") % self.name)

    def _transfer_compliance_shareholders(self):
        """Transfer compliance shareholders between projects"""
        self.ensure_one()
        
        if self.project_id and self.compliance_shareholder_ids:
            # Update the compliance project with current shareholders
            self.project_id.compliance_shareholder_ids = self.compliance_shareholder_ids
            self.message_post(body=_("Compliance shareholders transferred to project"))
