# Product charter

## Outcome

A governed decision layer above or alongside systems of record and planning engines.

## Explicit non-goals

A replacement for SAP, o9, Kinaxis, or another planning system; an autonomous write-back agent.

## Accountable buyer and decision

- Buyer: CSCO / VP Demand Planning
- Decision: Which demand or inventory intervention should we take, with what confidence and value?

## Technical posture

BigQuery, Gemini, ADK, Cloud Run or Agent Runtime, with explicit hybrid-cloud interoperability.

Technology choices must follow validated workflow needs. Deterministic business logic, explicit human approval, provenance, security, cost, and failure handling take priority over adding agents.

## Proof before claim

Six practitioner interviews, three repeat reviewers, and three unguided tests across five workflows.

## Stop condition

If relevant users cannot independently complete five workflows, narrow the product until they can.
