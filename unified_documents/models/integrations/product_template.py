# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _name = 'unified.product.template'
    _description = 'Unified Product Template'
    _order = 'sequence, name'

    name = fields.Char('Template Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    # Template configuration
    template_type = fields.Selection([
        ('document_based', 'Document-Based'),
        ('service_based', 'Service-Based'),
        ('hybrid', 'Hybrid (Document + Service)')
    ], string='Template Type', required=True, default='document_based')
    
    # Document template lines
    document_template_line_ids = fields.One2many(
        'unified.product.document.template.line', 'product_template_id',
        string='Document Template Lines'
    )
    
    # Service configuration
    service_tracking = fields.Selection([
        ('no', 'No Service'),
        ('project_only', 'Project Only'),
        ('task_in_project', 'Project and Task'),
        ('task_global_project', 'Task in Global Project')
    ], string='Service Tracking', default='task_in_project')
    
    # Project template relationship
    project_template_id = fields.Many2one(
        'project.project', string='Project Template',
        help='Linked project template for this product template'
    )
    
    # Task template relationship
    task_template_id = fields.Many2one(
        'project.task.template', string='Task Template',
        help='Linked task template for this product template'
    )
    
    # Statistics
    document_count = fields.Integer('Document Count', compute='_compute_counts', store=True)
    usage_count = fields.Integer('Usage Count', compute='_compute_usage_count', store=True)
    
    @api.depends('document_template_line_ids')
    def _compute_counts(self):
        for template in self:
            template.document_count = len(template.document_template_line_ids)
    
    def _compute_usage_count(self):
        for template in self:
            # Count how many times this template has been applied
            usage_count = self.env['unified.product.template.usage'].search_count([
                ('template_id', '=', template.id)
            ])
            template.usage_count = usage_count
    
    def action_apply_to_product(self, product):
        """Apply this template to a specific product"""
        self.ensure_one()
        
        # Check if product is valid
        if not product or not product.exists():
            raise ValidationError(_('Invalid product provided for template application.'))
        
        # Create documents from template
        created_docs = []
        for line in self.document_template_line_ids:
            try:
                document_vals = {
                    'name': line.name,
                    'category': line.category,
                    'priority': line.priority,
                    'notes': line.notes,
                    'linked_product_id': product.id,
                    'status': 'draft',
                    'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                }
                new_doc = self.env['documents.document'].create(document_vals)
                created_docs.append(new_doc)
            except Exception as e:
                _logger.warning(f"Failed to create document '{line.name}' for product {product.name}: {e}")
                continue
        
        # Check if usage record already exists
        existing_usage = self.env['unified.product.template.usage'].search([
            ('template_id', '=', self.id),
            ('product_id', '=', product.id)
        ], limit=1)
        
        # Record usage only if it doesn't exist
        if not existing_usage:
            try:
                usage_vals = {
                    'template_id': self.id,
                    'product_id': product.id,
                    'applied_by': self.env.user.id,
                    'notes': f"Template applied with {len(created_docs)} documents created"
                }
                self.env['unified.product.template.usage'].create(usage_vals)
            except Exception as e:
                _logger.warning(f"Failed to create usage record for template {self.name} and product {product.name}: {e}")
        
        return True
    
    def action_create_project_template(self):
        """Create a project template for this product template"""
        self.ensure_one()
        
        if self.project_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Project Template Exists'),
                    'message': _('This product template already has a project template.'),
                    'type': 'warning',
                }
            }
        
        # Create project template with enhanced configuration
        project_vals = {
            'name': f"{self.name} - Project Template",
            'description': f"Auto-generated project template for {self.name}",
            'is_template': True,
            'template_category': self._map_template_category(),
            'template_description': self.description,
            'estimated_duration': self._estimate_project_duration(),
            'complexity_level': self._determine_complexity_level(),
        }
        
        # Add timesheet fields if available
        if 'allow_timesheets' in self.env['project.project']._fields:
            project_vals['allow_timesheets'] = True
        if 'allow_billable' in self.env['project.project']._fields:
            project_vals['allow_billable'] = True
        
        project_template = self.env['project.project'].create(project_vals)
        self.project_template_id = project_template.id
        
        # Auto-link related templates based on category
        self._auto_link_related_templates(project_template)
        
        # Copy document template lines to project template
        self._copy_document_template_lines_to_project_template(project_template)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Project Template Created'),
                'message': _('Project template has been created successfully with auto-linked templates.'),
                'type': 'success',
            }
        }
    
    def _map_template_category(self):
        """Map product template type to project template category"""
        category_mapping = {
            'document_based': 'general',
            'service_based': 'general',
            'hybrid': 'general'
        }
        
        # Enhanced mapping based on template name and description
        name_lower = self.name.lower()
        if any(keyword in name_lower for keyword in ['company', 'formation', 'setup', 'incorporation']):
            return 'company_formation'
        elif any(keyword in name_lower for keyword in ['visa', 'permit', 'immigration']):
            return 'visa_services'
        elif any(keyword in name_lower for keyword in ['government', 'official', 'authority']):
            return 'government_services'
        elif any(keyword in name_lower for keyword in ['bank', 'financial', 'account', 'payment']):
            return 'financial_services'
        else:
            return category_mapping.get(self.template_type, 'general')
    
    def _estimate_project_duration(self):
        """Estimate project duration based on document count and complexity"""
        base_duration = 5  # Base 5 days
        document_factor = len(self.document_template_line_ids) * 2  # 2 days per document
        complexity_factor = {
            'simple': 0,
            'medium': 5,
            'complex': 10,
            'very_complex': 15
        }.get(self._determine_complexity_level(), 5)
        
        return base_duration + document_factor + complexity_factor
    
    def _determine_complexity_level(self):
        """Determine complexity level based on template characteristics"""
        doc_count = len(self.document_template_line_ids)
        has_high_priority = any(line.priority == '2' for line in self.document_template_line_ids)
        
        if doc_count > 10 or has_high_priority:
            return 'complex'
        elif doc_count > 5:
            return 'medium'
        else:
            return 'simple'
    
    def _auto_link_related_templates(self, project_template):
        """Auto-link related task and checkpoint templates based on category"""
        category = project_template.template_category
        
        # Link task templates
        task_template_domain = self._get_task_template_domain(category)
        task_templates = self.env['project.document.template'].search(task_template_domain)
        if task_templates:
            project_template.related_task_templates = [(6, 0, task_templates.ids)]
        
        # Link checkpoint templates (if available)
        try:
            checkpoint_template_domain = self._get_checkpoint_template_domain(category)
            checkpoint_templates = self.env['project.task.checkpoint.template'].search(checkpoint_template_domain)
            if checkpoint_templates:
                project_template.related_checkpoint_templates = [(6, 0, checkpoint_templates.ids)]
        except Exception as e:
            # Checkpoint templates might not be available, log and continue
            _logger.warning(f"Could not link checkpoint templates: {e}")
            pass
    
    def _copy_document_template_lines_to_project_template(self, project_template):
        """Copy document template lines from product template to project template"""
        if not self.document_template_line_ids:
            return
        
        # Create documents directly in the project template
        for line in self.document_template_line_ids:
            document_vals = {
                'name': line.name,
                'description': line.description,
                'category': line.category,
                'priority': line.priority,
                'notes': line.notes,
                'res_model': 'project.project',
                'res_id': project_template.id,
                'linked_project_id': project_template.id,
                'status': 'draft',
                'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
            }
            self.env['documents.document'].create(document_vals)
    
    def _get_task_template_domain(self, category):
        """Get domain for task templates based on category"""
        # For now, return all active templates since template_type field doesn't exist
        # This can be enhanced later when template categorization is implemented
        return [('active', '=', True)]
    
    def _get_checkpoint_template_domain(self, category):
        """Get domain for checkpoint templates based on category"""
        # For now, return all active templates since template_type field doesn't exist
        # This can be enhanced later when template categorization is implemented
        return [('active', '=', True)]
    
    def action_view_project_template(self):
        """Open the project template"""
        self.ensure_one()
        if self.project_template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.project_template_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False
    
    def action_view_relationships(self):
        """Show all relationships for this product template"""
        self.ensure_one()
        
        # Get related data
        project_template = self.project_template_id
        task_templates = project_template.related_task_templates if project_template else False
        checkpoint_templates = project_template.related_checkpoint_templates if project_template else False
        
        # Create relationship summary
        relationships = []
        
        if project_template:
            relationships.append(f"📋 Project Template: {project_template.name}")
            relationships.append(f"   Category: {project_template.template_category}")
            relationships.append(f"   Complexity: {project_template.complexity_level}")
            relationships.append(f"   Duration: {project_template.estimated_duration} days")
            
            if task_templates:
                relationships.append(f"📄 Task Templates: {len(task_templates)} templates")
                for tt in task_templates:
                    # Check if this is a document template created from this product template
                    if tt.name.startswith(f"{self.name} - Document Template"):
                        relationships.append(f"   • {tt.name} (document_based) - Created from product template")
                    else:
                        relationships.append(f"   • {tt.name} ({tt.template_type})")
            else:
                relationships.append("📄 Task Templates: None linked")
            
            if checkpoint_templates:
                relationships.append(f"✅ Checkpoint Templates: {len(checkpoint_templates)} templates")
                for ct in checkpoint_templates:
                    relationships.append(f"   • {ct.name}")
            else:
                relationships.append("✅ Checkpoint Templates: None available")
        else:
            relationships.append("📋 Project Template: Not created yet")
            relationships.append("   Click 'Create Project Template' to create one")
        
        # Add document template lines information
        if self.document_template_line_ids:
            relationships.append(f"📋 Document Template Lines: {len(self.document_template_line_ids)} lines")
            for line in self.document_template_line_ids[:5]:  # Show first 5
                relationships.append(f"   • {line.name} ({line.category})")
            if len(self.document_template_line_ids) > 5:
                relationships.append(f"   ... and {len(self.document_template_line_ids) - 5} more")
        
        # Show relationships in a notification
        message = "\n".join(relationships) if relationships else "No relationships found."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Relationships - %s') % self.name,
                'message': message,
                'type': 'info',
            }
        }
    
    def action_view_document_lines(self):
        """Open document template lines view"""
        self.ensure_one()
        return {
            'name': _('Document Template Lines - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'unified.product.document.template.line',
            'view_mode': 'list,form',
            'domain': [('product_template_id', '=', self.id)],
            'context': {
                'default_product_template_id': self.id,
            },
        }
    
    def action_view_usage(self):
        """Open template usage view"""
        self.ensure_one()
        return {
            'name': _('Template Usage - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'unified.product.template.usage',
            'view_mode': 'list,form',
            'domain': [('template_id', '=', self.id)],
            'context': {
                'default_template_id': self.id,
            },
        }
    
    def action_view_created_products(self):
        """Show all products created from this template"""
        self.ensure_one()
        
        # Find products created from this template
        usage_records = self.env['unified.product.template.usage'].search([
            ('template_id', '=', self.id)
        ])
        
        product_ids = usage_records.mapped('product_id.id')
        
        if product_ids:
            return {
                'name': _('Products Created from Template - %s') % self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'view_mode': 'list,form',
                'domain': [('id', 'in', product_ids)],
                'context': {
                    'default_name': self.name,
                },
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Products Created'),
                    'message': _('No products have been created from this template yet.'),
                    'type': 'info',
                }
            }

    def action_view_selected_task_template(self):
        """Open the selected task template"""
        self.ensure_one()
        
        if not self.task_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Template Selected'),
                    'message': _('No task template is selected for this product template.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'res_id': self.task_template_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_task_template(self):
        """Create a new task template for this product template"""
        self.ensure_one()
        
        return {
            'name': _('Create Task Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Task Template",
                'default_description': f"Task template for {self.name} product template",
            },
        }
    
    def action_copy_documents_to_project_template(self):
        """Copy document template lines to the linked project template"""
        self.ensure_one()
        
        if not self.project_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Project Template'),
                    'message': _('Please create a project template first.'),
                    'type': 'warning',
                }
            }
        
        if not self.document_template_line_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Document Lines'),
                    'message': _('This product template has no document template lines to copy.'),
                    'type': 'warning',
                }
            }
        
        # Copy document template lines to project template
        self._copy_document_template_lines_to_project_template(self.project_template_id)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Documents Copied'),
                'message': _('Document template lines have been copied to the project template successfully.'),
                'type': 'success',
            }
        }
    
    def action_auto_link_templates(self):
        """Auto-link product templates with project templates"""
        linked_count = 0
        created_count = 0
        error_count = 0
        
        for template in self:
            try:
                if not template.project_template_id:
                    # Try to find existing project template
                    existing_project = template._find_matching_project_template()
                    if existing_project:
                        template.project_template_id = existing_project.id
                        linked_count += 1
                    else:
                        # Create new project template
                        template.action_create_project_template()
                        created_count += 1
            except Exception as e:
                error_count += 1
                _logger.error(f"Error auto-linking template {template.name}: {e}")
        
        message = _('Linked %d templates, created %d new project templates.') % (linked_count, created_count)
        if error_count > 0:
            message += _(' %d templates had errors.') % error_count
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Linking Complete'),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
            }
        }
    
    def _find_matching_project_template(self):
        """Find matching project template based on category and name"""
        category = self._map_template_category()
        name_keywords = self.name.lower().split()
        
        # Search for project templates with similar category and name
        project_templates = self.env['project.project'].search([
            ('is_template', '=', True),
            ('template_category', '=', category)
        ])
        
        # Find best match based on name similarity
        best_match = None
        best_score = 0
        
        for pt in project_templates:
            pt_name_lower = pt.name.lower()
            score = sum(1 for keyword in name_keywords if keyword in pt_name_lower)
            if score > best_score:
                best_score = score
                best_match = pt
        
        return best_match if best_score > 0 else None
    
    def action_create_product_from_template(self):
        """Create a new product from this template"""
        self.ensure_one()
        return {
            'name': _('Create Product from Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'create.product.from.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_product_name': self.name,
                'default_description': self.description,
            },
        }
    
    def create_product_from_template(self, product_name=None, description=None, 
                                   create_documents=True, create_project=True):
        """Create a new product from this template"""
        self.ensure_one()
        
        # Prepare product values
        product_vals = {
            'name': product_name or f"{self.name} - Product",
            'description': description or self.description,
            'type': 'service',
            'service_tracking': self.service_tracking,
            'sale_ok': True,
            'purchase_ok': False,
        }
        
        # Create the product
        product = self.env['product.template'].create(product_vals)
        
        # Create documents from template if requested
        if create_documents:
            self.action_apply_to_product(product)
        
        # Create project if requested and service tracking is enabled
        if create_project and self.service_tracking != 'no':
            project = self._create_project_from_template(product)
            if project:
                # Link project to product
                product.write({
                    'project_template_id': project.id,
                })
        
        # Record usage
        self.env['unified.product.template.usage'].create({
            'template_id': self.id,
            'product_id': product.id,
            'applied_by': self.env.user.id,
            'notes': f"Product created from template: {product.name}",
        })
        
        return product
    
    def _create_project_from_template(self, product):
        """Create a project from template with documents and tasks"""
        if not self.project_template_id:
            # Create project template first
            self.action_create_project_template()
        
        if not self.project_template_id:
            return False
        
        # Create project from template
        project_vals = {
            'name': f"{product.name} - Project",
            'description': f"Project for {product.name}",
            'partner_id': False,  # Will be set when sold
            'user_id': self.env.user.id,
            'is_template': False,  # This is a real project, not a template
        }
        
        # Add timesheet fields if available
        if 'allow_timesheets' in self.env['project.project']._fields:
            project_vals['allow_timesheets'] = True
        if 'allow_billable' in self.env['project.project']._fields:
            project_vals['allow_billable'] = True
        
        project = self.env['project.project'].create(project_vals)
        
        # Copy documents to project
        self._copy_documents_to_project(product, project)
        
        # Apply task templates if available
        if self.project_template_id.related_task_templates:
            self._apply_task_templates_to_project(project)
        
        # Apply checkpoint templates if available
        if self.project_template_id.related_checkpoint_templates:
            self._apply_checkpoint_templates_to_project(project)
        
        return project
    
    def _copy_documents_to_project(self, product, project):
        """Copy product documents to project"""
        for document in product.document_ids:
            new_document = document.copy({
                'res_model': 'project.project',
                'res_id': project.id,
                'linked_project_id': project.id,
                'linked_product_id': False,  # Remove product link
            })
    
    def _apply_task_templates_to_project(self, project):
        """Apply task templates to project"""
        for task_template in self.project_template_id.related_task_templates:
            task_vals = {
                'name': task_template.name,
                'description': task_template.description,
                'project_id': project.id,
                'user_id': self.env.user.id,
                'priority': task_template.priority,
            }
            
            task = self.env['project.task'].create(task_vals)
            
            # Copy task documents if any
            if hasattr(task_template, 'document_ids') and task_template.document_ids:
                for doc in task_template.document_ids:
                    doc.copy({
                        'res_model': 'project.task',
                        'res_id': task.id,
                        'linked_task_id': task.id,
                    })
    
    def _apply_checkpoint_templates_to_project(self, project):
        """Apply checkpoint templates to project tasks"""
        for checkpoint_template in self.project_template_id.related_checkpoint_templates:
            # Find appropriate task to attach checkpoint to
            task = self._find_appropriate_task_for_checkpoint(project, checkpoint_template)
            
            if task:
                checkpoint_vals = {
                    'name': checkpoint_template.name,
                    'description': checkpoint_template.description,
                    'task_id': task.id,
                    'priority': checkpoint_template.priority,
                    'status': 'pending',
                }
                
                self.env['project.task.checkpoint'].create(checkpoint_vals)
    
    def _find_appropriate_task_for_checkpoint(self, project, checkpoint_template):
        """Find the most appropriate task to attach checkpoint to"""
        # Simple logic: find first task or create a default one
        if project.task_ids:
            return project.task_ids[0]
        else:
            # Create a default task if none exists
            task_vals = {
                'name': 'Main Task',
                'project_id': project.id,
                'user_id': self.env.user.id,
            }
            return self.env['project.task'].create(task_vals)


class ProductDocumentTemplateLine(models.Model):
    _name = 'unified.product.document.template.line'
    _description = 'Product Document Template Line'
    _order = 'sequence, name'

    name = fields.Char('Document Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    
    product_template_id = fields.Many2one(
        'unified.product.template', string='Product Template',
        required=True, ondelete='cascade'
    )
    
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


class ProductTemplateUsage(models.Model):
    _name = 'unified.product.template.usage'
    _description = 'Product Template Usage Tracking'
    _order = 'create_date desc'

    template_id = fields.Many2one(
        'unified.product.template', string='Product Template',
        required=True, ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.template', string='Product',
        required=True, ondelete='cascade'
    )
    
    applied_by = fields.Many2one(
        'res.users', string='Applied By',
        required=True, default=lambda self: self.env.user
    )
    
    applied_date = fields.Datetime(
        'Applied Date', default=fields.Datetime.now
    )
    
    notes = fields.Text('Notes')
