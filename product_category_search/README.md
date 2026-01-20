# Product Category Search Module

## Overview

**Product Category Search** is an advanced Odoo 18 module designed to organize, categorize, and search through 250+ UAE business service products from the Freezoner database. This module provides intelligent product classification, multi-criteria search, and department-based organization.

## Key Features

### 🔍 **Smart Product Categorization**
- **Service Type Taxonomy**: Visa, Accounting, Banking, Business Setup, etc.
- **Department Organization**: Accounts, Operations, Sales
- **Compliance Levels**: High, Medium, Low, None
- **Document-Based Classification**: Search by required/deliverable documents

### 🎯 **Advanced Search & Filtering**
- **Multi-Criteria Search**: Filter by service type, department, price, documents
- **Saved Search Presets**: Save commonly used filters for quick access
- **Quick Filters**: One-click filters for visa services, accounting, banking, etc.
- **Price Range Filtering**: Find products within specific price ranges

### 📊 **Enhanced Views**
- **Kanban View**: Color-coded cards grouped by service type or category
- **Tree View**: Advanced list with sorting and filtering
- **Search View**: Powerful search with multiple filter options
- **Department Views**: Separate views for Accounts, Operations, Sales teams

### 📥 **Data Import & Migration**
- **CSV Import**: Upload and categorize products from CSV files
- **Bulk Categorization**: Auto-categorize products based on naming patterns
- **Freezoner Migration**: Import from Freezoner Odoo 19 database
- **Validation & Preview**: Preview imports before committing

## Module Structure

```
product_category_search/
├── __manifest__.py              # Module configuration
├── README.md                    # This file
├── MODULE_DEVELOPMENT_PLAN.md   # Detailed implementation plan
├── models/                      # Data models
│   ├── product_category_enhanced.py
│   ├── product_template_enhanced.py
│   ├── product_service_type.py
│   ├── product_department.py
│   └── product_search_preset.py
├── wizard/                      # Wizards
│   ├── product_search_wizard.py
│   ├── product_bulk_categorize.py
│   └── product_import_wizard.py
├── views/                       # Views & UI
│   ├── product_category_views.xml
│   ├── product_template_views.xml
│   ├── product_search_views.xml
│   ├── product_kanban_views.xml
│   └── menu_views.xml
├── data/                        # Master data
│   ├── product_service_types.xml
│   ├── product_departments.xml
│   └── search_preset_templates.xml
├── security/                    # Security rules
│   ├── ir.model.access.csv
│   └── product_search_security.xml
└── demo/                        # Demo data
    └── demo_freezoner_products.xml
```

## Product Categories

Based on Freezoner database analysis (250+ products):

| Category | Products | Departments |
|----------|----------|-------------|
| Accounting Services | 46 | Accounts, Operations, Sales |
| Banking & Account Opening | 12 | Accounts, Operations, Sales |
| Business Administration | 24 | Accounts, Operations, Sales |
| Business Setup | 5 | Operations, Sales |
| Company Liquidation | 6 | Accounts, Operations, Sales |
| Company Renewal | 6 | Accounts, Operations, Sales |
| Value Added Services | 85+ | Accounts, Operations, Sales |
| Visa Services | 60+ | Accounts, Operations, Sales |
| Service Fees | 5 | All |
| Miscellaneous | 40+ | Various |

## Installation

### Prerequisites

```python
'depends': [
    'base',
    'product',
    'sale_management',
    'unified_documents',        # For document integration
    'project_templates_basic',  # For template linking
]
```

### Install Steps

1. Copy the module to your Odoo addons directory
2. Update the app list: `Settings > Apps > Update Apps List`
3. Search for "Product Category Search"
4. Click "Install"

## Usage

### 1. Access Product Categories

Navigate to: **Sales > Configuration > Product Categories**

Features:
- View all product categories with service type classification
- See product count and average price per category
- Manage department assignments
- Set compliance levels

### 2. Advanced Product Search

Navigate to: **Sales > Products > Advanced Search**

Search by:
- Product name or reference code
- Service type (Visa, Accounting, Banking, etc.)
- Target department (Accounts, Operations, Sales)
- Price range
- Document requirements
- Compliance level
- Service tracking type

Save frequently used searches as presets for quick access.

### 3. Department Views

Quick access to department-specific products:
- **Sales > Products > Accounts Products**
- **Sales > Products > Operations Products**
- **Sales > Products > Sales Products**

### 4. Import Products

Navigate to: **Sales > Configuration > Import Products**

Options:
- **CSV Upload**: Import from CSV file (template provided)
- **Database Import**: Connect directly to Freezoner Odoo 19 database
- **Auto-Categorization**: Automatically classify products based on patterns
- **Preview & Validate**: Review before importing

### 5. Saved Search Filters

Navigate to: **Sales > Configuration > Search Presets**

Pre-configured filters:
- **High Compliance Services**: All services requiring high compliance
- **All Visa Services**: Filter visa-related products
- **Premium Services**: Products over AED 5,000
- **Accounting Services**: All accounting-related products
- **Banking Services**: All banking-related products

Create custom filters and share with your team.

## Configuration

### Service Types

Define your service taxonomy at: **Sales > Configuration > Service Types**

Example hierarchy:
```
Visa Services
├── Employment Visa
├── Investor Visa
├── Golden Visa
├── Dependent Visa
└── Property Visa

Accounting Services
├── Tax Services
│   ├── Corporate Tax
│   └── VAT Services
├── Bookkeeping
└── Audit Services
```

### Departments

Configure departments at: **Sales > Configuration > Departments**

Default departments:
- **Accounts Department**: Financial and tax services
- **Operations Department**: Service delivery and execution
- **Sales Department**: Client-facing sales

### Compliance Levels

Set compliance requirements:
- **High**: Business formation, banking, corporate tax, golden visa
- **Medium**: VAT services, accounting, property visa
- **Low**: Simple certificates, service fees
- **None**: Operational costs, miscellaneous

## API & Integration

### Search Products Programmatically

```python
# Search for all visa services under 3000 AED
products = self.env['product.template'].search([
    ('is_visa_service', '=', True),
    ('list_price', '<', 3000)
])

# Search by service type
service_type = self.env['product.service.type'].search([('code', '=', 'VISA-EMP')], limit=1)
products = self.env['product.template'].search([('service_type_id', '=', service_type.id)])

# Search by department
products = self.env['product.template'].search([('target_department', '=', 'accounts')])
```

### Use Search Wizard

```python
# Create and execute search
wizard = self.env['product.search.wizard'].create({
    'service_type_id': visa_service_type.id,
    'price_min': 1000,
    'price_max': 5000,
    'requires_compliance': True,
})
return wizard.action_search()
```

## Reporting & Analytics

### Product Statistics

View product analytics:
- Products by service type
- Products by department
- Products by compliance level
- Average prices by category
- Most sold products
- Products requiring specific documents

### Export Options

Export search results to:
- **CSV**: For external analysis
- **Excel**: With formatting
- **PDF**: For printing

## Support & Development

### Documentation

- **Development Plan**: [MODULE_DEVELOPMENT_PLAN.md](MODULE_DEVELOPMENT_PLAN.md)
- **Freezoner Analysis**: [FREEZONER_PRODUCTS_ANALYSIS.md](../document_categorization_and_importing_plan/FREEZONER_PRODUCTS_ANALYSIS.md)
- **Migration Plan**: [PRODUCT_IMPORT_MIGRATION_PLAN.md](../document_categorization_and_importing_plan/PRODUCT_IMPORT_MIGRATION_PLAN.md)

### Roadmap

**Phase 1**: Core Module (✅ Current)
- Enhanced product categorization
- Basic search functionality
- Department organization

**Phase 2**: Advanced Search (🔄 In Progress)
- Multi-criteria search wizard
- Saved search presets
- Advanced filtering

**Phase 3**: Import & Migration (📋 Planned)
- CSV import
- Freezoner database migration
- Bulk categorization

**Phase 4**: Analytics & Reporting (📋 Planned)
- Product analytics dashboard
- Sales insights
- Compliance reporting

### Contributing

For feature requests or bug reports, please contact the development team.

## License

LGPL-3

## Author

**Sabry Youssef**  
GitHub: [sabryyoussef/mazagawy](https://github.com/sabryyoussef/mazagawy)

## Version History

- **18.0.1.0.0** (January 20, 2026)
  - Initial release
  - Enhanced product categorization
  - Service type taxonomy
  - Department organization
  - Basic search functionality

---

**Status**: Under Development  
**Next Milestone**: Phase 1 - Core Module Completion
