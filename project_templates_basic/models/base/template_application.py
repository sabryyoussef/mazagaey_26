# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTemplateApplication(models.Model):
    """
    Model to track template applications to tasks, projects, and products.
    Provides audit trail and usage statistics.
    """
    _name = 'project.template.application'
    _description = 'Template Application Tracking'
    _order = 'applied_date desc'
    _rec_name = 'display_name'

    # Template Information
    template_id = fields.Many2one(
        'project.template.base',
        string='Template',
        required=True,
        ondelete='cascade',
        help='Template that was applied'
    )
    template_name = fields.Char(
        string='Template Name',
        related='template_id.name',
        store=False,
        help='Name of the applied template'
    )
    template_type = fields.Selection(
        string='Template Type',
        related='template_id.template_type',
        store=False,
        help='Type of template that was applied'
    )
    
    # Target Information
    applied_to_model = fields.Char(
        string='Applied To Model',
        required=True,
        help='Model name of the target (e.g., project.task)'
    )
    applied_to_id = fields.Integer(
        string='Applied To ID',
        required=True,
        help='ID of the target record'
    )
    applied_to_name = fields.Char(
        string='Applied To Name',
        compute='_compute_applied_to_info',
        store=True,
        help='Name of the target record'
    )
    applied_to_display = fields.Char(
        string='Applied To',
        compute='_compute_applied_to_info',
        store=True,
        help='Display name of the target'
    )
    
    # Application Details
    applied_by = fields.Many2one(
        'res.users',
        string='Applied By',
        required=True,
        default=lambda self: self.env.user,
        help='User who applied the template'
    )
    applied_date = fields.Datetime(
        string='Applied Date',
        default=fields.Datetime.now,
        required=True,
        help='When the template was applied'
    )
    
    # Status and Progress
    status = fields.Selection([
        ('applied', 'Applied'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed')
    ], string='Status', default='applied', required=True, help='Current status of the application')
    
    completion_percentage = fields.Float(
        string='Completion %',
        default=0.0,
        help='Percentage of template items completed'
    )
    
    # Progress Tracking
    total_items = fields.Integer(
        string='Total Items',
        default=0,
        help='Total number of items in the template'
    )
    completed_items = fields.Integer(
        string='Completed Items',
        default=0,
        help='Number of completed items'
    )
    
    # Notes and Comments
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the template application'
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help='Display name for the application record'
    )
    
    # Related Fields for Easy Access
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        compute='_compute_related_records',
        store=True,
        help='Related project if applicable'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        compute='_compute_related_records',
        store=True,
        help='Related task if applicable'
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        compute='_compute_related_records',
        store=True,
        help='Related product if applicable'
    )

    @api.depends('applied_to_model', 'applied_to_id')
    def _compute_applied_to_info(self):
        """Compute target information"""
        for record in self:
            try:
                if record.applied_to_model and record.applied_to_id:
                    target = self.env[record.applied_to_model].browse(record.applied_to_id)
                    if target.exists():
                        record.applied_to_name = target.name if hasattr(target, 'name') else str(target.id)
                        record.applied_to_display = f"{record.applied_to_model.replace('.', ' ').title()}: {record.applied_to_name}"
                    else:
                        record.applied_to_name = f"Record {record.applied_to_id} (deleted)"
                        record.applied_to_display = f"{record.applied_to_model.replace('.', ' ').title()}: Record {record.applied_to_id} (deleted)"
                else:
                    record.applied_to_name = False
                    record.applied_to_display = False
            except Exception as e:
                _logger.error('Error computing applied_to_info: %s', str(e))
                record.applied_to_name = f"Error: {str(e)}"
                record.applied_to_display = f"Error computing target info"

    @api.depends('template_name', 'applied_to_display', 'applied_date')
    def _compute_display_name(self):
        """Compute display name for the record"""
        for record in self:
            if record.template_name and record.applied_to_display:
                record.display_name = f"{record.template_name} → {record.applied_to_display}"
            elif record.template_name:
                record.display_name = record.template_name
            else:
                record.display_name = f"Template Application {record.id}"

    @api.depends('applied_to_model', 'applied_to_id')
    def _compute_related_records(self):
        """Compute related record references"""
        for record in self:
            record.project_id = False
            record.task_id = False
            record.product_id = False
            
            try:
                if record.applied_to_model and record.applied_to_id:
                    target = self.env[record.applied_to_model].browse(record.applied_to_id)
                    if target.exists():
                        if record.applied_to_model == 'project.project':
                            record.project_id = target.id
                        elif record.applied_to_model == 'project.task':
                            record.task_id = target.id
                            if target.project_id:
                                record.project_id = target.project_id.id
                        elif record.applied_to_model == 'product.template':
                            record.product_id = target.id
            except Exception as e:
                _logger.error('Error computing related records: %s', str(e))

    @api.constrains('applied_to_model', 'applied_to_id')
    def _check_target_validity(self):
        """Ensure target model and ID are valid"""
        for record in self:
            if record.applied_to_model and record.applied_to_id:
                try:
                    target = self.env[record.applied_to_model].browse(record.applied_to_id)
                    if not target.exists():
                        raise ValidationError(_(
                            'Target record does not exist: %s (ID: %s)'
                        ) % (record.applied_to_model, record.applied_to_id))
                except Exception as e:
                    raise ValidationError(_(
                        'Invalid target model or ID: %s (ID: %s) - Error: %s'
                    ) % (record.applied_to_model, record.applied_to_id, str(e)))

    def action_view_target(self):
        """Open the target record"""
        self.ensure_one()
        if self.applied_to_model and self.applied_to_id:
            try:
                target = self.env[self.applied_to_model].browse(self.applied_to_id)
                if target.exists():
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': self.applied_to_model,
                        'view_mode': 'form',
                        'res_id': self.applied_to_id,
                        'target': 'current',
                    }
            except Exception as e:
                _logger.error('Error opening target: %s', str(e))
        
        return {'type': 'ir.actions.act_window_close'}

    def action_view_template(self):
        """Open the template record"""
        self.ensure_one()
        if self.template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.template_id._name,
                'view_mode': 'form',
                'res_id': self.template_id.id,
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}

    def action_update_progress(self):
        """Update progress for this application"""
        self.ensure_one()
        if self.template_id and self.applied_to_model and self.applied_to_id:
            try:
                target = self.env[self.applied_to_model].browse(self.applied_to_id)
                if target.exists():
                    # Calculate progress based on template type
                    progress_info = self._calculate_progress(target)
                    self.write({
                        'completion_percentage': progress_info['percentage'],
                        'total_items': progress_info['total'],
                        'completed_items': progress_info['completed'],
                        'status': progress_info['status']
                    })
            except Exception as e:
                _logger.error('Error updating progress: %s', str(e))

    def _calculate_progress(self, target):
        """Calculate progress for the template application"""
        # This will be implemented based on template type
        # For now, return default values
        return {
            'percentage': 0.0,
            'total': 0,
            'completed': 0,
            'status': 'applied'
        }

    @api.model
    def get_applications_for_target(self, target_model, target_id):
        """Get all template applications for a specific target"""
        return self.search([
            ('applied_to_model', '=', target_model),
            ('applied_to_id', '=', target_id)
        ], order='applied_date desc')

    @api.model
    def get_applications_by_template(self, template_id):
        """Get all applications of a specific template"""
        return self.search([
            ('template_id', '=', template_id)
        ], order='applied_date desc')

    def action_mark_completed(self):
        """Mark application as completed"""
        self.ensure_one()
        self.write({
            'status': 'completed',
            'completion_percentage': 100.0,
            'completed_items': self.total_items
        })

    def action_mark_cancelled(self):
        """Mark application as cancelled"""
        self.ensure_one()
        self.write({'status': 'cancelled'})

    def action_mark_failed(self):
        """Mark application as failed"""
        self.ensure_one()
        self.write({'status': 'failed'})

    @api.model
    def cleanup_orphaned_applications(self):
        """Clean up applications where target records no longer exist"""
        orphaned = self.search([])
        for app in orphaned:
            try:
                if app.applied_to_model and app.applied_to_id:
                    target = self.env[app.applied_to_model].browse(app.applied_to_id)
                    if not target.exists():
                        app.write({'status': 'failed'})
            except Exception as e:
                _logger.error('Error checking application %s: %s', app.id, str(e))
                app.write({'status': 'failed'})
