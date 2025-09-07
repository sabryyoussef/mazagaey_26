from odoo import models, fields, api

class SmartMilestoneTemplate(models.Model):
    _name = 'smart.milestone.template'
    _description = 'Smart Milestone Template'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(string='Milestone Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Milestone-specific fields
    milestone_type = fields.Selection([
        ('phase', 'Project Phase'),
        ('deliverable', 'Deliverable'),
        ('approval', 'Approval Point'),
        ('go_live', 'Go-Live'),
        ('review', 'Review Meeting'),
        ('testing', 'Testing Phase'),
        ('documentation', 'Documentation'),
        ('other', 'Other')
    ], string='Milestone Type', default='phase', required=True)
    
    priority_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority Level', default='medium', required=True)
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Complexity Level', default='medium', required=True)
    
    # Timeline fields
    estimated_duration_days = fields.Integer(string='Estimated Duration (Days)')
    estimated_duration_weeks = fields.Float(string='Estimated Duration (Weeks)')
    estimated_duration_months = fields.Float(string='Estimated Duration (Months)')
    buffer_days = fields.Integer(string='Buffer Days', default=1)
    deadline_type = fields.Selection([
        ('fixed', 'Fixed Deadline'),
        ('flexible', 'Flexible Deadline'),
        ('calculated', 'Calculated Deadline')
    ], string='Deadline Type', default='flexible', required=True)
    
    # Progress and status fields
    progress_tracking = fields.Selection([
        ('percentage', 'Percentage'),
        ('binary', 'Binary (Complete/Incomplete)'),
        ('stages', 'Stage-based'),
        ('milestone', 'Milestone-based')
    ], string='Progress Tracking', default='percentage', required=True)
    
    status_stages = fields.Text(string='Status Stages')
    completion_criteria = fields.Text(string='Completion Criteria')
    success_metrics = fields.Text(string='Success Metrics')
    failure_handling = fields.Text(string='Failure Handling')
    
    # Dependency fields
    has_dependencies = fields.Boolean(string='Has Dependencies', default=False)
    dependency_type = fields.Selection([
        ('prerequisite', 'Prerequisite'),
        ('blocking', 'Blocking'),
        ('parallel', 'Parallel'),
        ('sequential', 'Sequential')
    ], string='Dependency Type')
    
    dependency_description = fields.Text(string='Dependency Description')
    critical_path = fields.Boolean(string='Critical Path', default=False)
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='Risk Level', default='medium')
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    auto_schedule = fields.Boolean(string='Auto Schedule', default=False)
    auto_progress = fields.Boolean(string='Auto Progress', default=False)
    auto_notify = fields.Boolean(string='Auto Notify', default=False)
    
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
    
    checkpoint_template_ids = fields.Many2many(
        'smart.checkpoint.template',
        string='Checkpoint Templates'
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
    
    total_checkpoints = fields.Integer(
        string='Total Related Checkpoints',
        compute='_compute_total_checkpoints'
    )
    
    @api.depends('project_template_ids')
    def _compute_total_projects(self):
        for record in self:
            record.total_projects = len(record.project_template_ids)
    
    @api.depends('task_template_ids')
    def _compute_total_tasks(self):
        for record in self:
            record.total_tasks = len(record.task_template_ids)
    
    @api.depends('checkpoint_template_ids')
    def _compute_total_checkpoints(self):
        for record in self:
            record.total_checkpoints = len(record.checkpoint_template_ids)
    
    # Methods
    def apply_template(self):
        """Apply this milestone template to create a new milestone"""
        self.update_usage()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Create Milestone from {self.name}',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f'Milestone: {self.name}',
                'default_description': self.description,
                'template_id': self.id,
                'default_milestone_type': self.milestone_type
            }
        }
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()
    
    def get_suggestions(self):
        """Get suggested related milestone templates based on type and complexity"""
        domain = [
            ('milestone_type', '=', self.milestone_type),
            ('complexity_level', '=', self.complexity_level),
            ('id', '!=', self.id)
        ]
        return self.search(domain, limit=5)
    
    def view_related_projects(self):
        """View projects that use this milestone template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects using {self.name}',
            'res_model': 'smart.project.template',
            'view_mode': 'list,form',
            'domain': [('milestone_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def view_related_tasks(self):
        """View tasks that use this milestone template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks using {self.name}',
            'res_model': 'smart.task.template',
            'view_mode': 'list,form',
            'domain': [('milestone_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def view_related_checkpoints(self):
        """View checkpoints that use this milestone template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Checkpoints using {self.name}',
            'res_model': 'smart.checkpoint.template',
            'view_mode': 'list,form',
            'domain': [('milestone_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
    
    def calculate_timeline(self):
        """Calculate milestone timeline based on dependencies and constraints"""
        # This method would contain the actual timeline calculation logic
        # For now, it's a placeholder for future implementation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Timeline Calculation',
                'message': f'Timeline calculated for {self.name}',
                'type': 'success',
            }
        }
    
    def assess_dependencies(self):
        """Assess milestone dependencies and potential conflicts"""
        # This method would contain the actual dependency assessment logic
        # For now, it's a placeholder for future implementation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Dependency Assessment',
                'message': f'Dependencies assessed for {self.name}',
                'type': 'info',
            }
        }