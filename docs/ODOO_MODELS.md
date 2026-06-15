# ODOO MODELS — Planned Data Model

## Model: `compound.resident`
- **Purpose:** Represent a resident/owner identity authorized for compound access.
- **Important fields:** `name`, `mobile`, `email`, `status`, `user_id`, `unit_ids`, `blocked_reason`.
- **Relationships:** Many2many with `compound.unit`; One2many with `compound.access.pass`; One2many with invitations.
- **Access rights:** Admin full; security read/limited block action; resident self-read.
- **Notes:** Status toggles should instantly affect validation results.

## Model: `compound.unit`
- **Purpose:** Represent unit/apartment metadata and occupancy status.
- **Important fields:** `code`, `building`, `floor`, `status`, `owner_resident_id`.
- **Relationships:** One2many or Many2many with `compound.resident`.
- **Access rights:** Admin full; security read-only.
- **Notes:** Unit block should reject all linked passes.

## Model: `compound.gate`
- **Purpose:** Define physical gates and policy scope.
- **Important fields:** `name`, `code`, `status`, `direction_mode`, `location`.
- **Relationships:** One2many with `compound.device`; One2many with `compound.access.log`.
- **Access rights:** Admin/security admin full; guards read-only.
- **Notes:** Gate status directly controls acceptance logic.

## Model: `compound.device`
- **Purpose:** Register authorized N60 scanner devices.
- **Important fields:** `name`, `device_uid`, `api_key_hash`, `status`, `gate_id`, `last_heartbeat`, `app_version`.
- **Relationships:** Many2one to `compound.gate`; One2many to `compound.access.log`.
- **Access rights:** Admin/security admin manage; guard read own device config.
- **Notes:** Store key hash only; never store plain API keys.

## Model: `compound.access.pass`
- **Purpose:** Represent resident access pass state and token metadata.
- **Important fields:** `resident_id`, `unit_id`, `token_version`, `expires_at`, `status`.
- **Relationships:** Many2one to `compound.resident`, `compound.unit`; One2many logs.
- **Access rights:** Backend engine writes; admin read/manage; resident limited read.
- **Notes:** Supports token rotation and forced invalidation.

## Model: `compound.visitor.invitation`
- **Purpose:** Manage visitor and maintenance invitation lifecycle.
- **Important fields:** `resident_id`, `type`, `token_hash`, `valid_from`, `valid_to`, `single_use`, `used_at`, `status`, `allowed_gate_ids`.
- **Relationships:** Many2one resident; Many2many gate; One2many logs.
- **Access rights:** Resident create/read own; admin full; guard read on verification only.
- **Notes:** Use hashed token storage; include delivery as supported type when applicable.

## Model: `compound.access.log`
- **Purpose:** Immutable audit record of each access decision.
- **Important fields:** `event_type`, `decision`, `reason_code`, `timestamp`, `gate_id`, `device_id`, `resident_id`, `invitation_id`, `raw_payload`.
- **Relationships:** Many2one to gate/device/resident/invitation.
- **Access rights:** Admin/security read; system write-only creation.
- **Notes:** Avoid manual edits; preserve forensic integrity.

## Model: `compound.delivery.visit`
- **Purpose:** Delivery-specific invitation metadata and completion status.
- **Important fields:** `resident_id`, `provider_name`, `tracking_ref`, `invitation_id`, `status`, `arrival_time`.
- **Relationships:** Many2one resident; Many2one invitation.
- **Access rights:** Resident create/read own; admin/security read/manage.
- **Notes:** Can extend analytics for courier reliability.

## Model: `compound.security.rule`
- **Purpose:** Configurable validation policies.
- **Important fields:** `name`, `rule_type`, `active`, `priority`, `config_json`, `applies_to_gate_ids`.
- **Relationships:** Many2many gates.
- **Access rights:** Security admin full; admin read.
- **Notes:** Includes time-window, gate scope, and future anti-passback rules.

## Final Summary
The planned Odoo model set supports identity, gate/device control, invitation lifecycle, and immutable logging required for secure PASS/REJECT access decisions.
