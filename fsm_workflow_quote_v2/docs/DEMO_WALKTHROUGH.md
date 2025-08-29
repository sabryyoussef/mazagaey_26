# 🚀 Demo Walkthrough - Dynamic Quotation System

## 📋 **What You'll See After Installation**

When you install the FSM Workflow module with demo data, you'll have:

### **🏗️ Construction Project**
- **Client**: ABC Construction Corp
- **Project**: Office Building Construction
- **Milestones**: Foundation Complete, Structural Framework Complete
- **Checkpoints**: 6 checkpoints with quotation triggers

### **🖥️ Software Project**
- **Client**: TechStart Solutions
- **Project**: E-commerce Platform
- **Milestones**: Authentication System Complete
- **Checkpoints**: 3 checkpoints with quotation triggers

---

## 🎯 **Demo Walkthrough - Step by Step**

### **Step 1: Access the Demo Data**

1. **Open Odoo** and log in
2. **Navigate to**: FSM Workflow → Workflow Instances
3. **You'll see 2 demo workflows**:
   - "ABC Construction - Office Building Project"
   - "TechStart - E-commerce Platform"

### **Step 2: Explore the Construction Project**

1. **Click on**: "ABC Construction - Office Building Project"
2. **Notice the details**:
   - **Partner**: ABC Construction Corp
   - **Pricing Policy**: Fixed
   - **State**: Running

3. **Click "Open Project"** button (🔧 icon)
4. **In the project form, go to "Configuration" tab**
5. **Click on "Milestones"** to see project milestones
6. **You'll see 2 milestones**:
   - **Foundation Complete** (with quotation trigger)
   - **Structural Framework Complete** (with quotation trigger)

### **Step 3: Test Checkpoint-Triggered Quotations**

#### **Test 1: Foundation Checkpoints**

1. **Click on "Foundation Complete" milestone** (opens milestone form)
2. **In the milestone form, go to "Checkpoints" tab**
3. **You'll see 4 checkpoints**:
   - Site Preparation (no quotation trigger)
   - Excavation Complete (no quotation trigger)
   - Foundation Poured (✅ quotation trigger)
   - Foundation Inspection Passed (✅ quotation trigger)

4. **Mark "Foundation Poured" as reached**:
   - Click the checkbox next to "Foundation Poured"
   - **Result**: ✅ **Quotation automatically created!**

5. **Check the quotation**:
   - **Navigate to**: Sales → Orders → Quotations
   - **Look for**: "Checkpoint Quotation - Foundation Poured - ABC Construction..."
   - **Open it** and verify:
     - **Workflow Instance**: ABC Construction project
     - **Trigger Type**: Checkpoint Reached
     - **Trigger Name**: Foundation Poured
     - **Amount**: $165,000 (Foundation Work + Safety Inspection)

6. **Mark "Foundation Inspection Passed" as reached**:
   - Click the checkbox next to "Foundation Inspection Passed"
   - **Result**: ✅ **Another quotation created!**

#### **Test 2: Milestone Completion**

1. **Go back to the milestone**
2. **Notice**: All checkpoints are now reached
3. **Check**: Milestone should be marked as "Reached"
4. **Result**: ✅ **Milestone quotation automatically created!**

5. **Check the milestone quotation**:
   - **Navigate to**: Sales → Orders → Quotations
   - **Look for**: "Milestone Quotation - Foundation Complete - ABC Construction..."
   - **Open it** and verify:
     - **Trigger Type**: Milestone Reached
     - **Trigger Name**: Foundation Complete
     - **Amount**: $165,000

### **Step 4: Test Manual Quotation Creation**

1. **Go back to the Workflow Instance**
2. **Click "Create Quotation"** button (📄 icon)
3. **Fill in the quotation**:
   - **Customer**: Should be pre-filled (ABC Construction Corp)
   - **Add a line**: "Additional Services" - Qty: 1 - Price: $10,000
4. **Click "Save"**
5. **Result**: ✅ **Manual quotation linked to workflow**

### **Step 5: Test Quotation Management**

1. **In the Workflow Instance, click "All Quotations"** button (📋 icon)
2. **You should see 4 quotations**:
   - 2 checkpoint-triggered quotations
   - 1 milestone-triggered quotation
   - 1 manual quotation

3. **Test filtering**:
   - **Click on any quotation**
   - **Look for "Workflow Integration" section**
   - **Click "Workflow Instance"** button
   - **Result**: ✅ **Navigates back to workflow**

### **Step 6: Explore the Software Project**

1. **Go back to Workflow Instances**
2. **Click on**: "TechStart - E-commerce Platform"
3. **Notice the details**:
   - **Partner**: TechStart Solutions
   - **Pricing Policy**: Time & Materials (TM)
   - **State**: Running

4. **Open the project and explore**:
   - **Go to "Configuration" tab** → **Click "Milestones"**
   - **Milestone**: Authentication System Complete
   - **Checkpoints**: 3 checkpoints with quotation triggers

5. **Test the same process**:
   - Mark checkpoints as reached
   - Watch quotations being created
   - Verify workflow integration

---

## 📊 **Expected Results Summary**

### **Construction Project Results**:
| Action | Quotations Created | Total Amount |
|--------|-------------------|--------------|
| Foundation Poured | 1 checkpoint quotation | $165,000 |
| Foundation Inspection | 1 checkpoint quotation | $165,000 |
| Milestone Complete | 1 milestone quotation | $165,000 |
| Manual Creation | 1 manual quotation | $10,000 |
| **TOTAL** | **4 quotations** | **$505,000** |

### **Software Project Results**:
| Action | Quotations Created | Total Amount |
|--------|-------------------|--------------|
| Database Design | 1 checkpoint quotation | $75,000 |
| Auth System Built | 1 checkpoint quotation | $75,000 |
| Security Testing | 1 checkpoint quotation | $75,000 |
| Milestone Complete | 1 milestone quotation | $75,000 |
| **TOTAL** | **4 quotations** | **$300,000** |

---

## 🔍 **What to Look For**

### **✅ Successful Features**:
- **Automatic Quotation Creation**: Quotations appear instantly when checkpoints/milestones are reached
- **Proper Linking**: All quotations are linked to their workflow instances
- **Trigger Tracking**: Each quotation shows what triggered it (checkpoint/milestone/manual)
- **Template Application**: Quotation lines match the configured templates
- **Workflow Integration**: Easy navigation between quotations and workflows

### **🎯 Key Testing Points**:
1. **Checkpoint Triggers**: Only checkpoints with "Create Quotation on Reach" checked create quotations
2. **Milestone Triggers**: Milestones create quotations when all checkpoints are reached
3. **Manual Creation**: Manual quotations are properly linked to workflows
4. **Template Application**: Templates are applied with correct pricing
5. **Context Preservation**: All quotation context is maintained

---

## 🚨 **Troubleshooting Demo Issues**

### **If demo data doesn't appear**:
1. **Check**: Module is installed with demo data
2. **Check**: Database was created with demo data option
3. **Solution**: Reinstall module with demo data

### **If quotations aren't creating**:
1. **Check**: Workflow instances have partners assigned
2. **Check**: Checkpoints have quotation triggers enabled
3. **Check**: Quotation templates exist and are active

### **If templates aren't applying**:
1. **Check**: Demo products exist in the system
2. **Check**: Template lines have valid products
3. **Check**: Products have pricing configured

---

## 🎉 **Demo Success Criteria**

The demo is working correctly if you see:

- ✅ **2 workflow instances** with demo data
- ✅ **Automatic quotation creation** when checkpoints are reached
- ✅ **Milestone quotations** when all checkpoints are completed
- ✅ **Manual quotations** linked to workflows
- ✅ **Proper trigger tracking** in all quotations
- ✅ **Template application** with correct pricing
- ✅ **Workflow integration** working properly
- ✅ **Total of 8 quotations** created across both projects

---

## 🚀 **Next Steps After Demo**

1. **Create your own workflows** using the demo as a template
2. **Customize quotation templates** for your business needs
3. **Set up real projects** with your actual clients
4. **Configure milestones and checkpoints** for your specific processes
5. **Test with real data** to ensure everything works for your use case

This demo walkthrough shows you exactly how the Dynamic Quotation System works in practice! 🎯
