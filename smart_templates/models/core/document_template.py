# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartDocumentTemplate(models.Model):
    _name = 'smart.document.template'
    _description = 'Smart Document Template'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Document-specific fields
    document_type = fields.Selection([
        ('technical_spec', 'Technical Specification'),
        ('user_manual', 'User Manual'),
        ('api_documentation', 'API Documentation'),
        ('project_proposal', 'Project Proposal'),
        ('requirements_doc', 'Requirements Document'),
        ('design_document', 'Design Document'),
        ('test_plan', 'Test Plan'),
        ('deployment_guide', 'Deployment Guide'),
        ('troubleshooting', 'Troubleshooting Guide'),
        ('compliance_doc', 'Compliance Document'),
        ('contract', 'Contract'),
        ('report', 'Report'),
        ('presentation', 'Presentation'),
        ('other', 'Other')
    ], string='Document Type', default='technical_spec', required=True)
    
    document_format = fields.Selection([
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('rst', 'reStructuredText'),
        ('txt', 'Plain Text'),
        ('xml', 'XML'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
        ('other', 'Other')
    ], string='Document Format', default='pdf', required=True)
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Complexity Level', default='medium', required=True)
    
    # Document content and structure
    template_content = fields.Html(string='Template Content')
    document_structure = fields.Text(string='Document Structure')
    required_sections = fields.Text(string='Required Sections')
    optional_sections = fields.Text(string='Optional Sections')
    
    # Document requirements
    required_skills = fields.Text(string='Required Skills')
    prerequisites = fields.Text(string='Prerequisites')
    target_audience = fields.Text(string='Target Audience')
    
    # Document workflow
    review_required = fields.Boolean(string='Review Required', default=True)
    approval_required = fields.Boolean(string='Approval Required', default=False)
    version_control = fields.Boolean(string='Version Control', default=True)
    
    # Document lifecycle
    lifecycle_stage = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Lifecycle Stage', default='draft')
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    auto_generate = fields.Boolean(string='Auto Generate', default=False)
    auto_update = fields.Boolean(string='Auto Update', default=False)
    
    # Usage statistics
    usage_count = fields.Integer(string='Usage Count', default=0)
    last_used = fields.Datetime(string='Last Used')
    
    # Template relationships
    project_template_ids = fields.Many2many(
        'smart.project.template',
        string='Project Templates'
    )
    
    # Computed fields
    total_projects = fields.Integer(
        string='Total Related Projects',
        compute='_compute_total_projects'
    )
    
    @api.depends('project_template_ids')
    def _compute_total_projects(self):
        for record in self:
            record.total_projects = len(record.project_template_ids)
    
    # Methods
    def apply_template(self):
        """Apply this template to create a new document"""
        # Update usage statistics
        self.update_usage()
        
        # This will be implemented to create actual documents
        return {
            'type': 'ir.actions.act_window',
            'name': f'Create Document from {self.name}',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_description': self.description,
                'template_id': self.id
            }
        }
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()
    
    def get_suggestions(self):
        """Get suggested related templates based on document type and complexity"""
        domain = [
            ('document_type', '=', self.document_type),
            ('complexity_level', '=', self.complexity_level),
            ('id', '!=', self.id)
        ]
        return self.search(domain, limit=5)
    
    def view_related_projects(self):
        """View projects that use this document template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects using {self.name}',
            'res_model': 'smart.project.template',
            'view_mode': 'list,form',
            'domain': [('document_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def preview_template(self):
        """Preview the document template content"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Preview: {self.name}',
            'res_model': 'smart.document.template',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'preview_mode': True}
        }
