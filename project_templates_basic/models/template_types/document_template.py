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
            'task_id': task.id,
            'applied_by': self.env.user.id,
        })
        
        return True
    
    def action_preview_template(self):
        """Open a preview of this template"""
        self.ensure_one()
        return {
            'name': _('Template Preview: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.document.template',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project_templates_basic.view_project_document_template_preview').id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }


class ProjectDocumentTemplateLine(models.Model):
    _name = 'project.document.template.line'
    _description = 'Project Document Template Line'
    _order = 'sequence'

    template_id = fields.Many2one('project.document.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Document Name', required=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', required=True, default='required')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    
    notes = fields.Text('Notes')
    tag_ids = fields.Many2many('documents.tag', string='Document Tags')


class ProjectChecklistTemplateLine(models.Model):
    _name = 'project.checklist.template.line'
    _description = 'Project Checklist Template Line'
    _order = 'sequence'

    template_id = fields.Many2one('project.document.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    is_required = fields.Boolean('Required', default=True)


class ProjectTemplateUsage(models.Model):
    _name = 'project.template.usage'
    _description = 'Project Template Usage History'
    _order = 'create_date desc'

    template_id = fields.Many2one('project.document.template', string='Template', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    applied_by = fields.Many2one('res.users', string='Applied By', required=True)
    applied_date = fields.Datetime('Applied Date', default=fields.Datetime.now)
    
    # Statistics
    documents_created = fields.Integer('Documents Created', compute='_compute_statistics', store=True)
    checklist_items_created = fields.Integer('Checklist Items Created', compute='_compute_statistics', store=True)
    
    @api.depends('template_id', 'task_id')
    def _compute_statistics(self):
        for usage in self:
            if usage.template_id and usage.task_id:
                usage.documents_created = len(usage.template_id.document_template_line_ids)
                usage.checklist_items_created = len(usage.template_id.checklist_template_line_ids)
            else:
                usage.documents_created = 0
                usage.checklist_items_created = 0


class ProjectChecklistItem(models.Model):
    _name = 'project.checklist.item'
    _description = 'Project Checklist Item'
    _order = 'sequence'

    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    is_required = fields.Boolean('Required', default=True)
    is_completed = fields.Boolean('Completed', default=False)
    completed_by = fields.Many2one('res.users', string='Completed By')
    completed_date = fields.Datetime('Completed Date')
    
    def action_toggle_completion(self):
        """Toggle the completion status of this checklist item"""
        self.ensure_one()
        if self.is_completed:
            self.write({
                'is_completed': False,
                'completed_by': False,
                'completed_date': False,
            })
        else:
            self.write({
                'is_completed': True,
                'completed_by': self.env.user.id,
                'completed_date': fields.Datetime.now(),
            })
        return True
