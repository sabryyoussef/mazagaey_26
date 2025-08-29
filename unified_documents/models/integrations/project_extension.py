# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Document relationships (One2many fields)
    document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        string='Documents'
    )
    required_document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        domain=[('category', '=', 'required')],
        string='Required Documents'
    )
    deliverable_document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        domain=[('category', '=', 'deliverable')],
        string='Deliverable Documents'
    )

    # Document count fields
    document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Total Documents'
    )
    required_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Required Document Count'
    )
    deliverable_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Deliverable Document Count'
    )

    # Document Template Selection Field
    document_template_id = fields.Many2one(
        'project.document.template', 
        string='Document Template',
        help='Select a document template to automatically add template documents to this project'
    )

    # Temporary fields for document creation
    new_document_name = fields.Char('Document Name')
    
    # Document name field for compatibility with other modules
    document_name = fields.Char(
        string='Document Name', 
        compute='_compute_document_name',
        store=False,
        help='Document name for compatibility with other modules'
    )
    new_document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', default='required')
    new_document_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    new_document_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('delivered', 'Delivered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    new_document_expiry_date = fields.Date('Expiry Date')
    new_document_notes = fields.Text('Notes')
    new_document_tag_ids = fields.Many2many('documents.tag', string='Document Tags')
    


    documents_folder_id = fields.Many2one(
        'documents.document', 
        string='Documents Folder',
        help='Documents folder for this project in the Documents module'
    )
    
    project_files_count = fields.Integer(
        compute='_compute_project_files_count',
        string='Project Files',
        help='Number of files in the project folder'
    )
    
    project_folder_files = fields.Many2many(
        'ir.attachment',
        compute='_compute_project_folder_files',
        string='Project Folder Files',
        help='Files in the project documents folder'
    )
    
    # Note: Template functionality has been moved to project_templates_basic module

    # Task Template Selection Field (for project templates)
    task_template_id = fields.Many2one(
        'project.task.template', 
        string='Task Template',
        help='Select a task template to automatically add template tasks to this project template'
    )
    

    
    # Milestone Template Selection Field (for project templates)
    milestone_template_ids = fields.Many2many(
        'project.milestone.template', 
        'project_milestone_template_rel',
        'project_id', 'milestone_template_id',
        string='Milestone Templates',
        help='Select milestone templates to automatically add template milestones to this project template'
    )

    @api.depends('document_ids', 'required_document_ids', 'deliverable_document_ids')
    def _compute_document_counts(self):
        """Compute document counts for projects"""
        for project in self:
            project.document_count = len(project.document_ids)
            project.required_document_count = len(project.required_document_ids)
            project.deliverable_document_count = len(project.deliverable_document_ids)

    @api.onchange('document_template_id')
    def _onchange_document_template_id(self):
        """Show warning when a document template is selected"""
        if self.document_template_id:
            # Don't apply template during onchange, just show a warning
            return {
                'warning': {
                    'title': _('Template Selected'),
                    'message': _('Document template "%s" has been selected. Save the project to apply the template documents, or use the "Apply Template" button to apply immediately.') % self.document_template_id.name,
                }
            }



    @api.depends('new_document_name', 'document_ids')
    def _compute_document_name(self):
        """Compute document name for compatibility with other modules"""
        for project in self:
            if project.new_document_name:
                project.document_name = project.new_document_name
            elif project.document_ids:
                project.document_name = project.document_ids[0].name
            else:
                project.document_name = project.name or ''

    @api.depends('document_ids', 'documents_folder_id')
    def _compute_project_files_count(self):
        """Compute the number of files linked to project documents or folder"""
        for project in self:
            file_count = 0
            
            # First try to count files from project folder
            if project.documents_folder_id:
                folder_documents = self.env['documents.document'].search([
                    ('folder_id', '=', project.documents_folder_id.id)
                ])
                if folder_documents:
                    file_count = self.env['ir.attachment'].search_count([
                        ('res_model', '=', 'documents.document'),
                        ('res_id', 'in', folder_documents.ids)
                    ])
            
            # Fallback to project documents
            if file_count == 0 and project.document_ids:
                file_count = self.env['ir.attachment'].search_count([
                    ('res_model', '=', 'documents.document'),
                    ('res_id', 'in', project.document_ids.ids)
                ])
            
            # Final fallback to direct project attachments
            if file_count == 0:
                file_count = self.env['ir.attachment'].search_count([
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', project.id)
                ])
                
            project.project_files_count = file_count

    @api.depends('document_ids', 'documents_folder_id')
    def _compute_project_folder_files(self):
        """Compute the files linked to project documents or folder"""
        for project in self:
            files = self.env['ir.attachment']
            
            # First try to get files from project folder
            if project.documents_folder_id:
                folder_documents = self.env['documents.document'].search([
                    ('folder_id', '=', project.documents_folder_id.id)
                ])
                if folder_documents:
                    files = self.env['ir.attachment'].search([
                        ('res_model', '=', 'documents.document'),
                        ('res_id', 'in', folder_documents.ids)
                    ])
            
            # Fallback to project documents
            if not files and project.document_ids:
                files = self.env['ir.attachment'].search([
                    ('res_model', '=', 'documents.document'),
                    ('res_id', 'in', project.document_ids.ids)
                ])
            
            # Final fallback to direct project attachments
            if not files:
                files = self.env['ir.attachment'].search([
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', project.id)
                ])
                
            project.project_folder_files = files
    
    def action_fix_document_linking(self):
        """Fix document linking for documents in project folder that are not properly linked"""
        self.ensure_one()
        
        if not self.documents_folder_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project has no documents folder.'),
                    'type': 'warning',
                }
            }
        
        # Find documents in the folder that are not linked to this project
        unlinked_docs = self.env['documents.document'].search([
            ('folder_id', '=', self.documents_folder_id.id),
            '|',
            ('linked_project_id', '=', False),
            ('linked_project_id', '!=', self.id),
            ('type', '!=', 'folder')  # Exclude the folder itself
        ])
        
        # Also get all documents in folder for comparison
        all_folder_docs = self.env['documents.document'].search([
            ('folder_id', '=', self.documents_folder_id.id),
            ('type', '!=', 'folder')
        ])
        
        linked_docs = all_folder_docs.filtered(lambda d: d.linked_project_id == self)
        
        if not unlinked_docs:
            # Show detailed analysis even if no unlinked docs found
            analysis_msg = f"""
All documents in folder: {len(all_folder_docs)}
Linked to this project: {len(linked_docs)}
Unlinked documents: {len(unlinked_docs)}

Linked documents:
{chr(10).join([f"  - {doc.name} (linked_project_id: {doc.linked_project_id.name if doc.linked_project_id else 'None'})" for doc in linked_docs])}

Unlinked documents:
{chr(10).join([f"  - {doc.name} (linked_project_id: {doc.linked_project_id.name if doc.linked_project_id else 'None'})" for doc in unlinked_docs])}
            """
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Document Linking Analysis'),
                    'message': analysis_msg,
                    'type': 'info',
                }
            }
        
        # Link the documents to this project
        linked_count = 0
        for doc in unlinked_docs:
            doc.write({
                'linked_project_id': self.id,
                'res_model': 'project.project',
                'res_id': self.id
            })
            linked_count += 1
        
        # Invalidate cache to refresh counts
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Documents Linked'),
                'message': _('Successfully linked %d documents to this project.') % linked_count,
                'type': 'success',
            }
        }
    
    def action_force_link_all_folder_documents(self):
        """Force link ALL documents in the folder to this project"""
        self.ensure_one()
        
        if not self.documents_folder_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project has no documents folder.'),
                    'type': 'warning',
                }
            }
        
        # Get ALL documents in the folder (excluding the folder itself)
        all_folder_docs = self.env['documents.document'].search([
            ('folder_id', '=', self.documents_folder_id.id),
            ('type', '!=', 'folder')
        ])
        
        # Link ALL documents to this project
        linked_count = 0
        for doc in all_folder_docs:
            if doc.linked_project_id != self:
                doc.write({
                    'linked_project_id': self.id,
                    'res_model': 'project.project',
                    'res_id': self.id
                })
                linked_count += 1
        
        # Invalidate cache to refresh counts
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('All Documents Linked'),
                'message': _('Successfully linked ALL %d documents in the folder to this project.') % linked_count,
                'type': 'success',
            }
        }
    
    def action_debug_document_counts(self):
        """Debug method to show detailed document count information"""
        self.ensure_one()
        
        if not self.documents_folder_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project has no documents folder.'),
                    'type': 'warning',
                }
            }
        
        # Get all documents in the folder
        all_folder_docs = self.env['documents.document'].search([
            ('folder_id', '=', self.documents_folder_id.id)
        ])
        
        # Get documents linked to this project
        linked_docs = self.env['documents.document'].search([
            ('linked_project_id', '=', self.id)
        ])
        
        # Get documents in folder that are not folders (what folder_document_ids shows)
        folder_docs_not_folders = all_folder_docs.filtered(lambda d: d.type != 'folder')
        
        # Get documents linked to project that are not folders
        linked_docs_not_folders = linked_docs.filtered(lambda d: d.type != 'folder')
        
        # Build debug message
        debug_info = f"""
Project: {self.name}
Folder: {self.documents_folder_id.name}

📊 Count Analysis:
• All documents in folder: {len(all_folder_docs)}
• Documents in folder (not folders): {len(folder_docs_not_folders)}
• Documents linked to project: {len(linked_docs)}
• Documents linked to project (not folders): {len(linked_docs_not_folders)}

📋 Folder Documents (not folders):
{chr(10).join([f"  - {doc.name} (type: {doc.type}, linked_project_id: {doc.linked_project_id.name if doc.linked_project_id else 'None'})" for doc in folder_docs_not_folders])}

🔗 Linked Documents (not folders):
{chr(10).join([f"  - {doc.name} (type: {doc.type}, folder_id: {doc.folder_id.name if doc.folder_id else 'None'})" for doc in linked_docs_not_folders])}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Count Debug'),
                'message': debug_info,
                'type': 'info',
            }
        }
    
    def action_debug_project_document_ids(self):
        """Debug the project's document_ids field specifically"""
        self.ensure_one()
        
        # Get documents directly linked to this project
        linked_docs = self.env['documents.document'].search([
            ('linked_project_id', '=', self.id)
        ])
        
        # Get the actual document_ids field value
        actual_document_ids = self.document_ids
        
        # Get documents in folder
        folder_docs = []
        if self.documents_folder_id:
            folder_docs = self.env['documents.document'].search([
                ('folder_id', '=', self.documents_folder_id.id),
                ('type', '!=', 'folder')
            ])
        
        debug_info = f"""
Project: {self.name}
Project ID: {self.id}

🔍 Document Analysis:

📋 Direct Search (linked_project_id = {self.id}):
{chr(10).join([f"  - {doc.name} (ID: {doc.id}, type: {doc.type}, folder_id: {doc.folder_id.name if doc.folder_id else 'None'})" for doc in linked_docs])}
Count: {len(linked_docs)}

📋 Project document_ids Field:
{chr(10).join([f"  - {doc.name} (ID: {doc.id}, type: {doc.type}, folder_id: {doc.folder_id.name if doc.folder_id else 'None'})" for doc in actual_document_ids])}
Count: {len(actual_document_ids)}

📋 Documents in Folder:
{chr(10).join([f"  - {doc.name} (ID: {doc.id}, type: {doc.type}, linked_project_id: {doc.linked_project_id.name if doc.linked_project_id else 'None'})" for doc in folder_docs])}
Count: {len(folder_docs)}

🔍 Differences:
• Direct search vs document_ids field: {len(linked_docs)} vs {len(actual_document_ids)}
• Folder docs vs linked docs: {len(folder_docs)} vs {len(linked_docs)}

🔍 Missing from project document_ids:
{chr(10).join([f"  - {doc.name} (ID: {doc.id})" for doc in linked_docs if doc not in actual_document_ids])}

🔍 Missing from linked search:
{chr(10).join([f"  - {doc.name} (ID: {doc.id})" for doc in actual_document_ids if doc not in linked_docs])}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Project Document IDs Debug'),
                'message': debug_info,
                'type': 'info',
            }
        }
    
    def action_force_refresh_document_ids(self):
        """Force refresh the document_ids One2many field specifically"""
        self.ensure_one()
        
        # Get all documents that should be linked
        linked_docs = self.env['documents.document'].search([
            ('linked_project_id', '=', self.id)
        ])
        
        # Check the actual database state
        self.env.cr.execute("""
            SELECT id, name, linked_project_id, res_model, res_id, type 
            FROM documents_document 
            WHERE linked_project_id = %s
            ORDER BY id
        """, (self.id,))
        db_docs = self.env.cr.fetchall()
        
        # Get the One2many field value
        field_docs = self.document_ids
        
        # Fix documents with wrong res_model/res_id
        fixed_count = 0
        for row in db_docs:
            doc_id, name, linked_project_id, res_model, res_id, doc_type = row
            if res_model != 'project.project' or res_id != self.id:
                # Fix the document's res_model and res_id
                self.env.cr.execute("""
                    UPDATE documents_document 
                    SET res_model = 'project.project', res_id = %s
                    WHERE id = %s
                """, (self.id, doc_id))
                fixed_count += 1
        
        # Invalidate all caches
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Force recomputation
        self._compute_document_counts()
        
        # Get the refreshed document_ids
        refreshed_docs = self.document_ids
        
        debug_info = f"""
Database Analysis for Project {self.name} (ID: {self.id}):

📋 Database Records (linked_project_id = {self.id}):
{chr(10).join([f"  - ID: {row[0]}, Name: {row[1]}, linked_project_id: {row[2]}, res_model: {row[3]}, res_id: {row[4]}, type: {row[5]}" for row in db_docs])}
Count: {len(db_docs)}

📋 One2many Field Value (document_ids):
{chr(10).join([f"  - ID: {doc.id}, Name: {doc.name}, linked_project_id: {doc.linked_project_id.id if doc.linked_project_id else 'None'}, res_model: {doc.res_model}, res_id: {doc.res_id}, type: {doc.type}" for doc in field_docs])}
Count: {len(field_docs)}

📋 After Fix and Refresh:
{chr(10).join([f"  - ID: {doc.id}, Name: {doc.name}, linked_project_id: {doc.linked_project_id.id if doc.linked_project_id else 'None'}, res_model: {doc.res_model}, res_id: {doc.res_id}, type: {doc.type}" for doc in refreshed_docs])}
Count: {len(refreshed_docs)}

🔍 Fix Results:
• Documents fixed: {fixed_count}
• Before vs After: {len(field_docs)} vs {len(refreshed_docs)}
• Should be equal now: {len(db_docs)} == {len(refreshed_docs)}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document IDs Fixed'),
                'message': debug_info,
                'type': 'success',
            }
        }
    
    def action_fix_and_refresh_view(self):
        """Fix document linking and refresh the form view"""
        self.ensure_one()
        
        # First fix the documents
        linked_docs = self.env['documents.document'].search([
            ('linked_project_id', '=', self.id)
        ])
        
        # Fix documents with wrong res_model/res_id
        fixed_count = 0
        for doc in linked_docs:
            if doc.res_model != 'project.project' or doc.res_id != self.id:
                doc.write({
                    'res_model': 'project.project',
                    'res_id': self.id
                })
                fixed_count += 1
        
        # Invalidate all caches
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Force recomputation
        self._compute_document_counts()
        
        # Return action to refresh the form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'form': {'action_buttons': True}},
        }
    
    def action_refresh_all_counts(self):
        """Force refresh all computed document counts"""
        self.ensure_one()
        
        # Force recompute all document count fields
        self._compute_document_counts()
        self._compute_project_files_count()
        self._compute_project_folder_files()
        
        # Invalidate cache for all related fields
        self._invalidate_cache([
            'document_ids', 'document_count', 'required_document_count', 
            'deliverable_document_count', 'project_files_count', 'project_folder_files'
        ])
        
        # Force refresh the One2many field by triggering a write
        # This ensures the document_ids field is properly refreshed
        self.write({'id': self.id})
        
        # Also refresh folder counts if folder exists
        if self.documents_folder_id:
            self.documents_folder_id._compute_folder_counts()
            self.documents_folder_id._compute_folder_summary()
            self.documents_folder_id._invalidate_cache([
                'folder_document_ids', 'folder_document_count', 'folder_subfolder_count',
                'folder_category_summary', 'folder_status_summary', 'folder_expired_summary', 'folder_verified_summary'
            ])
        
        # Force a final recomputation after cache invalidation
        self._compute_document_counts()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Counts Refreshed'),
                'message': _('All document counts have been refreshed. Project: %d, Folder: %d') % (
                    self.document_count, 
                    self.documents_folder_id.folder_document_count if self.documents_folder_id else 0
                ),
                'type': 'success',
            }
        }

    def action_refresh_project_files(self):
        """Refresh the project files list and recompute fields"""
        self.ensure_one()
        if self.documents_folder_id:
            # Force recomputation of the project folder files
            self._invalidate_cache(['project_folder_files'])
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Files Refreshed'),
                    'message': _('Project files list has been refreshed.'),
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder.'),
                    'type': 'warning',
                }
            }

    def _invalidate_document_fields(self):
        """Invalidate all document-related computed fields"""
        self._invalidate_cache(['document_count', 'required_document_count', 'deliverable_document_count'])

    def action_view_documents(self):
        """Open documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Project Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
            },
        }

    def action_create_document(self):
        """Create a new document record for this project"""
        self.ensure_one()
        
        if not self.new_document_name:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Missing Information'),
                    'message': _('Please enter a document name.'),
                    'type': 'warning',
                }
            }
        
        # Ensure project has a folder
        self._ensure_project_folder()
        
        # Create the document record
        document_vals = {
            'name': self.new_document_name,
            'category': self.new_document_category,
            'priority': self.new_document_priority,
            'status': self.new_document_status,
            'expiry_date': self.new_document_expiry_date,
            'notes': self.new_document_notes,
            'tag_ids': [(6, 0, self.new_document_tag_ids.ids)] if self.new_document_tag_ids else False,
            'res_model': 'project.project',
            'res_id': self.id,
        }
        
        # Add folder_id if project has a documents folder (for documents.document model)
        if self.documents_folder_id:
            document_vals['folder_id'] = self.documents_folder_id.id
        
        new_document = self.env['documents.document'].create(document_vals)
        
        # Clear the temporary fields
        self.write({
            'new_document_name': False,
            'new_document_category': 'required',
            'new_document_priority': '1',
            'new_document_status': 'draft',
            'new_document_expiry_date': False,
            'new_document_notes': False,
            'new_document_tag_ids': [(5, 0, 0)],
        })
        
        # Refresh the document counts
        self.invalidate_recordset(['document_count', 'required_document_count', 'deliverable_document_count'])
        
        folder_name = self.documents_folder_id.name if self.documents_folder_id else 'Default'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Created'),
                'message': _('Document "%s" has been created in folder "%s". Use the Upload button to add the file.') % (new_document.name, folder_name),
                'type': 'success',
            }
        }

    def action_refresh_documents(self):
        """Force refresh of the document list in the UI"""
        self.ensure_one()
        
        # Force recomputation of all document-related fields
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Force a complete page reload to refresh the view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _force_document_ui_refresh(self):
        """Force UI refresh after document creation"""
        self.ensure_one()
        
        # Force recomputation
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Trigger a client action to refresh the view
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Documents Updated',
                'message': f'Documents have been updated for project {self.name}. Please refresh the page to see the changes.',
                'type': 'info',
                'sticky': False,
            }
        }

    def action_fix_document_tags(self):
        """Fix existing documents that might not have tag_ids field properly initialized"""
        self.ensure_one()
        documents = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.id),
            ('active', '=', True)
        ])
        
        fixed_count = 0
        for doc in documents:
            # Force recomputation of tag_ids field
            doc._invalidate_cache(['tag_ids'])
            fixed_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tags Fixed'),
                'message': _('Fixed tag display for %d documents.') % fixed_count,
                'type': 'success',
            }
        }

    def action_copy_product_documents(self, product):
        """Copy documents from a product to this project"""
        self.ensure_one()
        
        # Get documents from the product
        product_documents = self.env['documents.document'].search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', product.id),
            ('active', '=', True)
        ])
        
        if not product_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents'),
                    'message': _('No documents found in the selected product.'),
                    'type': 'warning',
                }
            }
        
        copied_count = 0
        for doc in product_documents:
            try:
                # Check if document already exists in project
                existing_doc = self.env['documents.document'].search([
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', self.id),
                    ('name', '=', doc.name),
                    ('category', '=', doc.category),
                    ('active', '=', True)
                ], limit=1)
                
                if existing_doc:
                    continue  # Skip if already exists
                
                # Get or create project folder (optional)
                project_folder = self.env['documents.document']._get_project_folder(self)
                
                # Create copy for project
                new_doc_vals = {
                    'name': doc.name,
                    'description': doc.description,
                    'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,  # Copy tags
                    'category': doc.category,
                    'status': 'draft',  # Reset status for new context
                    'expiry_date': doc.expiry_date,
                    'priority': doc.priority,
                    'notes': doc.notes,
                    'res_model': 'project.project',
                    'res_id': self.id,
                }
                
                # Temporarily disabled folder assignment due to disabled folder_id field
                if False:  # project_folder:
                    new_doc_vals['folder_id'] = project_folder.id
                
                self.env['documents.document'].create(new_doc_vals)
                copied_count += 1
                    
            except Exception as e:
                _logger.error(f"Error copying document {doc.name}: {e}")
        
        if copied_count > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Documents Copied'),
                    'message': _('%d documents copied from product.') % copied_count,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents Copied'),
                    'message': _('All documents already exist in the project.'),
                                    'type': 'info',
            }
        }

    def action_copy_from_product(self):
        """Open wizard to copy documents from a selected product to this project"""
        self.ensure_one()
        
        # Find products that have documents AND are used in quotations (sale orders)
        products_with_documents = self.env['product.template'].search([
            ('id', 'in', self.env['documents.document'].search([
                ('res_model', '=', 'product.template'),
                ('active', '=', True)
            ]).mapped('res_id')),
            # Filter to only products that are used in sale order lines (quotations)
            ('id', 'in', self.env['sale.order.line'].search([]).mapped('product_template_id').ids)
        ])
        
        if not products_with_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Quotation Products with Documents'),
                    'message': _('No quotation products found with documents to copy. Only products that are used in sale orders and have documents will be shown.'),
                    'type': 'warning',
                }
            }
        
        # If only one product, use it directly
        if len(products_with_documents) == 1:
            return {
                'name': _('Copy Documents from Product'),
                'type': 'ir.actions.act_window',
                'res_model': 'copy.documents.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_source_model': 'product.template',
                    'default_source_id': products_with_documents.id,
                    'default_source_product_id': products_with_documents.id,
                    'default_target_model': 'project.project',
                    'default_target_id': self.id,
                    'default_target_project_id': self.id,
                }
            }
        
        # If multiple products, show selection dialog
        return {
            'name': _('Select Quotation Product to Copy Documents From'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list',
            'view_id': self.env.ref('unified_documents.view_product_template_list_copy_selection').id,
            'target': 'new',
            'domain': [('id', 'in', products_with_documents.ids)],
            'context': {
                'default_target_project_id': self.id,
                'quotation_product_ids': products_with_documents.ids,
                'search_default_quotation_products': 1,  # Apply quotation products filter by default
            }
        }

    def _ensure_project_folder(self):
        """Ensure the project has a documents folder"""
        
        if not self.documents_folder_id:
            try:
                # Look for existing folder
                existing_folder = self.env['documents.document'].search([
                    ('name', '=', self.name),
                    ('type', '=', 'folder')
                ], limit=1)
                
                if existing_folder:
                    self.documents_folder_id = existing_folder.id
                else:
                    # Create new folder
                    new_folder = self.env['documents.document'].create({
                        'name': self.name,
                        'type': 'folder',
                        'company_id': self.company_id.id if self.company_id else False,
                    })
                    self.documents_folder_id = new_folder.id
            except Exception as e:
                _logger.error(f"Failed to create documents folder for project {self.name}: {e}")

    def action_create_project_folder(self):
        """Create or assign documents folder for this project"""
        self.ensure_one()
        self._ensure_project_folder()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Folder Created'),
                'message': _('Documents folder "%s" has been created/assigned to this project.') % (self.documents_folder_id.name if self.documents_folder_id else self.name),
                'type': 'success',
            }
        }

    def action_view_project_folder(self):
        """Open the project's documents folder"""
        self.ensure_one()
        if self.documents_folder_id:
            return {
                'name': _('Project Documents Folder'),
                'type': 'ir.actions.act_window',
                'res_model': 'documents.document',
                'res_id': self.documents_folder_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder yet. Create one first.'),
                    'type': 'warning',
                }
            }

    def action_view_project_files(self):
        """View all files in the project's documents folder"""
        self.ensure_one()
        # View files in the project's documents folder
        if self.documents_folder_id:
            # Find documents in the project folder, then get their attachments
            folder_documents = self.env['documents.document'].search([
                ('folder_id', '=', self.documents_folder_id.id)
            ])
            return {
                'name': _('Project Files - %s') % self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'ir.attachment',
                'view_mode': 'list',
                'view_id': self.env.ref('unified_documents.view_ir_attachment_tree_project_files').id,
                'domain': [
                    ('res_model', '=', 'documents.document'),
                    ('res_id', 'in', folder_documents.ids)
                ],
                'context': {
                    'default_res_model': 'documents.document',
                },
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder yet. Create one first.'),
                    'type': 'warning',
                }
            }

    def action_view_required_documents(self):
        """Open required documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Required Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id),
                ('category', '=', 'required')
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_category': 'required',
            },
        }

    def action_view_deliverable_documents(self):
        """Open deliverable documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Deliverable Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id),
                ('category', '=', 'deliverable')
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_category': 'deliverable',
            },
        }

    def action_upload_project_document(self):
        """Upload a new document for this project"""
        self.ensure_one()
        # Ensure project has a documents folder first
        if not self.documents_folder_id:
            self.action_create_documents_folder()
        
        return {
            'name': _('Upload Document for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('unified_documents.view_documents_document_upload_form').id,
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_linked_project_id': self.id,
                'default_name': f'New Document - {self.name}',
                'default_category': 'required',
                'default_folder_id': self.documents_folder_id.id if self.documents_folder_id else False,
                'default_type': 'file',  # Ensure it's a file type
                'default_owner_id': self.env.user.id,
                'form_view_initial_mode': 'edit',
                'preserve_linking': True,  # Prevent unlinking during upload
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # Apply template if selected
            if record.document_template_id:
                record._apply_selected_document_template()
        return records

    def write(self, vals):
        result = super().write(vals)
        
        # Check if document_template_id is being set
        if vals.get('document_template_id'):
            for record in self:
                if record.document_template_id:
                    record._apply_selected_document_template()
        
        return result

    def _apply_selected_document_template(self):
        """Apply the selected document template to this project"""
        self.ensure_one()
        
        if not self.document_template_id:
            return
        
        try:
            # Apply the template
            self._apply_document_template_to_project(self.document_template_id)
            _logger.info(f"Document template {self.document_template_id.name} applied to project {self.name}")
        except Exception as e:
            _logger.error(f"Failed to apply document template {self.document_template_id.name} to project {self.name}: {e}")
            # Don't raise the error to avoid breaking the save operation

    def _apply_document_template_to_project(self, template):
        """Apply a document template to this project"""
        self.ensure_one()
        
        if not template or not template.exists():
            raise ValidationError(_('Invalid document template provided.'))
        
        # Create documents from template lines
        created_docs = []
        for line in template.document_template_line_ids:
            try:
                document_vals = {
                    'name': line.name,
                    'category': line.category,
                    'priority': line.priority,
                    'notes': line.notes,
                    'res_model': 'project.project',
                    'res_id': self.id,
                    'linked_project_id': self.id,
                    'status': 'draft',
                    'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                }
                
                # Add folder_id if project has a documents folder (for documents.document model)
                if self.documents_folder_id:
                    document_vals['folder_id'] = self.documents_folder_id.id
                
                new_doc = self.env['documents.document'].create(document_vals)
                created_docs.append(new_doc)
            except Exception as e:
                _logger.warning(f"Failed to create document '{line.name}' for project {self.name}: {e}")
                continue
        
        return created_docs

    def action_apply_document_template(self):
        """Apply the selected document template to this project"""
        self.ensure_one()
        
        if not self.document_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Template Selected'),
                    'message': _('Please select a document template first.'),
                    'type': 'warning',
                }
            }
        
        # Apply the template
        created_docs = self._apply_document_template_to_project(self.document_template_id)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Applied'),
                'message': _('Document template "%s" has been applied successfully. %d documents have been added to this project.') % (self.document_template_id.name, len(created_docs)),
                'type': 'success',
            }
        }

    def action_view_selected_document_template(self):
        """Open the selected document template"""
        self.ensure_one()
        
        if not self.document_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Template Selected'),
                    'message': _('No document template is selected for this project.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.document.template',
            'res_id': self.document_template_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_project_task_template(self):
        """Open the selected task template (for project templates)"""
        self.ensure_one()
        
        if not self.task_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Template Selected'),
                    'message': _('No task template is selected for this project template.'),
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

    def action_create_project_task_template(self):
        """Create a new task template for this project template"""
        self.ensure_one()
        
        return {
            'name': _('Create Task Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Task Template",
                'default_description': f"Task template for {self.name} project template",
            },
        }



    def action_view_project_milestone_templates(self):
        """Open the selected milestone templates (for project templates)"""
        self.ensure_one()
        
        if not self.milestone_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Milestone Templates Selected'),
                    'message': _('No milestone templates are selected for this project template.'),
                    'type': 'info',
                }
            }
        
        return {
            'name': _('Milestone Templates - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.milestone.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.milestone_template_ids.ids)],
            'context': {
                'default_name': f"Milestone Templates for {self.name}",
            },
        }



    def action_create_project_milestone_template(self):
        """Create a new milestone template for this project template"""
        self.ensure_one()
        
        return {
            'name': _('Create Milestone Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.milestone.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Milestone Template",
                'default_description': f"Milestone template for {self.name} project template",
            },
        }

    def action_test_document_linking(self):
        """Test action to verify document linking - can be called from project form"""
        self.ensure_one()
        
        _logger.info(f"🧪 Testing document linking for project {self.name} (ID: {self.id})")
        
        # Check documents linked to this project
        docs_linked = self.env['documents.document'].search([('linked_project_id', '=', self.id)])
        _logger.info(f"📋 Documents with linked_project_id={self.id}: {[(d.id, d.name, d.category) for d in docs_linked]}")
        
        # Check documents with res_model and res_id
        docs_res = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.id)
        ])
        _logger.info(f"📋 Documents with res_model='project.project' and res_id={self.id}: {[(d.id, d.name, d.category) for d in docs_res]}")
        
        # Check project's document_ids field
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        _logger.info(f"📋 Project document_ids count: {len(self.document_ids)}")
        _logger.info(f"📋 Project document_ids: {[(d.id, d.name, d.category) for d in self.document_ids]}")
        
        # Check project's computed counts
        _logger.info(f"📊 Project document_count: {self.document_count}")
        _logger.info(f"📊 Project required_document_count: {self.required_document_count}")
        _logger.info(f"📊 Project deliverable_document_count: {self.deliverable_document_count}")
        
        # Create a test document if none exist
        if not docs_linked and not docs_res:
            _logger.info(f"🧪 No documents found, creating test document")
            test_doc = self.env['documents.document'].create({
                'name': f"TEST DOC - {self.name}",
                'res_model': 'project.project',
                'res_id': self.id,
                'linked_project_id': self.id,
                'category': 'required',
                'status': 'draft',
                'priority': '1',
                'description': 'Test document for debugging',
                'notes': f"Test document from project: {self.name}",
            })
            _logger.info(f"🧪 Created test document: {test_doc.name} (ID: {test_doc.id})")
            
            # Force recomputation
            self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
            
            message = f"Test Document Created!\n\nProject: {self.name} (ID: {self.id})\n"
            message += f"Test Document: {test_doc.name} (ID: {test_doc.id})\n"
            message += f"Document linked_project_id: {test_doc.linked_project_id.id if test_doc.linked_project_id else 'None'}\n"
            message += f"Document res_model: {test_doc.res_model}, res_id: {test_doc.res_id}\n"
            message += f"Project document_ids count after creation: {len(self.document_ids)}\n"
            message += f"Project document_count after creation: {self.document_count}"
        else:
            message = f"Document Linking Test Results for {self.name}:\n\n"
            message += f"Project ID: {self.id}\n"
            message += f"Documents with linked_project_id: {len(docs_linked)}\n"
            message += f"Documents with res_model/res_id: {len(docs_res)}\n"
            message += f"Project document_ids count: {len(self.document_ids)}\n"
            message += f"Project document_count: {self.document_count}\n"
            message += f"Project required_document_count: {self.required_document_count}\n"
            message += f"Project deliverable_document_count: {self.deliverable_document_count}\n\n"
            
            if docs_linked:
                message += "Documents with linked_project_id:\n"
                for doc in docs_linked:
                    message += f"  - {doc.name} (ID: {doc.id}, Category: {doc.category})\n"
            
            if docs_res:
                message += "Documents with res_model/res_id:\n"
                for doc in docs_res:
                    message += f"  - {doc.name} (ID: {doc.id}, Category: {doc.category})\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Document Linking Test',
                'message': message,
                'type': 'info',
            }
        }
