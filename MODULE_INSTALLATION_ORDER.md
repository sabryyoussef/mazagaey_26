# Module Installation Order

## Dependency Analysis

Based on the `__manifest__.py` files, here's the dependency tree:

```
Level 1 (Base Dependencies):
├── project_checkpoints_basic
│   └── Depends on: base, project, product, documents, sale_management

Level 2 (Depends on Level 1):
├── project_templates_basic
│   └── Depends on: base, project, product, documents, project_checkpoints_basic, sale_management

Level 3 (Depends on Level 2):
├── unified_documents
│   └── Depends on: base, product, project, documents, sale, sale_project, purchase, project_templates_basic
├── smart_templates
│   └── Depends on: base, project, product, documents, sale_management, project_checkpoints_basic, unified_documents

Level 4 (Depends on Level 3):
├── project_handover_notes
│   └── Depends on: base, project, mail, unified_documents, project_templates_basic, project_checkpoints_basic
├── project_compliance
│   └── Depends on: base, project, mail, unified_documents, project_handover_notes, project_templates_basic, project_checkpoints_basic

Level 5 (Depends on Level 4):
└── fsm_workflow_quote_v2
    └── Depends on: base, project, sale_management, hr_timesheet, project_templates_basic, project_checkpoints_basic
```

---

## ✅ Recommended Installation Order

### Step 1: Install Base Module
```
1. project_checkpoints_basic
   - No custom module dependencies
   - Provides checkpoint and milestone functionality
```

### Step 2: Install Template Foundation
```
2. project_templates_basic
   - Depends on: project_checkpoints_basic
   - Provides workflow and template models
```

### Step 3: Install Document Management
```
3. unified_documents
   - Depends on: project_templates_basic
   - Provides document management extensions
```

### Step 4: Install Smart Features (Optional - can be installed later)
```
4. smart_templates
   - Depends on: project_checkpoints_basic, unified_documents
   - Provides AI/smart template suggestions
```

### Step 5: Install Handover System
```
5. project_handover_notes
   - Depends on: unified_documents, project_templates_basic, project_checkpoints_basic
   - Provides handover documentation
```

### Step 6: Install Compliance Module
```
6. project_compliance
   - Depends on: unified_documents, project_handover_notes, project_templates_basic, project_checkpoints_basic
   - Provides compliance and shareholder management
```

### Step 7: Install FSM Workflow (if needed)
```
7. fsm_workflow_quote_v2
   - Depends on: project_templates_basic, project_checkpoints_basic
   - Provides Field Service Management workflows
```

---

## Quick Install Command

After creating your database in Odoo, install in this order:

```bash
# From Odoo Apps menu, search and install in this exact order:

1. Project Checkpoints Basic
2. Project Templates Basic
3. Unified Documents Extension
4. Smart Templates (optional)
5. Project Handover Notes
6. Project Compliance
7. FSM Workflow → Quotation v2 (if needed for field service)
```

---

## Critical Notes

⚠️ **Important:**
- Install in the exact order shown above
- Wait for each module to fully install before installing the next
- Missing dependencies will cause installation failures
- `project_checkpoints_basic` MUST be installed first

🔧 **Enterprise Dependencies:**
- All modules require Odoo Enterprise `documents` module
- Make sure you have Odoo Enterprise license activated

📋 **Optional Modules:**
- `smart_templates` - Can be skipped if you don't need smart suggestions
- `fsm_workflow_quote_v2` - Only needed for Field Service Management workflows

---

## Installation via Database Manager

When creating a new database through http://localhost:8069/web/database/manager:

1. **Database Name:** Choose a meaningful name (e.g., `mazagawy_production`)
2. **Master Password:** Use `admin` (as configured in odoo.conf)
3. **Demo Data:** Choose "Without demonstration data" for production
4. **Language:** Select your preferred language
5. **Country:** Select your country

After database creation:
- Login with admin credentials
- Go to Apps menu
- Remove "Apps" filter to see all modules
- Search and install modules in the order listed above

---

## Troubleshooting

**If you see "module not found" errors:**
1. Check that addons path is correct in odoo.conf: `/opt/odoo/extra-addons,/opt/odoo/enterprise-addons`
2. Restart Odoo container: `docker-compose restart odoo`
3. Update apps list: Apps → Update Apps List

**If dependencies fail:**
- Ensure enterprise addons are properly mounted
- Check that `documents` module is available (Enterprise only)
- Verify all parent modules are installed first
