# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TrainingProgram(models.Model):
    _name = 'gr.training.program'
    _description = 'Training Program Definition'
    _order = 'name'

    name = fields.Char(
        string='Program Name',
        required=True,
        help='Name of the training program'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the training program'
    )
    
    # Program Structure
    course_integrations = fields.One2many(
        'gr.course.integration',
        'training_program_id',
        string='Course Integrations'
    )
    
    # Requirements
    eligibility_criteria = fields.Text(
        string='Eligibility Criteria',
        help='Specific criteria for this program'
    )
    
    duration_weeks = fields.Integer(
        string='Duration (Weeks)',
        help='Expected program duration in weeks'
    )
    
    # Certification
    # TODO: Create gr.certificate.template model in future phase
    # certificate_template_id = fields.Many2one(
    #     'gr.certificate.template',
    #     string='Certificate Template',
    #     help='Template to use for program completion certificates'
    # )
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    
    # Statistics
    total_courses = fields.Integer(
        string='Total Courses',
        compute='_compute_total_courses',
        store=True
    )
    
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
    
    # Computed fields
    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_completion_rate',
        store=True
    )
    
    @api.depends('course_integrations')
    def _compute_total_courses(self):
        """Compute total number of courses in the program."""
        for record in self:
            record.total_courses = len(record.course_integrations)
    
    @api.depends('course_integrations', 'course_integrations.enrolled_students')
    def _compute_enrolled_students(self):
        """Compute total enrolled students across all courses."""
        for record in self:
            record.enrolled_students = sum(
                course.enrolled_students for course in record.course_integrations
            )
    
    @api.depends('course_integrations', 'course_integrations.completed_students')
    def _compute_completed_students(self):
        """Compute total completed students across all courses."""
        for record in self:
            record.completed_students = sum(
                course.completed_students for course in record.course_integrations
            )
    
    @api.depends('enrolled_students', 'completed_students')
    def _compute_completion_rate(self):
        """Compute overall completion rate for the program."""
        for record in self:
            if record.enrolled_students > 0:
                record.completion_rate = (record.completed_students / record.enrolled_students) * 100
            else:
                record.completion_rate = 0.0
    
    @api.constrains('duration_weeks')
    def _check_duration_weeks(self):
        """Validate duration weeks."""
        for record in self:
            if record.duration_weeks and record.duration_weeks < 1:
                raise ValidationError(_('Duration must be at least 1 week.'))
    
    def action_activate(self):
        """Activate the training program."""
        for record in self:
            if record.status == 'draft':
                record.status = 'active'
                _logger.info('Training program activated: %s', record.name)
    
    def action_archive(self):
        """Archive the training program."""
        for record in self:
            if record.status == 'active':
                record.status = 'archived'
                _logger.info('Training program archived: %s', record.name)
    
    def action_enroll_eligible_students(self):
        """Enroll eligible students in all active courses."""
        for record in self:
            if record.status != 'active':
                continue
                
            total_enrolled = 0
            for course in record.course_integrations:
                if course.status == 'active' and course.auto_enroll_eligible:
                    result = course.action_enroll_eligible_students()
                    if result and 'params' in result:
                        # Extract enrolled count from message
                        message = result['params']['message']
                        # Simple extraction - could be improved
                        if 'enrolled' in message.lower():
                            total_enrolled += 1
            
            _logger.info('Enrolled students in program: %s', record.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Program Enrollment Complete'),
                    'message': _('Enrollment process completed for program: %s') % record.name,
                    'type': 'success',
                }
            }
    
    def action_generate_certificates(self):
        """Generate certificates for completed students."""
        for record in self:
            # TODO: Add certificate template validation when gr.certificate.template model is created
            # if not record.certificate_template_id:
            #     raise ValidationError(_('No certificate template configured for this program.'))
            
            # Get students who completed all courses
            completed_students = self._get_completed_students()
            
            certificates_created = 0
            for student in completed_students:
                # Check if certificate already exists
                existing_cert = self.env['gr.certificate'].search([
                    ('student_id', '=', student.id),
                    ('certificate_type', '=', 'program_completion'),
                    ('training_program_id', '=', record.id)
                ])
                
                if not existing_cert:
                    self.env['gr.certificate'].create({
                        'student_id': student.id,
                        'certificate_type': 'program_completion',
                        'training_program_id': record.id,
                        'state': 'draft'
                    })
                    certificates_created += 1
            
            _logger.info('Generated %d certificates for program: %s', certificates_created, record.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificates Generated'),
                    'message': _('Generated %d certificates for program: %s') % (certificates_created, record.name),
                    'type': 'success',
                }
            }
    
    def _get_completed_students(self):
        """Get students who have completed all courses in the program."""
        completed_students = []
        
        for record in self:
            # Get all students enrolled in any course of this program
            all_students = set()
            for course in record.course_integrations:
                for tracker in course.progress_trackers:
                    all_students.add(tracker.student_id.id)
            
            # Check each student's completion status
            for student_id in all_students:
                student = self.env['gr.student'].browse(student_id)
                all_courses_completed = True
                
                for course in record.course_integrations:
                    tracker = self.env['gr.progress.tracker'].search([
                        ('student_id', '=', student_id),
                        ('course_integration_id', '=', course.id)
                    ])
                    
                    if not tracker or tracker.status != 'completed':
                        all_courses_completed = False
                        break
                
                if all_courses_completed:
                    completed_students.append(student)
        
        return completed_students
