# IMPLEMENTATION PHASES — Delivery Plan

## Phase 0: Repository and Documentation
### Scope
Planning repository structure and full specifications.
### Deliverables
README and all planning docs.
### Acceptance Criteria
All required documents complete and aligned.
### Out of Scope
Any production code.

## Phase 1: Odoo Backend MVP
### Scope
Core models, APIs, and QR validation logic.
### Deliverables
Odoo endpoints for pass/invitation verification, logging, and device config.
### Acceptance Criteria
N60 can verify QR and receive PASS/REJECT from Odoo.
### Out of Scope
Mobile app and NFC implementation.

## Phase 2: N60 QR Gate Scanner App
### Scope
N60 app for device auth, QR scan, and result display.
### Deliverables
Operational scanner app with heartbeat.
### Acceptance Criteria
Guard can scan resident/invitation QR and see deterministic decision.
### Out of Scope
Offline queue and NFC scan mode.

## Phase 3: Resident Mobile App QR Pass and Invitations
### Scope
Resident login, dynamic QR, and invitation creation/sharing.
### Deliverables
Resident app MVP connected to Odoo APIs.
### Acceptance Criteria
Resident can enter with QR and generate invitation QR successfully.
### Out of Scope
Advanced analytics and offline support.

## Phase 4: Delivery and Visitor Enhancements
### Scope
Specialized visitor/delivery flows and policy refinements.
### Deliverables
Enhanced invitation controls, statuses, and admin workflows.
### Acceptance Criteria
Delivery and visitor scenarios pass end-to-end with traceable logs.
### Out of Scope
NFC HCE and anti-passback advanced logic.

## Phase 5: NFC HCE Research and Implementation
### Scope
Feasibility, architecture, and implementation of phone-based NFC credentials.
### Deliverables
NFC design, prototype, and integration plan.
### Acceptance Criteria
Controlled pilot validates NFC read and backend decision flow.
### Out of Scope
Offline synchronization strategy.

## Phase 6: Offline Mode and Advanced Security
### Scope
Offline scan queue, sync conflict rules, anti-passback.
### Deliverables
Offline architecture, queue processing, advanced security policies.
### Acceptance Criteria
Graceful degraded mode with synchronized audit consistency.
### Out of Scope
New actor-facing app modules.

## Phase 7: Dashboards and Reporting
### Scope
Operational dashboards, audit analytics, and alerting views.
### Deliverables
Admin/security KPI dashboards and filterable reports.
### Acceptance Criteria
Management can inspect trends, incidents, and compliance evidence.
### Out of Scope
Core access flow redesign.

## Final Summary
The phased plan starts with documentation and QR MVP essentials, then incrementally expands into app features, advanced controls, NFC, offline capabilities, and reporting.
