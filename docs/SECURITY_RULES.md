# SECURITY RULES — Access Validation Policy

## Mandatory Rules (MVP)
1. **Signed Tokens**
   - Resident and invitation credentials must be digitally signed.
2. **Expiring QR Codes**
   - Resident pass QR and invitation tokens must have short validity windows.
3. **Single-Use Visitor Passes**
   - Visitor invitations are single-use by default.
4. **Gate-Specific Validation**
   - Access only allowed on configured gates.
5. **Time-Window Validation**
   - Validate `valid_from` and `valid_to` on every scan.
6. **Resident/Unit Active Validation**
   - Blocked or inactive resident/unit always rejected.
7. **Device Authorization**
   - Only registered active N60 devices can call verify endpoints.
8. **Audit Logs**
   - Every PASS/REJECT request is logged with reason code.
9. **Role-Based Access Rights**
   - Strict roles for resident, guard, admin, and security admin actions.

## Future Rule
- **Anti-passback** (Phase 6+): Detect repeated entry without corresponding exit logic.

## Decision Matrix
| Check | On Failure | REJECT Reason |
|---|---|---|
| Token signature | Reject scan | `INVALID_SIGNATURE` |
| Token expiry | Reject scan | `TOKEN_EXPIRED` |
| Device active | Reject scan | `DEVICE_UNAUTHORIZED` |
| Gate scope | Reject scan | `GATE_NOT_ALLOWED` |
| Resident/unit active | Reject scan | `ENTITY_BLOCKED` |
| Invitation used | Reject scan | `INVITATION_ALREADY_USED` |

## Audit Requirements
- Immutable log record per verification attempt
- Store request metadata and evaluated reason code
- Include operator/device/gate references
- Support admin and audit export filters

## Final Summary
Security is enforced through signed, expiring credentials, strict entity/device validation, and complete audit trails, with anti-passback and offline controls deferred to future phases.
