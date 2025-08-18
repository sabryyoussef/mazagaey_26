You are an Odoo 18 developer. Extend an existing custom module that already implements:
- model project.task.checkpoint with fields (name, sequence, task_id, is_reached, auto_advance_stage, target_stage_id, notes) and auto-advance on change
- extension of project.task adding checkpoint_ids and computed progress with stage advancement when checkpoints are marked reached

Goal: Add reusable “Task Checkpoint Configuration Templates” that can be linked to service products. When a sale order of such product creates a project/task, instantiate checkpoints from the selected template(s). Enable stage transitions when N checkpoints (by tag or count) are reached.

**Hard Requirements**

1) Data Model (new)
   a) `project.task.checkpoint.tag`
      - Fields: name (required), color
   b) `project.task.checkpoint.template`
      - Fields:
        * name (required), sequence (int, default 10)
        * line_ids (one2many -> project.task.checkpoint.template.line)
        * rule_ids (one2many -> project.task.checkpoint.rule)
        * active (bool, default True), notes (text)
   c) `project.task.checkpoint.template.line`
      - Represents a single checkpoint definition in a template
      - Fields:
        * name (required)
        * sequence (int, default 10)
        * tag_ids (many2many -> project.task.checkpoint.tag)
        * auto_advance_stage (bool, default True)
        * target_stage_id (many2one -> project.task.type)
        * notes (text)
   d) `project.task.checkpoint.rule`
      - Stage transition rules evaluated at the task level using reached checkpoints
      - Fields:
        * name (required)
        * condition_type (selection: 'all', 'min_count', 'by_tag_count', 'percentage')
        * min_count (int), percentage (float)
        * tag_ids (many2many -> project.task.checkpoint.tag)  # used when condition_type is 'by_tag_count'
        * target_stage_id (many2one -> project.task.type, required)
        * sequence (int, default 10), active (bool, default True)
   e) Product linkage
      - Inherit `product.template`:
        * field `checkpoint_template_ids` (many2many -> project.task.checkpoint.template)
        * field `auto_apply_checkpoint_templates` (bool, default True)
        * constraints: only for products with `type='service'` and a service tracking that generates tasks/projects

2) Integrations / Hooks
   a) On creation of tasks from sales (e.g., via service tracking), if the originating product has templates and auto_apply is true:
      - Instantiate `project.task.checkpoint` records from each template line (copy name, sequence, tags, auto_advance_stage, target_stage_id, notes) and link to the new task.
      - Attach the template(s) reference on the task (new m2m field `applied_checkpoint_template_ids`).
   b) Support a wizard `project.apply.checkpoint.template.wizard` to backfill/apply one or more templates to existing tasks (bulk, multi-company safe).
   c) If multiple templates are linked, merge lines by sequence; allow duplicates (same name) but deduplicate by (name + tags) if needed with a checkbox in the wizard.

3) Task Logic (extend existing behavior)
   a) Add on `project.task`:
      - `applied_checkpoint_template_ids` (m2m -> project.task.checkpoint.template, readonly once created)
      - helper compute: `checkpoint_reached_count`, `checkpoint_reached_by_tag_json` (dict stored as JSON or compute-only)
   b) Whenever a checkpoint is toggled to `is_reached=True`, evaluate rules:
      - If condition_type='all': all checkpoints reached -> move to rule.target_stage_id
      - If condition_type='min_count': reached_count >= min_count -> move
      - If condition_type='by_tag_count': for each tag in rule.tag_ids, reached_count(tag) >= min_count -> move
      - If condition_type='percentage': (reached_count / total) * 100 >= percentage -> move
   c) Stage change should respect project stage pipeline and avoid loops; only move forward (by sequence). No-op if already at target stage.
   d) Keep existing single-checkpoint auto-advance behavior, but evaluate template rules first; if no rule triggers, fall back to individual checkpoint’s target_stage_id.

4) Views / UX
   a) Menus under Project ▸ Configuration:
      - Checkpoint Tags
      - Checkpoint Templates (tree/form with notebook: Lines, Rules)
   b) Product form (service products):
      - New page “Checkpoint Templates” with m2m and auto_apply boolean; domain: type='service'
   c) Task form:
      - Stat button “Checkpoints (x/y)”
      - Smart button “Templates” (opens applied templates)
      - One2many list for checkpoints showing: sequence, name, tags, is_reached (toggle), target_stage_id; progress bar (widget) for checkpoint_progress
   d) Wizard to apply templates to selected tasks with options:
      - Merge duplicates by (name+tags)
      - Overwrite existing checkpoints (danger)
      - Append only (default)

5) Security / Data
   - `ir.model.access.csv` for new models (read for user, write/create for project user/manager)
   - Demo data:
     * Tags: Legal, KYC, Payment
     * Template: “Company Formation – Base”
       - Lines: “Collect Passport Copy” [Legal], “Collect Trade Name Options” [Legal], “Receive Initial Payment” [Payment] (target stage = In Progress), “Submit KYC Form” [KYC]
       - Rules: by_tag_count(tag=Legal, min_count=2 -> stage=In Progress); percentage(>=75% -> stage=Done)
     * A service product “Company Formation (UAE)” linked to the template

6) Technical Details
   - Odoo 18, Python 3.12. Use env-friendly create/write; no raw SQL.
   - Detect origin product on task creation via `sale_line_id.product_id` or context keys used by service tracking; support multi-company.
   - Implement a reusable method on `project.task`: `_apply_checkpoint_templates_from_products()` and `_evaluate_checkpoint_rules()`; call on checkpoint write/onchange and after template instantiation.
   - Unit tests:
     * Creating SO with the service product creates project/task and instantiates checkpoints.
     * Marking checkpoints triggers rule-based stage changes (all, min_count, by_tag_count, percentage).
     * Wizard applies template to existing tasks idempotently when “append only” is selected.

7) Performance / Edge Cases
   - Avoid recomputing aggregates per record sync; use set-based counts when multiple checkpoints updated.
   - If multiple rules qualify, apply the one with the highest sequence priority; if same, choose the target stage with higher sequence in pipeline.
   - Respect record rules; ensure write on `stage_id` is allowed.

8) Deliverables
   - New models, views, wizard, security, demo data
   - Minimal changes to existing models; keep backwards compatibility with current checkpoint behavior
   - Clear commit structure:
     * models/checkpoint_template.py, models/checkpoint_rule.py, models/checkpoint_tag.py
     * models/product_template.py (inherit)
     * wizards/apply_checkpoint_template_wizard.py
     * views/* (templates, rules, tags, product, task)
     * security/ir.model.access.csv
     * data/demo_checkpoint_templates.xml

Do not modify existing unrelated features. Follow Odoo guidelines for domains, onchange, and computed fields. Provide robust docstrings and type hints where reasonable.
