# CRM Connector Design Note

## Context

The ERP system sends customer updates to the CRM connector through a REST API. The connector validates field names, maps internal identifiers, and forwards the payload to the CRM endpoint.

## Design Constraints

- The ERP payload uses `customerId`.
- The CRM endpoint expects `customer_id`.
- The connector must reject malformed payloads before forwarding.
- The connector must log request ID, source system, response status, and retry count.
- Retries must be idempotent because CRM updates can be replayed.

## Engineering Risks

- Field mapping drift can break synchronization.
- Retry behavior can create duplicate updates if idempotency keys are missing.
- Missing logs make production investigation slower.

## Suggested Validation

- Add API contract tests for field mapping.
- Add integration tests with duplicated retry payloads.
- Add log assertions for failed CRM responses.
