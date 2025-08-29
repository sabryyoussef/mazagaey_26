# Field Reference - FSM Workflow Instance

## 📋 **Available States**

The FSM Workflow Instance has the following states:

| State Value | Display Name | Description |
|-------------|--------------|-------------|
| `running` | Running | Workflow is active and in progress |
| `quoted` | Quoted | Quotation has been sent to customer |
| `closed` | Closed | Workflow has been completed |

**Default State**: `running`

## 💰 **Available Pricing Policies**

The FSM Workflow Instance supports the following pricing policies:

| Policy Value | Display Name | Description |
|--------------|--------------|-------------|
| `tm` | Time & Materials | Billing based on actual time and materials used |
| `fixed` | Fixed Price | Fixed price for the entire project |
| `hybrid` | Hybrid | Combination of fixed price and time & materials |

**Default Policy**: `tm`

## 🔧 **Field Definitions**

### **Core Fields**
- `name`: Char (required) - Workflow instance name
- `project_id`: Many2one (required) - Linked project
- `partner_id`: Many2one (required) - Customer/client
- `pricing_policy`: Selection - How the project is billed
- `state`: Selection - Current status of the workflow

### **Integration Fields**
- `sale_order_id`: Many2one - Last quotation created
- `template_id`: Many2one - Workflow template used
- `fsm_order_id`: Char - Reference to FSM order

### **Computed Fields**
- `timesheet_hours`: Float - Total hours from timesheets
- `total_checkpoints`: Integer - Total number of checkpoints
- `completed_checkpoints`: Integer - Number of completed checkpoints
- `checkpoint_progress`: Float - Percentage of checkpoints completed

## 📝 **Usage Examples**

### **Creating a Fixed Price Project**
```python
workflow = self.env['fsm.workflow.instance'].create({
    'name': 'Office Building Construction',
    'partner_id': customer.id,
    'project_id': project.id,
    'pricing_policy': 'fixed',
    'state': 'running',
})
```

### **Creating a Time & Materials Project**
```python
workflow = self.env['fsm.workflow.instance'].create({
    'name': 'Software Development',
    'partner_id': client.id,
    'project_id': project.id,
    'pricing_policy': 'tm',
    'state': 'running',
})
```

### **Changing State to Quoted**
```python
workflow.state = 'quoted'
```

### **Closing a Project**
```python
workflow.state = 'closed'
```

## 🎯 **State Transitions**

### **Typical Workflow**
1. **Running** → Project starts and is active
2. **Quoted** → Quotation sent to customer
3. **Closed** → Project completed

### **State Rules**
- New workflows start in **Running** state
- Can move from **Running** to **Quoted** when quotation is sent
- Can move from **Quoted** to **Running** if quotation is revised
- Can move from any state to **Closed** when project is complete

## 📊 **Pricing Policy Guidelines**

### **Time & Materials (TM)**
- **Best for**: Projects with uncertain scope
- **Billing**: Based on actual time and materials
- **Risk**: Higher risk for customer, lower risk for contractor
- **Use case**: Software development, consulting, maintenance

### **Fixed Price**
- **Best for**: Well-defined projects with clear scope
- **Billing**: Fixed amount regardless of time/materials
- **Risk**: Lower risk for customer, higher risk for contractor
- **Use case**: Construction, manufacturing, standard services

### **Hybrid**
- **Best for**: Projects with fixed and variable components
- **Billing**: Combination of fixed price + time & materials
- **Risk**: Shared risk between customer and contractor
- **Use case**: Complex projects with standard and custom components

---

This reference helps you understand the available options when creating and managing FSM workflow instances.
