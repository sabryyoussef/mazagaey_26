# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class HomeworkAttempt(models.Model):
    _name = 'gr.homework.attempt'
    _description = 'Grants Training Homework Attempt'
    _order = 'submission_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Attempt Reference',
        required=True,
        default=lambda self: _('New'),
        help='Unique reference for this homework attempt'
    )
    
    # Homework Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student who submitted the homework'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        related='student_id.assigned_agent_id',
        store=True,
        help='Agent assigned to the student'
    )
    
    # Homework Information
    homework_title = fields.Char(
        string='Homework Title',
        required=True,
        help='Title of the homework assignment'
    )
    
    homework_description = fields.Text(
        string='Homework Description',
        help='Description of the homework assignment'
    )
    
    homework_type = fields.Selection([
        ('written', 'Written Assignment'),
        ('practical', 'Practical Exercise'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ], string='Homework Type', default='written', help='Type of homework assignment')
    
    # Submission Information
    submission_date = fields.Datetime(
        string='Submission Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='Date when homework was submitted'
    )
    
    due_date = fields.Datetime(
        string='Due Date',
        required=True,
        help='Due date for the homework'
    )
    
    is_late = fields.Boolean(
        string='Is Late',
        compute='_compute_is_late',
        store=True,
        help='Whether the submission is late'
    )
    
    days_late = fields.Integer(
        string='Days Late',
        compute='_compute_days_late',
        store=True,
        help='Number of days the submission is late'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
        ('resubmitted', 'Resubmitted'),
    ], string='Status', default='draft', tracking=True)
    
    # Submission Content
    submission_content = fields.Text(
        string='Submission Content',
        help='Text content of the homework submission'
    )
    
    submission_file = fields.Binary(
        string='Submission File',
        help='File attachment for the homework submission'
    )
    
    submission_filename = fields.Char(
        string='Submission Filename',
        help='Name of the submitted file'
    )
    
    # Grading Information
    grade = fields.Float(
        string='Grade',
        help='Grade received for the homework (0-100)'
    )
    
    max_grade = fields.Float(
        string='Maximum Grade',
        default=100.0,
        help='Maximum possible grade for the homework'
    )
    
    grade_percentage = fields.Float(
        string='Grade Percentage',
        compute='_compute_grade_percentage',
        store=True,
        help='Grade as percentage of maximum grade'
    )
    
    grade_letter = fields.Char(
        string='Letter Grade',
        compute='_compute_grade_letter',
        store=True,
        help='Letter grade based on percentage'
    )
    
    # Review Information
    review_date = fields.Datetime(
        string='Review Date',
        help='Date when homework was reviewed'
    )
    
    reviewed_by_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='User who reviewed the homework'
    )
    
    feedback = fields.Text(
        string='Feedback',
        help='Feedback provided by the reviewer'
    )
    
    # Attempt Information
    attempt_number = fields.Integer(
        string='Attempt Number',
        default=1,
        help='Number of attempts for this homework'
    )
    
    is_resubmission = fields.Boolean(
        string='Is Resubmission',
        default=False,
        help='Whether this is a resubmission'
    )
    
    previous_attempt_id = fields.Many2one(
        'gr.homework.attempt',
        string='Previous Attempt',
        help='Previous attempt if this is a resubmission'
    )
    
    # Computed Fields
    days_since_submission = fields.Integer(
        string='Days Since Submission',
        compute='_compute_days_since_submission',
        store=True,
        help='Number of days since submission'
    )
    
    processing_time = fields.Float(
        string='Processing Time (hours)',
        compute='_compute_processing_time',
        store=True,
        help='Time taken to process the submission'
    )
    
    def _compute_is_late(self):
        """Compute if submission is late."""
        for record in self:
            if record.submission_date and record.due_date:
                record.is_late = record.submission_date > record.due_date
            else:
                record.is_late = False
    
    def _compute_days_late(self):
        """Compute days late."""
        for record in self:
            if record.is_late and record.submission_date and record.due_date:
                delta = record.submission_date - record.due_date
                record.days_late = delta.days
            else:
                record.days_late = 0
    
    def _compute_grade_percentage(self):
        """Compute grade percentage."""
        for record in self:
            if record.grade and record.max_grade > 0:
                record.grade_percentage = (record.grade / record.max_grade) * 100
            else:
                record.grade_percentage = 0.0
    
    def _compute_grade_letter(self):
        """Compute letter grade."""
        for record in self:
            if record.grade_percentage >= 90:
                record.grade_letter = 'A'
            elif record.grade_percentage >= 80:
                record.grade_letter = 'B'
            elif record.grade_percentage >= 70:
                record.grade_letter = 'C'
            elif record.grade_percentage >= 60:
                record.grade_letter = 'D'
            else:
                record.grade_letter = 'F'
    
    def _compute_days_since_submission(self):
        """Compute days since submission."""
        for record in self:
            if record.submission_date:
                delta = fields.Datetime.now() - record.submission_date
                record.days_since_submission = delta.days
            else:
                record.days_since_submission = 0
    
    def _compute_processing_time(self):
        """Compute processing time."""
        for record in self:
            if record.submission_date and record.review_date:
                delta = record.review_date - record.submission_date
                record.processing_time = delta.total_seconds() / 3600  # Convert to hours
            else:
                record.processing_time = 0.0
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and attempt number."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.homework.attempt') or _('New')
        
        # Set attempt number if not provided
        if not vals.get('attempt_number'):
            student_id = vals.get('student_id')
            homework_title = vals.get('homework_title')
            if student_id and homework_title:
                existing_attempts = self.search([
                    ('student_id', '=', student_id),
                    ('homework_title', '=', homework_title)
                ])
                vals['attempt_number'] = len(existing_attempts) + 1
        
        homework_attempt = super(HomeworkAttempt, self).create(vals)
        
        # Log creation
        _logger.info('Homework attempt created: %s - Student: %s, Title: %s', 
                    homework_attempt.name, homework_attempt.student_id.name, homework_attempt.homework_title)
        
        return homework_attempt
    
    def action_submit(self):
        """Action to submit the homework."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft homework can be submitted.'))
        
        if not self.submission_content and not self.submission_file:
            raise UserError(_('Please provide submission content or file before submitting.'))
        
        self.state = 'submitted'
        self.submission_date = fields.Datetime.now()
        
        # Log submission
        _logger.info('Homework submitted: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Homework Submitted'),
                'message': _('Homework has been submitted for review.'),
                'type': 'success',
            }
        }
    
    def action_start_review(self):
        """Action to start homework review."""
        self.ensure_one()
        
        if self.state != 'submitted':
            raise UserError(_('Only submitted homework can be reviewed.'))
        
        self.state = 'under_review'
        self.review_date = fields.Datetime.now()
        self.reviewed_by_id = self.env.user
        
        # Log review start
        _logger.info('Homework review started: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Review Started'),
                'message': _('Homework review has been started.'),
                'type': 'info',
            }
        }
    
    def action_grade(self):
        """Action to grade the homework."""
        self.ensure_one()
        
        if self.state != 'under_review':
            raise UserError(_('Only homework under review can be graded.'))
        
        if not self.grade:
            raise UserError(_('Please provide a grade before completing the review.'))
        
        self.state = 'graded'
        self.review_date = fields.Datetime.now()
        self.reviewed_by_id = self.env.user
        
        # Log grading
        _logger.info('Homework graded: %s - Student: %s, Grade: %s', 
                    self.name, self.student_id.name, self.grade)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Homework Graded'),
                'message': _('Homework has been graded.'),
                'type': 'success',
            }
        }
    
    def action_return(self):
        """Action to return homework to student."""
        self.ensure_one()
        
        if self.state != 'graded':
            raise UserError(_('Only graded homework can be returned.'))
        
        self.state = 'returned'
        
        # Log return
        _logger.info('Homework returned: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Homework Returned'),
                'message': _('Homework has been returned to the student.'),
                'type': 'info',
            }
        }
    
    def action_resubmit(self):
        """Action to resubmit homework."""
        self.ensure_one()
        
        if self.state not in ['returned', 'graded']:
            raise UserError(_('Only returned or graded homework can be resubmitted.'))
        
        # Create new attempt
        new_attempt_vals = {
            'student_id': self.student_id.id,
            'homework_title': self.homework_title,
            'homework_description': self.homework_description,
            'homework_type': self.homework_type,
            'due_date': self.due_date,
            'attempt_number': self.attempt_number + 1,
            'is_resubmission': True,
            'previous_attempt_id': self.id,
            'state': 'draft',
        }
        
        new_attempt = self.create(new_attempt_vals)
        
        # Update current attempt
        self.state = 'resubmitted'
        
        # Log resubmission
        _logger.info('Homework resubmitted: %s - Student: %s, New attempt: %s', 
                    self.name, self.student_id.name, new_attempt.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Homework Resubmitted'),
                'message': _('New homework attempt has been created.'),
                'type': 'success',
            }
        }
    
    def action_reset(self):
        """Action to reset homework to draft."""
        self.ensure_one()
        self.state = 'draft'
        self.submission_date = False
        self.grade = 0.0
        self.review_date = False
        self.reviewed_by_id = False
        self.feedback = False
        
        # Log reset
        _logger.info('Homework reset: %s', self.name)
    
    @api.constrains('grade')
    def _check_grade(self):
        """Validate grade."""
        for record in self:
            if record.grade < 0:
                raise ValidationError(_('Grade cannot be negative.'))
            if record.grade > record.max_grade:
                raise ValidationError(_('Grade cannot exceed maximum grade.'))
    
    @api.constrains('due_date')
    def _check_due_date(self):
        """Validate due date."""
        for record in self:
            if record.due_date and record.due_date < fields.Datetime.now() - timedelta(days=30):
                raise ValidationError(_('Due date cannot be more than 30 days in the past.'))
    
    def name_get(self):
        """Custom name display for homework attempt records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.homework_title} ({record.student_id.name if record.student_id else 'No Student'})"
            result.append((record.id, name))
        return result
