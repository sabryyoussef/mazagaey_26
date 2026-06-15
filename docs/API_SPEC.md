# API SPEC — Planned REST APIs

## Common Rules
- Base path: `/compound_access/api`
- Authentication: device API key for gate endpoints, resident JWT/session for invitation creation
- Responses include `status`, `decision`, `reason_code`, and `server_time`
- All accepted/rejected scans are logged

---

## POST /compound_access/api/verify_pass
### Purpose
Validate resident digital pass (QR now, NFC token future).

### Request JSON
```json
{
  "device_id": "DEV-001",
  "gate_id": "GATE-A",
  "pass_token": "eyJ...",
  "scan_time": "2026-06-15T07:10:00Z",
  "mode": "QR"
}
```

### Response JSON
```json
{
  "status": "ok",
  "decision": "PASS",
  "reason_code": "VALID",
  "decision_id": "DEC-1001",
  "resident": {"id": 45, "name": "Resident Name"},
  "server_time": "2026-06-15T07:10:01Z"
}
```

### PASS Example
Resident active, unit active, gate allowed, token valid and unexpired.

### REJECT Example
```json
{"status":"ok","decision":"REJECT","reason_code":"TOKEN_EXPIRED","decision_id":"DEC-1002"}
```

### Validation Rules
- Device must be authorized and active
- Gate must be active
- Token signature and expiry must be valid
- Resident and linked unit must be active
- Gate scope and time window must pass

---

## POST /compound_access/api/create_invitation
### Purpose
Create visitor/delivery/maintenance invitation with constrained validity.

### Request JSON
```json
{
  "resident_id": 45,
  "type": "visitor",
  "valid_from": "2026-06-15T08:00:00Z",
  "valid_to": "2026-06-15T18:00:00Z",
  "allowed_gate_ids": ["GATE-A"],
  "single_use": true,
  "guest_name": "Ahmed Ali"
}
```

### Response JSON
```json
{
  "status": "ok",
  "invitation_id": 992,
  "invitation_token": "eyJ...",
  "qr_payload": "INV:eyJ...",
  "expires_at": "2026-06-15T18:00:00Z"
}
```

### PASS Example
Invitation created successfully and returned for sharing.

### REJECT Example
```json
{"status":"error","reason_code":"RESIDENT_BLOCKED"}
```

### Validation Rules
- Resident must own or be assigned to selected unit
- Validity window must be coherent (`valid_to > valid_from`)
- Invitation type must be one of: visitor, delivery, maintenance
- Gate list must reference active gates

---

## POST /compound_access/api/verify_invitation
### Purpose
Validate invitation QR at gate and consume single-use token where applicable.

### Request JSON
```json
{
  "device_id": "DEV-001",
  "gate_id": "GATE-A",
  "invitation_token": "eyJ...",
  "scan_time": "2026-06-15T09:15:00Z"
}
```

### Response JSON
```json
{
  "status": "ok",
  "decision": "PASS",
  "reason_code": "VALID_INVITATION",
  "decision_id": "DEC-2001",
  "invitation_id": 992,
  "server_time": "2026-06-15T09:15:00Z"
}
```

### PASS Example
Unexpired invitation within time window and allowed gate; unused if single-use.

### REJECT Example
```json
{"status":"ok","decision":"REJECT","reason_code":"INVITATION_ALREADY_USED","decision_id":"DEC-2002"}
```

### Validation Rules
- Invitation must exist and be active
- Token must be signed and not expired
- Gate/device must be allowed and active
- Single-use invitation cannot be reused

---

## POST /compound_access/api/log_exit
### Purpose
Record optional exit event for movement tracking.

### Request JSON
```json
{
  "device_id": "DEV-001",
  "gate_id": "GATE-A",
  "entity_type": "resident",
  "entity_token": "eyJ...",
  "event_time": "2026-06-15T17:30:00Z"
}
```

### Response JSON
```json
{
  "status": "ok",
  "decision": "PASS",
  "reason_code": "EXIT_LOGGED",
  "log_id": 7811
}
```

### PASS Example
Exit event accepted and linked to entity.

### REJECT Example
```json
{"status":"error","decision":"REJECT","reason_code":"INVALID_ENTITY_TOKEN"}
```

### Validation Rules
- Device and gate must be authorized
- Entity token must decode to known resident/invitation
- Exit timestamp cannot be malformed

---

## GET /compound_access/api/device_config
### Purpose
Provide gate device with runtime configuration.

### Request JSON
No body; authenticated by API key.

### Response JSON
```json
{
  "status": "ok",
  "device_id": "DEV-001",
  "gate_id": "GATE-A",
  "scan_modes": ["QR"],
  "future_scan_modes": ["NFC"],
  "heartbeat_interval_sec": 60,
  "photo_capture_enabled": false
}
```

### PASS Example
Authorized device receives config profile.

### REJECT Example
```json
{"status":"error","reason_code":"DEVICE_UNAUTHORIZED"}
```

### Validation Rules
- API key must map to active device
- Device must be assigned to active gate

---

## POST /compound_access/api/device_heartbeat
### Purpose
Track N60 health, connectivity, and app version.

### Request JSON
```json
{
  "device_id": "DEV-001",
  "app_version": "1.0.0",
  "battery": 78,
  "network": "wifi",
  "timestamp": "2026-06-15T07:30:00Z"
}
```

### Response JSON
```json
{
  "status": "ok",
  "decision": "PASS",
  "reason_code": "HEARTBEAT_ACCEPTED",
  "next_heartbeat_sec": 60
}
```

### PASS Example
Active device heartbeat accepted.

### REJECT Example
```json
{"status":"error","decision":"REJECT","reason_code":"DEVICE_BLOCKED"}
```

### Validation Rules
- Device must be active and not blocked
- Timestamp must be within acceptable drift
- App version policy checks may be enforced

## Final Summary
These APIs define the MVP verification and invitation workflows with strict validation, auditable outcomes, and a clear PASS/REJECT contract for N60 gate operations.
