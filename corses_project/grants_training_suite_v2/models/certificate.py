# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Certificate(models.Model):
    _name = 'gr.certificate'
    _description = 'Grants Training Certificate'
    _order = 'issue_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Certificate Number',
        required=True,
        default=lambda self: _('New'),
        help='Unique certificate number'
    )
    
    # Certificate Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student receiving the certificate'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        related='student_id.assigned_agent_id',
        store=True,
        help='Agent assigned to the student'
    )
    
    # Certificate Information
    certificate_type = fields.Selection([
        ('completion', 'Course Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('excellence', 'Excellence'),
        ('professional', 'Professional Development'),
        ('language', 'Language Proficiency'),
        ('technical', 'Technical Skills'),
        ('program_completion', 'Program Completion'),
        ('other', 'Other'),
    ], string='Certificate Type', required=True, tracking=True, help='Type of certificate')
    
    certificate_title = fields.Char(
        string='Certificate Title',
        required=True,
        help='Title of the certificate'
    )
    
    certificate_description = fields.Text(
        string='Certificate Description',
        help='Description of the certificate'
    )
    
    # Course Information
    course_name = fields.Char(
        string='Course Name',
        help='Name of the course for which certificate is issued'
    )
    
    course_duration = fields.Float(
        string='Course Duration (hours)',
        help='Duration of the course in hours'
    )
    
    completion_date = fields.Date(
        string='Course Completion Date',
        help='Date when the course was completed'
    )
    
    # Automation Integration
    automation_id = fields.Many2one(
        'gr.certificate.automation',
        string='Certificate Automation',
        help='Automation rule that generated this certificate'
    )
    
    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        help='Training program this certificate is for'
    )
    
    # Issue Information
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        required=True,
        tracking=True,
        help='Date when certificate was issued'
    )
    
    issued_by_id = fields.Many2one(
        'res.users',
        string='Issued By',
        default=lambda self: self.env.user,
        tracking=True,
        help='User who issued the certificate'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('delivered', 'Delivered'),
        ('verified', 'Verified'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)
    
    # Validity Information
    valid_from = fields.Date(
        string='Valid From',
        default=fields.Date.today,
        help='Date from which certificate is valid'
    )
    
    valid_until = fields.Date(
        string='Valid Until',
        help='Date until which certificate is valid'
    )
    
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True,
        help='Whether the certificate is expired'
    )
    
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True,
        help='Number of days until certificate expires'
    )
    
    # Performance Information
    final_grade = fields.Float(
        string='Final Grade',
        help='Final grade achieved in the course'
    )
    
    grade_percentage = fields.Float(
        string='Grade Percentage',
        help='Grade as percentage'
    )
    
    attendance_percentage = fields.Float(
        string='Attendance Percentage',
        help='Attendance percentage in the course'
    )
    
    # Certificate File
    certificate_file = fields.Binary(
        string='Certificate File',
        help='Digital certificate file'
    )
    
    certificate_filename = fields.Char(
        string='Certificate Filename',
        help='Name of the certificate file'
    )
    
    # Delivery Information
    delivery_date = fields.Date(
        string='Delivery Date',
        help='Date when certificate was delivered to student'
    )
    
    delivery_method = fields.Selection([
        ('email', 'Email'),
        ('postal', 'Postal Mail'),
        ('in_person', 'In Person'),
        ('digital', 'Digital Download'),
        ('other', 'Other'),
    ], string='Delivery Method', help='Method used to deliver the certificate')
    
    delivery_address = fields.Text(
        string='Delivery Address',
        help='Address where certificate was delivered'
    )
    
    # Additional Information
    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about the certificate'
    )
    
    # Verification Information
    verification_code = fields.Char(
        string='Verification Code',
        help='Unique code for certificate verification'
    )
    
    verification_url = fields.Char(
        string='Verification URL',
        help='URL for online certificate verification'
    )
    
    verified_date = fields.Date(
        string='Verified Date',
        help='Date when certificate was verified'
    )
    
    verified_by_id = fields.Many2one(
        'res.users',
        string='Verified By',
        help='User who verified the certificate'
    )
    
    # Computed Fields
    days_since_issue = fields.Integer(
        string='Days Since Issue',
        compute='_compute_days_since_issue',
        store=True,
        help='Number of days since certificate was issued'
    )
    
    is_valid = fields.Boolean(
        string='Is Valid',
        compute='_compute_is_valid',
        store=True,
        help='Whether the certificate is currently valid'
    )
    
    def _compute_is_expired(self):
        """Compute if certificate is expired."""
        for record in self:
            if record.valid_until:
                record.is_expired = fields.Date.today() > record.valid_until
            else:
                record.is_expired = False
    
    def _compute_days_until_expiry(self):
        """Compute days until expiry."""
        for record in self:
            if record.valid_until:
                delta = record.valid_until - fields.Date.today()
                record.days_until_expiry = delta.days
            else:
                record.days_until_expiry = 0
    
    def _compute_days_since_issue(self):
        """Compute days since issue."""
        for record in self:
            if record.issue_date:
                delta = fields.Date.today() - record.issue_date
                record.days_since_issue = delta.days
            else:
                record.days_since_issue = 0
    
    def _compute_is_valid(self):
        """Compute if certificate is valid."""
        for record in self:
            if record.state == 'verified' and not record.is_expired:
                record.is_valid = True
            else:
                record.is_valid = False
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and verification code."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.certificate') or _('New')
        
        # Generate verification code if not provided
        if not vals.get('verification_code'):
            import secrets
            vals['verification_code'] = secrets.token_hex(8).upper()
        
        # Set default validity period (2 years) if not provided
        if not vals.get('valid_until') and vals.get('issue_date'):
            issue_date = fields.Date.from_string(vals['issue_date'])
            vals['valid_until'] = issue_date + timedelta(days=730)  # 2 years
        elif not vals.get('valid_until'):
            vals['valid_until'] = fields.Date.today() + timedelta(days=730)
        
        certificate = super(Certificate, self).create(vals)
        
        # Log creation
        _logger.info('Certificate created: %s - Student: %s, Type: %s', 
                    certificate.name, certificate.student_id.name, certificate.certificate_type)
        
        return certificate
    
    def action_issue(self):
        """Action to issue the certificate."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft certificates can be issued.'))
        
        self.state = 'issued'
        self.issue_date = fields.Date.today()
        self.issued_by_id = self.env.user
        
        # Log issue
        _logger.info('Certificate issued: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Issued'),
                'message': _('Certificate has been issued.'),
                'type': 'success',
            }
        }
    
    def action_deliver(self):
        """Action to deliver the certificate."""
        self.ensure_one()
        
        if self.state != 'issued':
            raise UserError(_('Only issued certificates can be delivered.'))
        
        self.state = 'delivered'
        self.delivery_date = fields.Date.today()
        
        # Log delivery
        _logger.info('Certificate delivered: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Delivered'),
                'message': _('Certificate has been delivered.'),
                'type': 'success',
            }
        }
    
    def action_verify(self):
        """Action to verify the certificate."""
        self.ensure_one()
        
        if self.state not in ['issued', 'delivered']:
            raise UserError(_('Only issued or delivered certificates can be verified.'))
        
        self.state = 'verified'
        self.verified_date = fields.Date.today()
        self.verified_by_id = self.env.user
        
        # Log verification
        _logger.info('Certificate verified: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Verified'),
                'message': _('Certificate has been verified.'),
                'type': 'success',
            }
        }
    
    def action_revoke(self):
        """Action to revoke the certificate."""
        self.ensure_one()
        
        if self.state in ['revoked']:
            raise UserError(_('Certificate is already revoked.'))
        
        self.state = 'revoked'
        
        # Log revocation
        _logger.info('Certificate revoked: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Revoked'),
                'message': _('Certificate has been revoked.'),
                'type': 'warning',
            }
        }
    
    def action_expire(self):
        """Action to mark certificate as expired."""
        self.ensure_one()
        
        if self.state in ['revoked', 'expired']:
            raise UserError(_('Certificate is already revoked or expired.'))
        
        self.state = 'expired'
        
        # Log expiration
        _logger.info('Certificate expired: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Expired'),
                'message': _('Certificate has been marked as expired.'),
                'type': 'warning',
            }
        }
    
    def action_reset(self):
        """Action to reset certificate to draft."""
        self.ensure_one()
        self.state = 'draft'
        self.issue_date = False
        self.issued_by_id = False
        self.delivery_date = False
        self.verified_date = False
        self.verified_by_id = False
        
        # Log reset
        _logger.info('Certificate reset: %s', self.name)
    
    @api.constrains('valid_until')
    def _check_valid_until(self):
        """Validate valid until date."""
        for record in self:
            if record.valid_until and record.valid_from and record.valid_until < record.valid_from:
                raise ValidationError(_('Valid until date cannot be before valid from date.'))
    
    @api.constrains('final_grade')
    def _check_final_grade(self):
        """Validate final grade."""
        for record in self:
            if record.final_grade and (record.final_grade < 0 or record.final_grade > 100):
                raise ValidationError(_('Final grade must be between 0 and 100.'))
    
    @api.constrains('attendance_percentage')
    def _check_attendance_percentage(self):
        """Validate attendance percentage."""
        for record in self:
            if record.attendance_percentage and (record.attendance_percentage < 0 or record.attendance_percentage > 100):
                raise ValidationError(_('Attendance percentage must be between 0 and 100.'))
    
    def name_get(self):
        """Custom name display for certificate records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.certificate_title} ({record.student_id.name if record.student_id else 'No Student'})"
            result.append((record.id, name))
        return result
