# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CourseIntegration(models.Model):
    _name = 'gr.course.integration'
    _description = 'Course Integration between eLearning and Training Suite'
    _order = 'name'

    name = fields.Char(
        string='Integration Name',
        required=True,
        help='Name of the course integration'
    )
    
    # eLearning Course
    elearning_course_id = fields.Many2one(
        'slide.channel',
        string='eLearning Course',
        required=True,
        help='The eLearning course to integrate with'
    )
    
    # Training Program
    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        help='The training program this course belongs to'
    )
    
    # Integration Settings
    auto_enroll_eligible = fields.Boolean(
        string='Auto-enroll Eligible Students',
        default=True,
        help='Automatically enroll eligible students in this course'
    )
    
    completion_threshold = fields.Float(
        string='Completion Threshold (%)',
        default=100.0,
        help='Percentage required to consider course completed'
    )
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    
    # Statistics
    enrolled_students = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_students',
        store=True
    )
    
    completed_students = fields.Integer(
        string='Completed Students',
        compute='_compute_completed_students',
        store=True
    )
    
    # Progress tracking
    progress_trackers = fields.One2many(
        'gr.progress.tracker',
        'course_integration_id',
        string='Progress Trackers'
    )
    
    # Computed fields
    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_completion_rate',
        store=True
    )
    
    @api.depends('progress_trackers')
    def _compute_enrolled_students(self):
        """Compute number of enrolled students."""
        for record in self:
            record.enrolled_students = len(record.progress_trackers)
    
    @api.depends('progress_trackers', 'progress_trackers.status')
    def _compute_completed_students(self):
        """Compute number of completed students."""
        for record in self:
            record.completed_students = len(record.progress_trackers.filtered(
                lambda p: p.status == 'completed'
            ))
    
    @api.depends('enrolled_students', 'completed_students')
    def _compute_completion_rate(self):
        """Compute completion rate percentage."""
        for record in self:
            if record.enrolled_students > 0:
                record.completion_rate = (record.completed_students / record.enrolled_students) * 100
            else:
                record.completion_rate = 0.0
    
    @api.constrains('completion_threshold')
    def _check_completion_threshold(self):
        """Validate completion threshold."""
        for record in self:
            if record.completion_threshold < 0 or record.completion_threshold > 100:
                raise ValidationError(_('Completion threshold must be between 0 and 100.'))
    
    def action_activate(self):
        """Activate the course integration."""
        for record in self:
            if record.status == 'draft':
                record.status = 'active'
                _logger.info('Course integration activated: %s', record.name)
    
    def action_archive(self):
        """Archive the course integration."""
        for record in self:
            if record.status == 'active':
                record.status = 'archived'
                _logger.info('Course integration archived: %s', record.name)
    
    def action_enroll_eligible_students(self):
        """Enroll all eligible students in this course."""
        for record in self:
            if not record.auto_enroll_eligible:
                continue
                
            # Get eligible students
            eligible_students = self.env['gr.student'].search([
                ('state', 'in', ['eligible', 'assigned_to_agent'])
            ])
            
            enrolled_count = 0
            for student in eligible_students:
                # Check if already enrolled
                existing_tracker = self.env['gr.progress.tracker'].search([
                    ('student_id', '=', student.id),
                    ('course_integration_id', '=', record.id)
                ])
                
                if not existing_tracker:
                    # Create progress tracker
                    self.env['gr.progress.tracker'].create({
                        'student_id': student.id,
                        'course_integration_id': record.id,
                        'status': 'not_started'
                    })
                    enrolled_count += 1
            
            _logger.info('Enrolled %d eligible students in course: %s', enrolled_count, record.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Enrollment Complete'),
                    'message': _('Successfully enrolled %d students in %s') % (enrolled_count, record.name),
                    'type': 'success',
                }
            }
    
    def name_get(self):
        """Custom name display."""
        result = []
        for record in self:
            name = f"{record.name} ({record.elearning_course_id.name})"
            result.append((record.id, name))
        return result
