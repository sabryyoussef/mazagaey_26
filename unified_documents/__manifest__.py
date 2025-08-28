# -*- coding: utf-8 -*-
{
    "name": "Unified Documents Extension",
    "summary": "Extends Odoo Documents module with additional functionality for products and projects",
    "version": "18.0.1.0.5",
    "category": "Documents",
    "author": "Sabry",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
        "project",
        "documents",  # Odoo Enterprise Documents module
        "sale",  # For sale order automation support
        "sale_project",  # For project template support
        "purchase",  # For purchase order automation support
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/configuration.xml",
        "data/documents_tag_data.xml",
        "data/user_groups.xml",
        "data/demo_documents_simple.xml",
        "data/demo_automation_simple.xml",
        "data/demo_product_templates.xml",
        "data/demo_service_products.xml",
        "demo/demo_data.xml",
        # Core views
        "views/core/documents_document_views.xml",
        "views/core/document_copy_automation_views.xml",
        "views/core/document_management_views.xml",
        # Extension views
        "views/extensions/ir_attachment_views.xml",
        "views/extensions/task_views.xml",
        "views/extensions/task_views_new.xml",
        # Integration views
        "views/integrations/product_views.xml",
        "views/integrations/product_template_views.xml",
        "views/integrations/project_views.xml",
        "views/integrations/document_upload_views.xml",
        "views/integrations/sale_order_views.xml",
        "views/integrations/sale_order_line_views.xml",
        "wizard/copy_documents_wizard_views.xml",
        "wizard/documents_upload_wizard_views.xml",
        "wizard/create_product_from_template_wizard_views.xml",
        "views/menu_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
