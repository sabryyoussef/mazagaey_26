from odoo import models, fields, api

class SmartCheckpointTemplate(models.Model):
    _name = 'smart.checkpoint.template'
    _description = 'Smart Checkpoint Template'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(string='Checkpoint Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Checkpoint-specific fields
    checkpoint_type = fields.Selection([
        ('quality_gate', 'Quality Gate'),
        ('compliance', 'Compliance Check'),
        ('approval', 'Approval Point'),
        ('documentation', 'Documentation Review'),
        ('deployment', 'Deployment Validation'),
        ('performance', 'Performance Check'),
        ('security', 'Security Audit'),
        ('other', 'Other')
    ], string='Checkpoint Type', default='quality_gate', required=True)
    
    validation_level = fields.Selection([
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], string='Validation Level', default='standard', required=True)
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Complexity Level', default='medium', required=True)
    
    # Compliance and approval fields
    compliance_required = fields.Boolean(string='Compliance Required', default=False)
    approval_required = fields.Boolean(string='Approval Required', default=False)
    compliance_standards = fields.Text(string='Compliance Standards')
    approval_workflow = fields.Text(string='Approval Workflow')
    
    # Validation criteria and methods
    validation_criteria = fields.Text(string='Validation Criteria')
    validation_method = fields.Selection([
        ('manual', 'Manual Review'),
        ('automated', 'Automated Check'),
        ('hybrid', 'Hybrid (Manual + Automated)')
    ], string='Validation Method', default='manual', required=True)
    
    success_criteria = fields.Text(string='Success Criteria')
    failure_actions = fields.Text(string='Failure Actions')
    
    # Required documentation and skills
    required_documents = fields.Text(string='Required Documents')
    required_skills = fields.Text(string='Required Skills')
    prerequisites = fields.Text(string='Prerequisites')
    
    # Timeline and scheduling
    estimated_duration_hours = fields.Float(string='Estimated Duration (Hours)')
    estimated_duration_days = fields.Integer(string='Estimated Duration (Days)')
    deadline_buffer_days = fields.Integer(string='Deadline Buffer (Days)', default=1)
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    auto_validate = fields.Boolean(string='Auto Validate', default=False)
    auto_escalate = fields.Boolean(string='Auto Escalate on Failure', default=False)
    
    # Usage statistics
    usage_count = fields.Integer(string='Usage Count', default=0)
    last_used = fields.Datetime(string='Last Used')
    
    # Template relationships
    project_template_ids = fields.Many2many(
        'smart.project.template',
        string='Project Templates'
    )
    
    task_template_ids = fields.Many2many(
        'smart.task.template',
        string='Task Templates'
    )
    
    # Computed fields
    total_projects = fields.Integer(
        string='Total Related Projects',
        compute='_compute_total_projects'
    )
    
    total_tasks = fields.Integer(
        string='Total Related Tasks',
        compute='_compute_total_tasks'
    )
    
    @api.depends('project_template_ids')
    def _compute_total_projects(self):
        for record in self:
            record.total_projects = len(record.project_template_ids)
    
    @api.depends('task_template_ids')
    def _compute_total_tasks(self):
        for record in self:
            record.total_tasks = len(record.task_template_ids)
    
    # Methods
    def apply_template(self):
        """Apply this checkpoint template to create a new checkpoint"""
        self.update_usage()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Create Checkpoint from {self.name}',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f'Checkpoint: {self.name}',
                'default_description': self.description,
                'template_id': self.id,
                'default_checkpoint_type': self.checkpoint_type
            }
        }
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()
    
    def get_suggestions(self):
        """Get suggested related checkpoint templates based on type and complexity"""
        domain = [
            ('checkpoint_type', '=', self.checkpoint_type),
            ('complexity_level', '=', self.complexity_level),
            ('id', '!=', self.id)
        ]
        return self.search(domain, limit=5)
    
    def view_related_projects(self):
        """View projects that use this checkpoint template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects using {self.name}',
            'res_model': 'smart.project.template',
            'view_mode': 'list,form',
            'domain': [('checkpoint_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def view_related_tasks(self):
        """View tasks that use this checkpoint template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks using {self.name}',
            'res_model': 'smart.task.template',
            'view_mode': 'list,form',
            'domain': [('checkpoint_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def validate_checkpoint(self):
        """Perform validation logic for this checkpoint"""
        # This method would contain the actual validation logic
        # For now, it's a placeholder for future implementation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Checkpoint Validation',
                'message': f'Validation completed for {self.name}',
                'type': 'success',
            }
        }