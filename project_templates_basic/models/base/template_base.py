# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTemplateBase(models.AbstractModel):
    """
    Abstract base model for all project templates.
    Provides common functionality for checkpoint, document, checklist, and milestone templates.
    """
    _name = 'project.template.base'
    _description = 'Base Template Model'
    _order = 'sequence, name'
    _abstract = True

    # Basic Information
    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the template'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of the template'
    )
    template_type = fields.Selection([
        ('checkpoint', 'Checkpoint Template'),
        ('document', 'Document Template'),
        ('checklist', 'Checklist Template'),
        ('milestone', 'Milestone Template'),
        ('hybrid', 'Hybrid Template')
    ], string='Template Type', required=True, help='Type of template')
    
    # Application Settings
    auto_apply = fields.Boolean(
        string='Auto Apply',
        default=False,
        help='Automatically apply this template when creating new tasks/projects'
    )
    apply_to_tasks = fields.Boolean(
        string='Apply to Tasks',
        default=True,
        help='This template can be applied to individual tasks'
    )
    apply_to_projects = fields.Boolean(
        string='Apply to Projects',
        default=False,
        help='This template can be applied to entire projects'
    )
    apply_to_products = fields.Boolean(
        string='Apply to Products',
        default=False,
        help='This template can be applied to products for automatic application'
    )
    
    # Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of template in lists'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active and available for use'
    )
    
    # Statistics and Tracking
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_stats',
        store=False,
        help='Number of times this template has been applied'
    )
    last_used = fields.Datetime(
        string='Last Used',
        compute='_compute_usage_stats',
        store=False,
        help='When this template was last applied'
    )
    
    # Metadata
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        help='User who created this template'
    )
    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True,
        help='When this template was created'
    )
    updated_by = fields.Many2one(
        'res.users',
        string='Updated By',
        default=lambda self: self.env.user,
        help='User who last updated this template'
    )
    updated_date = fields.Datetime(
        string='Updated Date',
        default=fields.Datetime.now,
        help='When this template was last updated'
    )

    @api.depends('template_application_ids')
    def _compute_usage_stats(self):
        """Compute usage statistics for templates"""
        for template in self:
            applications = self.env['project.template.application'].search([
                ('template_id', '=', template.id)
            ])
            template.usage_count = len(applications)
            
            if applications:
                template.last_used = max(applications.mapped('applied_date'))
            else:
                template.last_used = False

    @api.constrains('template_type')
    def _check_template_type_consistency(self):
        """Ensure template type is consistent with model"""
        for template in self:
            if hasattr(template, '_template_type') and template._template_type:
                if template.template_type != template._template_type:
                    raise ValidationError(_(
                        'Template type must be consistent with the model type. '
                        'Expected: %s, Found: %s'
                    ) % (template._template_type, template.template_type))

    def action_apply_template(self, target_model, target_id):
        """
        Apply this template to a target (task, project, etc.)
        
        Args:
            target_model (str): Model name (e.g., 'project.task')
            target_id (int): ID of the target record
            
        Returns:
            dict: Action result for UI feedback
        """
        self.ensure_one()
        
        try:
            # Validate target exists
            target = self.env[target_model].browse(target_id)
            if not target.exists():
                raise ValidationError(_('Target record not found'))
            
            # Apply template based on type
            if self.template_type == 'checkpoint':
                result = self._apply_checkpoint_template(target)
            elif self.template_type == 'document':
                result = self._apply_document_template(target)
            elif self.template_type == 'checklist':
                result = self._apply_checklist_template(target)
            elif self.template_type == 'milestone':
                result = self._apply_milestone_template(target)
            elif self.template_type == 'hybrid':
                result = self._apply_hybrid_template(target)
            else:
                raise ValidationError(_('Unknown template type: %s') % self.template_type)
            
            # Record application
            self._record_template_application(target_model, target_id)
            
            return result
            
        except Exception as e:
            _logger.error('Error applying template %s: %s', self.name, str(e))
            raise ValidationError(_('Error applying template: %s') % str(e))

    def _apply_checkpoint_template(self, target):
        """Apply checkpoint template to target"""
        # To be implemented by checkpoint template model
        raise NotImplementedError(_('Checkpoint template application not implemented'))

    def _apply_document_template(self, target):
        """Apply document template to target"""
        # To be implemented by document template model
        raise NotImplementedError(_('Document template application not implemented'))

    def _apply_checklist_template(self, target):
        """Apply checklist template to target"""
        # To be implemented by checklist template model
        raise NotImplementedError(_('Checklist template application not implemented'))

    def _apply_milestone_template(self, target):
        """Apply milestone template to target"""
        # To be implemented by milestone template model
        raise NotImplementedError(_('Milestone template application not implemented'))

    def _apply_hybrid_template(self, target):
        """Apply hybrid template to target"""
        # To be implemented by hybrid template model
        raise NotImplementedError(_('Hybrid template application not implemented'))

    def _record_template_application(self, target_model, target_id):
        """Record template application for tracking"""
        self.env['project.template.application'].create({
            'template_id': self.id,
            'applied_to_model': target_model,
            'applied_to_id': target_id,
            'applied_by': self.env.user.id,
            'status': 'applied'
        })

    def action_view_applications(self):
        """View all applications of this template"""
        self.ensure_one()
        return {
            'name': _('Template Applications: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.template.application',
            'view_mode': 'list,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

    def action_duplicate_template(self):
        """Duplicate this template"""
        self.ensure_one()
        new_template = self.copy({
            'name': _('%s (Copy)') % self.name,
            'usage_count': 0,
            'last_used': False,
            'created_by': self.env.user.id,
            'created_date': fields.Datetime.now(),
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': new_template._name,
            'view_mode': 'form',
            'res_id': new_template.id,
            'target': 'current',
        }

    @api.model
    def get_available_templates(self, target_model, target_id=None):
        """
        Get available templates for a specific target
        
        Args:
            target_model (str): Model name
            target_id (int): Optional target ID for context
            
        Returns:
            recordset: Available templates
        """
        domain = [
            ('active', '=', True),
            ('template_type', '!=', False)
        ]
        
        # Filter by application type
        if target_model == 'project.task':
            domain.append(('apply_to_tasks', '=', True))
        elif target_model == 'project.project':
            domain.append(('apply_to_projects', '=', True))
        elif target_model == 'product.template':
            domain.append(('apply_to_products', '=', True))
        
        return self.search(domain, order='sequence, name')

    def write(self, vals):
        """Override write to track updates"""
        vals['updated_by'] = self.env.user.id
        vals['updated_date'] = fields.Datetime.now()
        return super().write(vals)
