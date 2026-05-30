# Approval Workflow Requirement

## Business Rule

The expense approval workflow must route a request to the direct manager when the amount is below 10,000,000 VND.

When the amount is equal to or above 10,000,000 VND, the workflow must route to the department head after manager approval.

## Acceptance Criteria

- A submitted expense request must show the current approval owner.
- The workflow must prevent approval by the requester.
- If the direct manager rejects the request, the request status becomes `Rejected`.
- If the direct manager approves an amount above the threshold, the next owner becomes the department head.
- The audit log must record approver, decision, timestamp, and note.

## Open Questions

- What should happen if the requester has no manager assigned?
- Should the threshold include tax?
- Is delegation allowed when an approver is on leave?
