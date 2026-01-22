# -*- coding: utf-8 -*-
{
    'name': 'Product Category Search',
    'version': '18.0.1.1.0',
    'category': 'Sales',
    'summary': 'Advanced product categorization and search for UAE business services',
    'description': """
        Product Category Search Module
        ===============================
        
        Advanced product categorization and search system for organizing 250+ UAE 
        business service products from Freezoner database.
        
        Key Features:
        * Smart Product Categorization by service type
        * Department-based organization (Accounts, Operations, Sales)
        * Advanced multi-criteria search wizard
        * Saved search presets for quick access
        * Document-based filtering and classification
        * Compliance level tracking
        * CSV import and bulk categorization
        * Enhanced kanban, tree, and form views
        * Integration with unified_documents and project_templates_basic
        
        Product Categories:
        * Visa Services (60+ products)
        * Accounting Services (46 products)
        * Value Added Services (85+ products)
        * Business Setup, Renewal, Liquidation
        * Banking & Account Opening
        * Business Administration
        * Service Fees and Miscellaneous
        
        Perfect for UAE business service providers managing large product catalogs
        with complex document requirements and compliance needs.
    """,
    'author': 'Sabry Youssef',
    'website': 'https://github.com/sabryyoussef/mazagawy',
    'license': 'LGPL-3',
    
    'depends': [
        'base',
        'product',
        'sale_management',
    ],
    
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/product_search_security.xml',
        
        # Master Data (load first)
        'data/product_service_types.xml',
        'data/product_departments.xml',
        'data/search_preset_templates.xml',
        
        # Views - Models
        'views/product_service_type_views.xml',
        'views/product_department_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/product_search_preset_views.xml',
        
        # Views - Wizards
        'wizard/product_search_wizard_views.xml',
        'wizard/product_import_wizard_views.xml',
        'wizard/product_bulk_categorize_views.xml',
        
        # Menu
        'views/menu_views.xml',
    ],
    
    'demo': [
        'demo/demo_freezoner_products.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'product_category_search/static/src/css/product_category_search.css',
            'product_category_search/static/src/js/product_search_widget.js',
        ],
    },
    
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_search.png',
        'static/description/screenshot_kanban.png',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
