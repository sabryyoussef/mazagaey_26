# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class DocumentRequest(models.Model):
    _name = 'gr.document.request'
    _description = 'Grants Training Document Request'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Request Reference',
        required=True,
        default=lambda self: _('New'),
        help='Unique reference for this document request'
    )
    
    # Request Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student requesting the document'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        related='student_id.assigned_agent_id',
        store=True,
        help='Agent assigned to the student'
    )
    
    # Document Information
    document_type = fields.Selection([
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('birth_certificate', 'Birth Certificate'),
        ('education_certificate', 'Education Certificate'),
        ('work_experience', 'Work Experience Certificate'),
        ('language_certificate', 'Language Certificate'),
        ('medical_certificate', 'Medical Certificate'),
        ('financial_document', 'Financial Document'),
        ('other', 'Other'),
    ], string='Document Type', required=True, tracking=True, help='Type of document requested')
    
    document_name = fields.Char(
        string='Document Name',
        help='Specific name or description of the document'
    )
    
    # Request Information
    request_date = fields.Datetime(
        string='Request Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='Date when the request was made'
    )
    
    requested_by_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        tracking=True,
        help='User who made the request'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)
    
    # Document Details
    document_description = fields.Text(
        string='Document Description',
        help='Detailed description of the required document'
    )
    
    required_format = fields.Selection([
        ('original', 'Original'),
        ('certified_copy', 'Certified Copy'),
        ('photocopy', 'Photocopy'),
        ('digital_copy', 'Digital Copy'),
        ('any', 'Any Format'),
    ], string='Required Format', default='any', help='Required format of the document')
    
    is_mandatory = fields.Boolean(
        string='Mandatory',
        default=True,
        help='Whether this document is mandatory for the student'
    )
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal', tracking=True, help='Priority level of the request')
    
    # Submission Information
    submission_date = fields.Datetime(
        string='Submission Date',
        help='Date when the document was submitted'
    )
    
    submitted_by_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        help='User who submitted the document'
    )
    
    # Review Information
    review_date = fields.Datetime(
        string='Review Date',
        help='Date when the document was reviewed'
    )
    
    reviewed_by_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='User who reviewed the document'
    )
    
    review_notes = fields.Text(
        string='Review Notes',
        help='Notes from the document review'
    )
    
    # Document File
    document_file = fields.Binary(
        string='Document File',
        help='Uploaded document file'
    )
    
    document_filename = fields.Char(
        string='Document Filename',
        help='Name of the uploaded document file'
    )
    
    # Deadline Information
    deadline_date = fields.Datetime(
        string='Deadline',
        help='Deadline for document submission'
    )
    
    days_until_deadline = fields.Integer(
        string='Days Until Deadline',
        compute='_compute_days_until_deadline',
        store=True,
        help='Number of days until deadline'
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='Whether the request is overdue'
    )
    
    # Computed Fields
    days_since_request = fields.Integer(
        string='Days Since Request',
        compute='_compute_days_since_request',
        store=True,
        help='Number of days since request was made'
    )
    
    processing_time = fields.Float(
        string='Processing Time (hours)',
        compute='_compute_processing_time',
        store=True,
        help='Time taken to process the request'
    )
    
    def _compute_days_until_deadline(self):
        """Compute days until deadline."""
        for record in self:
            if record.deadline_date:
                delta = record.deadline_date - fields.Datetime.now()
                record.days_until_deadline = delta.days
            else:
                record.days_until_deadline = 0
    
    def _compute_is_overdue(self):
        """Compute if request is overdue."""
        for record in self:
            if record.deadline_date and record.state not in ['approved', 'rejected']:
                record.is_overdue = fields.Datetime.now() > record.deadline_date
            else:
                record.is_overdue = False
    
    def _compute_days_since_request(self):
        """Compute days since request."""
        for record in self:
            if record.request_date:
                delta = fields.Datetime.now() - record.request_date
                record.days_since_request = delta.days
            else:
                record.days_since_request = 0
    
    def _compute_processing_time(self):
        """Compute processing time."""
        for record in self:
            if record.request_date and record.state in ['approved', 'rejected']:
                end_date = record.review_date or fields.Datetime.now()
                delta = end_date - record.request_date
                record.processing_time = delta.total_seconds() / 3600  # Convert to hours
            else:
                record.processing_time = 0.0
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and deadline."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.document.request') or _('New')
        
        # Set default deadline (7 days from request)
        if not vals.get('deadline_date') and vals.get('request_date'):
            request_date = fields.Datetime.from_string(vals['request_date'])
            vals['deadline_date'] = request_date + timedelta(days=7)
        elif not vals.get('deadline_date'):
            vals['deadline_date'] = fields.Datetime.now() + timedelta(days=7)
        
        document_request = super(DocumentRequest, self).create(vals)
        
        # Log creation
        _logger.info('Document request created: %s - Student: %s, Type: %s', 
                    document_request.name, document_request.student_id.name, document_request.document_type)
        
        return document_request
    
    def action_request(self):
        """Action to confirm the request."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft requests can be confirmed.'))
        
        self.state = 'requested'
        
        # Log request
        _logger.info('Document request confirmed: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Request Confirmed'),
                'message': _('Document request has been confirmed.'),
                'type': 'success',
            }
        }
    
    def action_submit_document(self):
        """Action to submit the document."""
        self.ensure_one()
        
        if self.state != 'requested':
            raise UserError(_('Only requested documents can be submitted.'))
        
        if not self.document_file:
            raise UserError(_('Please upload the document file before submitting.'))
        
        self.state = 'submitted'
        self.submission_date = fields.Datetime.now()
        self.submitted_by_id = self.env.user
        
        # Log submission
        _logger.info('Document submitted: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Submitted'),
                'message': _('Document has been submitted for review.'),
                'type': 'success',
            }
        }
    
    def action_start_review(self):
        """Action to start document review."""
        self.ensure_one()
        
        if self.state != 'submitted':
            raise UserError(_('Only submitted documents can be reviewed.'))
        
        self.state = 'under_review'
        self.review_date = fields.Datetime.now()
        self.reviewed_by_id = self.env.user
        
        # Log review start
        _logger.info('Document review started: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Review Started'),
                'message': _('Document review has been started.'),
                'type': 'info',
            }
        }
    
    def action_approve(self):
        """Action to approve the document."""
        self.ensure_one()
        
        if self.state != 'under_review':
            raise UserError(_('Only documents under review can be approved.'))
        
        self.state = 'approved'
        self.review_date = fields.Datetime.now()
        self.reviewed_by_id = self.env.user
        
        # Log approval
        _logger.info('Document approved: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Approved'),
                'message': _('Document has been approved.'),
                'type': 'success',
            }
        }
    
    def action_reject(self):
        """Action to reject the document."""
        self.ensure_one()
        
        if self.state != 'under_review':
            raise UserError(_('Only documents under review can be rejected.'))
        
        self.state = 'rejected'
        self.review_date = fields.Datetime.now()
        self.reviewed_by_id = self.env.user
        
        # Log rejection
        _logger.info('Document rejected: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Rejected'),
                'message': _('Document has been rejected.'),
                'type': 'warning',
            }
        }
    
    def action_expire(self):
        """Action to mark request as expired."""
        self.ensure_one()
        
        if self.state in ['approved', 'rejected']:
            raise UserError(_('Completed requests cannot be expired.'))
        
        self.state = 'expired'
        
        # Log expiration
        _logger.info('Document request expired: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Request Expired'),
                'message': _('Document request has been marked as expired.'),
                'type': 'warning',
            }
        }
    
    def action_reset(self):
        """Action to reset request to draft."""
        self.ensure_one()
        self.state = 'draft'
        self.submission_date = False
        self.submitted_by_id = False
        self.review_date = False
        self.reviewed_by_id = False
        self.review_notes = False
        self.document_file = False
        self.document_filename = False
        
        # Log reset
        _logger.info('Document request reset: %s', self.name)
    
    @api.constrains('deadline_date')
    def _check_deadline_date(self):
        """Validate deadline date."""
        for record in self:
            if record.deadline_date and record.deadline_date < record.request_date:
                raise ValidationError(_('Deadline cannot be before the request date.'))
    
    @api.onchange('document_file')
    def _onchange_document_file(self):
        """Auto-populate filename when document is uploaded."""
        if self.document_file:
            # Extract filename from the uploaded file
            # In Odoo, the filename is usually stored in the context or can be extracted
            # For now, we'll set a default filename if none is provided
            if not self.document_filename:
                self.document_filename = f"document_{self.document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    @api.constrains('document_file')
    def _check_document_file(self):
        """Validate document file."""
        for record in self:
            if record.document_file and not record.document_filename:
                # Auto-generate filename if missing
                record.document_filename = f"document_{record.document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def name_get(self):
        """Custom name display for document request records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.document_type} ({record.student_id.name if record.student_id else 'No Student'})"
            result.append((record.id, name))
        return result
