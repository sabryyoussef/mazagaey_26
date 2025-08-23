# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CreateProductFromTemplateWizard(models.TransientModel):
    _name = 'create.product.from.template.wizard'
    _description = 'Create Product from Template Wizard'

    template_id = fields.Many2one(
        'unified.product.template', string='Product Template',
        required=True, readonly=True
    )
    
    product_name = fields.Char('Product Name', required=True)
    description = fields.Text('Description')
    
    # Options
    create_documents = fields.Boolean('Create Documents', default=True, 
                                    help='Create documents from template')
    create_project = fields.Boolean('Create Project', default=True,
                                  help='Create project for the product')
    
    # Template information (readonly)
    template_type = fields.Selection(related='template_id.template_type', readonly=True)
    service_tracking = fields.Selection(related='template_id.service_tracking', readonly=True)
    document_count = fields.Integer(related='template_id.document_count', readonly=True)
    
    # Preview
    preview_documents = fields.Text('Document Preview', readonly=True)
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Update preview when template changes"""
        if self.template_id:
            self._update_preview()
    
    def _update_preview(self):
        """Update the document preview"""
        if not self.template_id:
            return
        
        preview_lines = []
        for line in self.template_id.document_template_line_ids:
            preview_lines.append(f"• {line.name} ({line.category}) - Priority: {line.priority}")
        
        if preview_lines:
            self.preview_documents = "\n".join(preview_lines)
        else:
            self.preview_documents = "No documents in template"
    
    def action_create_product(self):
        """Create the product from template"""
        self.ensure_one()
        
        try:
            # Create product from template
            product = self.template_id.create_product_from_template(
                product_name=self.product_name,
                description=self.description,
                create_documents=self.create_documents,
                create_project=self.create_project
            )
            
            # Show success message
            message = f"Product '{product.name}' created successfully!"
            
            if self.create_documents:
                message += f"\n• {len(product.document_ids)} documents created"
            
            if self.create_project and product.project_template_id:
                message += f"\n• Project '{product.project_template_id.name}' created"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Product Created'),
                    'message': message,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error(f"Error creating product from template: {e}")
            raise ValidationError(_('Failed to create product: %s') % str(e))
    
    def action_preview_template(self):
        """Preview the template details"""
        self.ensure_one()
        
        preview_info = f"""
Template: {self.template_id.name}
Type: {self.template_type}
Service Tracking: {self.service_tracking}
Document Count: {self.document_count}

Documents:
{self.preview_documents}
        """.strip()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Preview'),
                'message': preview_info,
                'type': 'info',
            }
        }
