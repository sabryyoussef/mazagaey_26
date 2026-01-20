# Product Category Search Module - Development Plan
**Module Name:** `product_category_search`  
**Version:** 18.0.1.0.0  
**Purpose:** Advanced product categorization and search for 250+ Freezoner UAE service products  
**Date Created:** January 20, 2026

---

## 🎯 **Module Objectives**

1. **Smart Product Categorization**: Organize 250+ products by service type, department, document requirements
2. **Advanced Search & Filters**: Multi-criteria search with saved filters and custom views
3. **Department-Based Organization**: Separate views for Accounts, Operations, Sales departments
4. **Document-Based Search**: Find products by required/deliverable documents
5. **Price Range Filtering**: Filter by price tiers and service packages
6. **Service Type Grouping**: Group products by visa, accounting, business setup, banking, etc.
7. **Migration Support**: Import and categorize products from Freezoner Odoo 19 database

---

## 📊 **Product Categories Overview**

Based on Freezoner database analysis (250+ products):

| Category | Count | Departments | Service Tracking |
|----------|-------|-------------|------------------|
| **Accounting Services** | 46 | Accounts, Operations, Sales | new_workflow |
| **Banking & Accounts Opening** | 12 | Accounts, Operations, Sales | new_workflow |
| **Business Administration** | 24 | Accounts, Operations, Sales | new_workflow |
| **Business Setup** | 5 | Operations, Sales | new_workflow |
| **Company Liquidation** | 6 | Accounts, Operations, Sales | new_workflow |
| **Company Renewal** | 6 | Accounts, Operations, Sales | new_workflow |
| **Value Added Services** | 85+ | Accounts, Operations, Sales | new_workflow |
| **Visa Services** | 60+ | Accounts, Operations, Sales | new_workflow |
| **Service Fees** | 5 | All | task_global_project |
| **Miscellaneous** | 40+ | Various | various |

**Total Products:** 250+

---

## 🏗️ **Module Architecture**

### **Phase 1: Foundation & Core Models** ✅ **START HERE**

#### **1.1 Module Structure**
```
product_category_search/
├── __init__.py
├── __manifest__.py
├── README.md
├── MODULE_DEVELOPMENT_PLAN.md (this file)
├── models/
│   ├── __init__.py
│   ├── product_category_enhanced.py      # Enhanced product.category
│   ├── product_template_enhanced.py      # Enhanced product.template
│   ├── product_service_type.py           # Service type taxonomy
│   ├── product_department.py             # Department taxonomy
│   └── product_search_preset.py          # Saved search filters
├── wizard/
│   ├── __init__.py
│   ├── product_search_wizard.py          # Advanced search wizard
│   ├── product_bulk_categorize.py        # Bulk categorization
│   └── product_import_wizard.py          # Import from CSV/Freezoner
├── views/
│   ├── product_category_views.xml        # Enhanced category views
│   ├── product_template_views.xml        # Enhanced product views
│   ├── product_search_views.xml          # Search wizard views
│   ├── product_kanban_views.xml          # Kanban by category
│   └── menu_views.xml                    # Menu structure
├── data/
│   ├── product_service_types.xml         # Service type master data
│   ├── product_departments.xml           # Department master data
│   ├── product_category_taxonomy.xml     # Category structure
│   └── search_preset_templates.xml       # Pre-defined search filters
├── security/
│   ├── ir.model.access.csv
│   └── product_search_security.xml
├── demo/
│   └── demo_freezoner_products.xml       # Sample Freezoner products
└── static/
    └── description/
        ├── icon.png
        └── index.html
```

#### **1.2 Dependencies**
```python
'depends': [
    'base',
    'product',
    'sale_management',
    'unified_documents',  # For document integration
    'project_templates_basic',  # For template linking
]
```

---

## 🔧 **Feature Specifications**

### **Feature 1: Enhanced Product Categories**

**Model:** `product.category` (extended)

**New Fields:**
```python
# Service Type Classification
service_type = fields.Selection([
    ('visa', 'Visa Services'),
    ('accounting', 'Accounting Services'),
    ('banking', 'Banking Services'),
    ('business_setup', 'Business Setup'),
    ('business_admin', 'Business Administration'),
    ('company_renewal', 'Company Renewal'),
    ('company_liquidation', 'Company Liquidation'),
    ('value_added', 'Value Added Services'),
    ('service_fees', 'Service Fees'),
    ('miscellaneous', 'Miscellaneous'),
])

# Department Assignment
department_ids = fields.Many2many('product.department', string='Departments')

# Compliance Level
compliance_level = fields.Selection([
    ('high', 'High Compliance'),
    ('medium', 'Medium Compliance'),
    ('low', 'Low Compliance'),
    ('none', 'No Compliance Required'),
])

# Category Icon & Color
category_icon = fields.Char(string='Icon Class')
category_color = fields.Integer(string='Color Index')

# Statistics
product_count = fields.Integer(compute='_compute_product_count')
avg_price = fields.Float(compute='_compute_avg_price')
```

---

### **Feature 2: Enhanced Product Template**

**Model:** `product.template` (extended)

**New Fields:**
```python
# Service Classification
service_type_id = fields.Many2one('product.service.type', string='Service Type')
target_department = fields.Selection([
    ('accounts', 'Accounts Department'),
    ('operations', 'Operations Department'),
    ('sales', 'Sales Department'),
    ('all', 'All Departments'),
])

# Document Requirements
document_required_count = fields.Integer(compute='_compute_document_counts')
document_deliverable_count = fields.Integer(compute='_compute_document_counts')
has_compliance_docs = fields.Boolean(compute='_compute_has_compliance')

# Pricing Tiers
has_multiyear_pricing = fields.Boolean(string='Multi-Year Options Available')
price_tier_ids = fields.One2many('product.price.tier', 'product_id')

# Search Tags
search_tags = fields.Char(string='Search Keywords', help='Comma-separated keywords')
freezoner_reference = fields.Char(string='Freezoner Reference Code')

# Quick Filters
is_visa_service = fields.Boolean(compute='_compute_service_flags', store=True)
is_accounting_service = fields.Boolean(compute='_compute_service_flags', store=True)
is_banking_service = fields.Boolean(compute='_compute_service_flags', store=True)
is_setup_service = fields.Boolean(compute='_compute_service_flags', store=True)
requires_high_compliance = fields.Boolean(compute='_compute_compliance_flag', store=True)

# Statistics
usage_count = fields.Integer(string='Times Sold')
avg_project_duration = fields.Float(string='Avg Project Duration (days)')
```

---

### **Feature 3: Service Type Taxonomy**

**Model:** `product.service.type` (new)

**Purpose:** Master data for service type classification

**Fields:**
```python
name = fields.Char(string='Service Type Name', required=True)
code = fields.Char(string='Code', required=True)
description = fields.Text(string='Description')
icon = fields.Char(string='Icon Class')
color = fields.Integer(string='Color Index')
parent_id = fields.Many2one('product.service.type', string='Parent Type')
child_ids = fields.One2many('product.service.type', 'parent_id', string='Sub-Types')
product_count = fields.Integer(compute='_compute_product_count')
sequence = fields.Integer(string='Sequence', default=10)
active = fields.Boolean(default=True)
```

**Sample Data:**
```xml
<record id="service_type_visa" model="product.service.type">
    <field name="name">Visa Services</field>
    <field name="code">VISA</field>
    <field name="icon">fa-id-card</field>
    <field name="color">4</field>
    <field name="sequence">10</field>
</record>

<record id="service_type_visa_employment" model="product.service.type">
    <field name="name">Employment Visa</field>
    <field name="code">VISA-EMP</field>
    <field name="parent_id" ref="service_type_visa"/>
    <field name="sequence">11</field>
</record>

<!-- More service types: Investor Visa, Golden Visa, Dependent Visa, etc. -->
```

---

### **Feature 4: Department Taxonomy**

**Model:** `product.department` (new)

**Purpose:** Organize products by target department

**Fields:**
```python
name = fields.Char(string='Department Name', required=True)
code = fields.Char(string='Code', required=True)
description = fields.Text(string='Description')
manager_id = fields.Many2one('res.users', string='Department Manager')
product_ids = fields.Many2many('product.template', string='Products')
product_count = fields.Integer(compute='_compute_product_count')
active = fields.Boolean(default=True)
```

**Sample Data:**
```xml
<record id="dept_accounts" model="product.department">
    <field name="name">Accounts Department</field>
    <field name="code">ACCT</field>
    <field name="description">Accounting, tax, and financial services</field>
</record>

<record id="dept_operations" model="product.department">
    <field name="name">Operations Department</field>
    <field name="code">OPS</field>
    <field name="description">Service delivery and execution</field>
</record>

<record id="dept_sales" model="product.department">
    <field name="name">Sales Department</field>
    <field name="code">SALES</field>
    <field name="description">Client-facing sales services</field>
</record>
```

---

### **Feature 5: Advanced Product Search Wizard**

**Model:** `product.search.wizard` (transient)

**Purpose:** Multi-criteria product search with filters

**Fields:**
```python
# Basic Filters
name = fields.Char(string='Product Name Contains')
categ_id = fields.Many2one('product.category', string='Category')
service_type_id = fields.Many2one('product.service.type', string='Service Type')
target_department = fields.Selection([...], string='Department')

# Price Filters
price_min = fields.Float(string='Min Price')
price_max = fields.Float(string='Max Price')
has_multiyear = fields.Boolean(string='Has Multi-Year Options')

# Document Filters
requires_passport = fields.Boolean(string='Requires Passport')
requires_emirates_id = fields.Boolean(string='Requires Emirates ID')
requires_business_plan = fields.Boolean(string='Requires Business Plan')
min_required_docs = fields.Integer(string='Min Required Documents')
min_deliverable_docs = fields.Integer(string='Min Deliverable Documents')

# Compliance Filters
compliance_level = fields.Selection([...], string='Compliance Level')
requires_compliance = fields.Boolean(string='Requires Compliance Check')

# Service Tracking
service_tracking = fields.Selection([...], string='Service Tracking Type')
has_project_template = fields.Boolean(string='Has Project Template')

# Quick Filters
is_visa_service = fields.Boolean(string='Visa Services Only')
is_accounting_service = fields.Boolean(string='Accounting Services Only')
is_banking_service = fields.Boolean(string='Banking Services Only')
is_setup_service = fields.Boolean(string='Setup Services Only')

# Sorting
sort_by = fields.Selection([
    ('name', 'Name'),
    ('price', 'Price'),
    ('usage', 'Most Used'),
    ('recent', 'Recently Added'),
], default='name')

# Results
product_ids = fields.Many2many('product.template', compute='_compute_search_results')
result_count = fields.Integer(compute='_compute_result_count')

# Save Filter
save_filter = fields.Boolean(string='Save This Filter')
filter_name = fields.Char(string='Filter Name')
```

**Methods:**
```python
def action_search(self):
    """Execute search and display results"""
    domain = self._build_search_domain()
    products = self.env['product.template'].search(domain)
    
    # Open results in tree/kanban view
    return {
        'type': 'ir.actions.act_window',
        'name': 'Search Results',
        'res_model': 'product.template',
        'view_mode': 'kanban,tree,form',
        'domain': [('id', 'in', products.ids)],
        'context': {'search_default_group_by_category': 1}
    }

def action_save_filter(self):
    """Save current filter as preset"""
    # Create product.search.preset record
    pass
```

---

### **Feature 6: Saved Search Presets**

**Model:** `product.search.preset` (new)

**Purpose:** Save commonly used search filters

**Fields:**
```python
name = fields.Char(string='Filter Name', required=True)
description = fields.Text(string='Description')
user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
is_public = fields.Boolean(string='Public Filter', default=False)
search_domain = fields.Text(string='Search Domain (JSON)')
sort_order = fields.Char(string='Sort Order')
usage_count = fields.Integer(string='Times Used', default=0)
last_used = fields.Datetime(string='Last Used')
active = fields.Boolean(default=True)
```

**Pre-defined Filters:**
```xml
<!-- High Compliance Services -->
<record id="preset_high_compliance" model="product.search.preset">
    <field name="name">High Compliance Services</field>
    <field name="description">All services requiring high compliance checks</field>
    <field name="is_public">True</field>
    <field name="search_domain">[('requires_high_compliance', '=', True)]</field>
</record>

<!-- Visa Services -->
<record id="preset_all_visas" model="product.search.preset">
    <field name="name">All Visa Services</field>
    <field name="is_public">True</field>
    <field name="search_domain">[('is_visa_service', '=', True)]</field>
</record>

<!-- Premium Services (>5000 AED) -->
<record id="preset_premium_services" model="product.search.preset">
    <field name="name">Premium Services (>5000 AED)</field>
    <field name="is_public">True</field>
    <field name="search_domain">[('list_price', '>', 5000)]</field>
</record>
```

---

## 🎨 **UI/UX Features**

### **View 1: Enhanced Product Kanban View**

**Features:**
- Group by service type, category, or department
- Color-coded cards by compliance level
- Quick stats: document count, price, usage
- Quick actions: view details, duplicate, create SO

```xml
<record id="view_product_template_kanban_category" model="ir.ui.view">
    <field name="name">product.template.kanban.category</field>
    <field name="model">product.template</field>
    <field name="arch" type="xml">
        <kanban default_group_by="service_type_id" class="o_kanban_mobile">
            <field name="id"/>
            <field name="name"/>
            <field name="list_price"/>
            <field name="service_type_id"/>
            <field name="target_department"/>
            <field name="document_required_count"/>
            <field name="document_deliverable_count"/>
            <field name="compliance_level"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_global_click">
                        <!-- Product Card -->
                        <div class="o_kanban_record_top">
                            <strong class="o_kanban_record_title">
                                <field name="name"/>
                            </strong>
                            <span class="badge badge-pill" 
                                  t-attf-class="badge-{{record.compliance_level.raw_value}}">
                                <field name="compliance_level"/>
                            </span>
                        </div>
                        <div class="o_kanban_record_body">
                            <div>Department: <field name="target_department"/></div>
                            <div>Price: <field name="list_price" widget="monetary"/></div>
                            <div>
                                <i class="fa fa-file-text"/> Required: <field name="document_required_count"/>
                                | Deliverable: <field name="document_deliverable_count"/>
                            </div>
                        </div>
                        <div class="o_kanban_record_bottom">
                            <button type="object" name="action_view_documents" 
                                    class="btn btn-sm btn-secondary">
                                Documents
                            </button>
                            <button type="object" name="action_create_quotation" 
                                    class="btn btn-sm btn-primary">
                                Create SO
                            </button>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

### **View 2: Advanced Search Wizard**

**Features:**
- Multiple filter panels
- Live result count
- Save/load filter presets
- Export results to CSV

```xml
<record id="view_product_search_wizard_form" model="ir.ui.view">
    <field name="name">product.search.wizard.form</field>
    <field name="model">product.search.wizard</field>
    <field name="arch" type="xml">
        <form string="Advanced Product Search">
            <sheet>
                <group>
                    <group string="Basic Filters">
                        <field name="name"/>
                        <field name="categ_id"/>
                        <field name="service_type_id"/>
                        <field name="target_department"/>
                    </group>
                    <group string="Price Range">
                        <field name="price_min"/>
                        <field name="price_max"/>
                        <field name="has_multiyear"/>
                    </group>
                </group>
                
                <group>
                    <group string="Document Requirements">
                        <field name="requires_passport"/>
                        <field name="requires_emirates_id"/>
                        <field name="requires_business_plan"/>
                        <field name="min_required_docs"/>
                        <field name="min_deliverable_docs"/>
                    </group>
                    <group string="Compliance & Tracking">
                        <field name="compliance_level"/>
                        <field name="requires_compliance"/>
                        <field name="service_tracking"/>
                        <field name="has_project_template"/>
                    </group>
                </group>
                
                <group string="Quick Filters">
                    <group>
                        <field name="is_visa_service"/>
                        <field name="is_accounting_service"/>
                    </group>
                    <group>
                        <field name="is_banking_service"/>
                        <field name="is_setup_service"/>
                    </group>
                </group>
                
                <group>
                    <field name="result_count" readonly="1"/>
                </group>
                
                <notebook>
                    <page string="Search Results">
                        <field name="product_ids" nolabel="1">
                            <tree>
                                <field name="name"/>
                                <field name="categ_id"/>
                                <field name="service_type_id"/>
                                <field name="list_price"/>
                                <field name="target_department"/>
                            </tree>
                        </field>
                    </page>
                    
                    <page string="Save Filter">
                        <group>
                            <field name="save_filter"/>
                            <field name="filter_name" attrs="{'invisible': [('save_filter', '=', False)], 'required': [('save_filter', '=', True)]}"/>
                        </group>
                    </page>
                </notebook>
            </sheet>
            
            <footer>
                <button name="action_search" string="Search" type="object" class="btn-primary"/>
                <button name="action_save_filter" string="Save Filter" type="object" 
                        attrs="{'invisible': [('save_filter', '=', False)]}" 
                        class="btn-secondary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## 📥 **Data Import & Migration**

### **Feature 7: Freezoner Product Import Wizard**

**Model:** `product.import.wizard` (transient)

**Purpose:** Import products from Freezoner CSV or direct database connection

**Features:**
- CSV upload with template
- Direct Odoo 19 database connection
- Smart field mapping
- Bulk categorization
- Validation & preview before import

**Fields:**
```python
import_method = fields.Selection([
    ('csv', 'CSV Upload'),
    ('database', 'Direct Database Connection'),
], default='csv', required=True)

# CSV Import
csv_file = fields.Binary(string='CSV File')
csv_filename = fields.Char(string='Filename')
has_header = fields.Boolean(string='First Row is Header', default=True)

# Database Import
db_host = fields.Char(string='Database Host')
db_port = fields.Integer(string='Port', default=8069)
db_name = fields.Char(string='Database Name')
db_user = fields.Char(string='Username')
db_password = fields.Char(string='Password')

# Mapping Options
auto_categorize = fields.Boolean(string='Auto-Categorize Products', default=True)
create_missing_categories = fields.Boolean(string='Create Missing Categories', default=True)
skip_existing = fields.Boolean(string='Skip Existing Products', default=True)

# Preview
import_preview_ids = fields.One2many('product.import.preview', 'wizard_id')
total_products = fields.Integer(compute='_compute_totals')
valid_products = fields.Integer(compute='_compute_totals')
invalid_products = fields.Integer(compute='_compute_totals')

# Results
import_log = fields.Text(string='Import Log', readonly=True)
```

**CSV Template:**
```csv
Name,Reference Code,Category,Service Type,Department,Price,Service Tracking,Required Docs,Deliverable Docs,Compliance Level
"Corporate Tax Registration",CTR,Accounting Services,Tax Services,Accounts,1000,new_workflow,"passport,emirates_id,business_plan","tax_certificate,registration_letter",high
"Employment Visa",VISA-EMP,Visa Services,Employment Visa,Operations,2500,new_workflow,"passport,photo,noc,medical","visa_page,emirates_id,labor_card",high
```

---

## 🚀 **Implementation Phases**

### **Phase 1: Core Module (Week 1)** ✅ **PRIORITY**

**Days 1-2: Module Structure & Models**
- [x] Create module folder structure
- [ ] Create enhanced product.category model
- [ ] Create enhanced product.template model
- [ ] Create product.service.type model
- [ ] Create product.department model
- [ ] Create security rules

**Days 3-4: Basic Views**
- [ ] Enhanced product category views
- [ ] Enhanced product template views (tree, form, kanban)
- [ ] Service type views
- [ ] Department views
- [ ] Menu structure

**Days 5-7: Master Data**
- [ ] Service type taxonomy data
- [ ] Department master data
- [ ] Sample categorized products
- [ ] Testing basic functionality

---

### **Phase 2: Advanced Search (Week 2)**

**Days 1-3: Search Wizard**
- [ ] Product search wizard model
- [ ] Search wizard form view
- [ ] Search domain builder
- [ ] Results display

**Days 4-5: Saved Filters**
- [ ] Search preset model
- [ ] Preset views
- [ ] Pre-defined filters
- [ ] Filter management

**Days 6-7: Testing**
- [ ] Test all search combinations
- [ ] Performance optimization
- [ ] User acceptance testing

---

### **Phase 3: Import & Migration (Week 3)**

**Days 1-3: CSV Import**
- [ ] CSV upload wizard
- [ ] CSV parser and validator
- [ ] Field mapping
- [ ] Preview and validation

**Days 4-5: Database Import**
- [ ] Odoo RPC connector
- [ ] Direct database query
- [ ] Data transformation
- [ ] Bulk import processing

**Days 6-7: Testing & Documentation**
- [ ] Import testing with sample data
- [ ] User documentation
- [ ] Migration guide

---

### **Phase 4: Polish & Deploy (Week 4)**

**Days 1-2: UI/UX Enhancement**
- [ ] Kanban view refinement
- [ ] Color coding and icons
- [ ] Quick actions
- [ ] Smart buttons

**Days 3-4: Performance**
- [ ] Query optimization
- [ ] Indexing
- [ ] Caching
- [ ] Load testing

**Days 5-7: Production Deployment**
- [ ] Final testing
- [ ] Data migration
- [ ] User training
- [ ] Go-live support

---

## 📋 **Success Criteria**

### **Must Have (MVP)**
- ✅ Enhanced product categorization with service types
- ✅ Advanced search with multiple filters
- ✅ Department-based product organization
- ✅ CSV import capability
- ✅ Basic kanban and tree views

### **Should Have**
- ✅ Saved search presets
- ✅ Document-based filtering
- ✅ Compliance level tracking
- ✅ Direct database import
- ✅ Export functionality

### **Nice to Have**
- Analytics dashboard
- Product comparison tool
- Recommendation engine
- Mobile-optimized views
- API for external integration

---

## 🎯 **Next Steps**

1. **Review & Approve Plan**: Get stakeholder approval
2. **Create Module Structure**: Start Phase 1, Day 1
3. **Build Core Models**: Implement enhanced models
4. **Test with Sample Data**: Use Freezoner product samples
5. **Iterate & Refine**: Based on user feedback

---

**Created By:** GitHub Copilot  
**Date:** January 20, 2026  
**Status:** Ready for Implementation  
**Next Review:** After Phase 1 completion
