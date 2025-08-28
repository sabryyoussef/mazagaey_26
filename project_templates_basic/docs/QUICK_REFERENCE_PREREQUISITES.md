# 🚀 Quick Reference: Prerequisite Tasks

## 📍 Where to Find It
**Path**: Task Templates → Open Template → **Task Configuration Tab** → **Prerequisite Tasks** field

## ⚡ Quick Setup (3 Steps)
1. **Open** task template
2. **Go to** Task Configuration tab  
3. **Select** prerequisite templates from dropdown

## 🎯 Common Patterns

### Sequential Flow
```
Collect → Review → Submit → Approve
   ↓       ↓        ↓       ↓
  None → Collect → Review → Submit
```

### Parallel to Sequential
```
Collect Required ────┐
                     ├──→ Review All → Submit
Collect Deliverable ─┘
```

### Milestone Checkpoints
```
Setup → Documents → Review Milestone → Final Milestone
```

## ⚠️ Remember
- ✅ **Can have multiple** prerequisites per template
- ✅ **Automatically creates** task dependencies in projects
- ❌ **Avoid circular** dependencies (A→B→A)
- ❌ **Don't over-complicate** - keep workflows simple

## 🔧 Testing
Create a test project to verify your dependency chain works as expected!

---
*Quick access: Project Templates → Task Templates → Task Configuration*
