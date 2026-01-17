# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectDocumentTemplate(models.Model):
    _name = 'project.document.template'
    _description = 'Project Document Template'
    _order = 'sequence, name'

    @classmethod
    def _valid_field_parameter(cls, field, name):
        """Allow tracking parameter for fields"""
        return super()._valid_field_parameter(field, name) or name == 'tracking'

    name = fields.Char('Template Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    # Template configuration
    template_type = fields.Selection([
        ('document_based', 'Document-Based'),
        ('checklist_based', 'Checklist-Based'),
        ('hybrid', 'Hybrid (Document + Checklist)')
    ], string='Template Type', required=True, default='document_based')
    
    # Document template lines
    document_template_line_ids = fields.One2many(
        'project.document.template.line', 'template_id',
        string='Document Template Lines'
    )
    
    # Checklist template lines
    checklist_template_line_ids = fields.One2many(
        'project.checklist.template.line', 'template_id',
        string='Checklist Template Lines'
    )
    
    # Application settings
    auto_apply = fields.Boolean('Auto-Apply', default=False, 
                               help='Automatically apply this template to new tasks')
    apply_to_projects = fields.Boolean('Apply to Projects', default=True)
    apply_to_tasks = fields.Boolean('Apply to Tasks', default=True)
    
    # Statistics
    document_count = fields.Integer('Document Count', compute='_compute_counts', store=True)
    checklist_count = fields.Integer('Checklist Count', compute='_compute_counts', store=True)
    usage_count = fields.Integer('Usage Count', compute='_compute_usage_count', store=True)
    
    @api.depends('document_template_line_ids', 'checklist_template_line_ids')
    def _compute_counts(self):
        for template in self:
            template.document_count = len(template.document_template_line_ids)
            template.checklist_count = len(template.checklist_template_line_ids)
    
    def _compute_usage_count(self):
        for template in self:
            # Count how many times this template has been applied
            usage_count = self.env['project.template.usage'].search_count([
                ('template_id', '=', template.id)
            ])
            template.usage_count = usage_count
    
    def action_apply_to_task(self, task):
        """Apply this template to a specific task"""
        self.ensure_one()
        
        # Create documents from template
        for line in self.document_template_line_ids:
            document_vals = {
                'name': line.name,
                'category': line.category,
                'priority': line.priority,
                'notes': line.notes,
                'res_model': 'project.task',
                'res_id': task.id,
                'linked_project_id': task.project_id.id,
                'status': 'draft',
                'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
            }
            self.env['documents.document'].create(document_vals)
        
        # Create checklist items from template
        for line in self.checklist_template_line_ids:
            checklist_vals = {
                'name': line.name,
                'description': line.description,
                'task_id': task.id,
                'sequence': line.sequence,
                'is_required': line.is_required,
            }
            self.env['project.checklist.item'].create(checklist_vals)
        
        # Record usage
        self.env['project.template.usage'].create({
            'template_id': self.id,
            'res_model': 'project.task',
            'res_id': task.id,
            'applied_by': self.env.user.id,
        })
        
        return True
    
    def action_preview_template(self):
        """Preview the template structure"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Preview'),
            'res_model': 'project.document.template',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project_templates_basic.view_project_document_template_preview').id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }
    
    def action_apply_template(self):
        """Open wizard to apply template to projects or tasks"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Apply Template'),
            'res_model': 'project.template.application',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_template_type': 'document',
            },
        }
