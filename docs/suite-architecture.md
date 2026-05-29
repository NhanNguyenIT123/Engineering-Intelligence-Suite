# Engineering Intelligence Suite Architecture

The portfolio is organized as a suite, not as unrelated apps.

```text
Engineering issue / test finding / validation failure
        |
        v
Issue Intake
        |
        v
IssueSense ML
  - issue type classification
  - likely cause estimation
  - similar case retrieval
  - uncertainty / human-review flag
  - next investigation steps
        |
        +----------------------+
        |                      |
        v                      v
EngiAgent                  QAForge AI
  - evidence RAG             - requirement-to-test mapping
  - tool routing             - test case generation
  - session memory           - edge-case discovery
  - 8D draft support         - QA artifact validation
```

## Implemented Now

`IssueSense ML` is implemented as the first module.

It is intentionally not positioned as a final enterprise app. It is an AI triage engine that produces structured signals for deeper engineering workflows.

## Planned Next Modules

### EngiAgent

Agentic workflow layer for engineering problem solving and 8D assistance.

### QAForge AI

AI-assisted QA validation layer for requirement-to-test coverage.

## Why This Positioning Matters

Bosch-style AI engineering work is rarely just a chatbot or a single classifier. The useful system is usually a pipeline:

1. collect data,
2. structure the finding,
3. retrieve evidence,
4. evaluate model output,
5. route the result into a human or agent workflow.

This suite structure shows that the portfolio is built around applied engineering workflows, not isolated demos.
