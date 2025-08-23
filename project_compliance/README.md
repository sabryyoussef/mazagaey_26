# Project Compliance Module

## Overview
This module provides comprehensive compliance functionality for Odoo projects, including shareholder management, UBO tracking, and compliance workflows. It integrates with `project_handover_notes`, `unified_documents`, `project_templates_basic`, and `project_checkpoints_basic` modules.

## Features

### 🏗️ **Core Models**
- **`res.partner.business.shareholder`**: Business shareholder management
- **`business.relationships`**: Relationship types between shareholders
- **`res.partner.ubo`**: Ultimate beneficial owner tracking

### 📊 **Compliance Workflow**
- **Complete**: Validate shareholder data and mark compliance complete
- **Confirm**: Confirm compliance (requires task assignee or admin)
- **Return**: Return compliance for revision with reason
- **Update**: Update compliance after return
- **Repeat**: Repeat compliance process (admin only)

### 🎯 **Key Features**
- **Shareholder Management**: Individual and corporate shareholders
- **UBO Tracking**: Ultimate beneficial owner information
- **Document References**: Integration with document system
- **Validation**: Shareholding totals, required fields
- **Security**: Role-based access control
- **Odoo 18 Compatible**: Uses modern Odoo 18 standards

## Dependencies
- `base`
- `project`
- `mail`
- `unified_documents`
- `project_handover_notes`
- `project_templates_basic`
- `project_checkpoints_basic`

## Installation
1. Place the module in your `custom_addons` directory
2. Update the addons list in Odoo
3. Install the module from Apps menu

## Usage

### Project Integration
- Compliance tab appears in project form
- Manage shareholders directly in projects
- Track compliance status and workflow

### Partner Integration
- Compliance shareholders in partner form
- View compliance information per partner

### Business Shareholders
- Create and manage individual/corporate shareholders
- Track shareholding percentages
- Manage relationships and UBO information

## Security Groups
- **Compliance User**: Read-only access
- **Compliance Manager**: Create and edit access
- **Compliance Administrator**: Full access including deletion

## Data
The module includes demo data for:
- Business relationships (Family, Business Partner, Investor, Director)
- UBO types (Individual, Corporate)

## License
LGPL-3
