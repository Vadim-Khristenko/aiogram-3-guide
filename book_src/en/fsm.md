---
title: Finite State Machines
description: Building dialog flows with FSM in aiogram
---

# Finite State Machines {: id="fsm" }

!!! info ""
    aiogram version used: 3.7.0  
    Tested with aiogram: 3.27.0 | 24.04.2026

This chapter introduces FSM as a robust way to design multi-step dialogs.

## Theory {: id="theory" }

FSM (Finite State Machine) helps model user interaction as explicit states and transitions.

Key principles:

- each step is represented by a state;
- handlers are scoped by state;
- transitions are explicit and predictable;
- state storage strategy must match deployment requirements.

Typical choices:

- in-memory storage for local/testing usage;
- Redis/DB-backed storage for production and horizontal scaling.

## Practice {: id="practice" }

A standard flow for aiogram FSM:

1. Define state groups and state fields.
2. Enter a starting state on command.
3. Validate input on every state step.
4. Save intermediate data in FSM context.
5. Move to the next state or finish/reset.
6. Handle cancellation globally.

Production checklist:

- always provide a cancel path;
- validate and sanitize all user input;
- keep state transitions idempotent where possible;
- clear state on completion and on critical errors.

## Code and Further Reading

- Russian chapter source: `/fsm/`
- Example code base: `code/ru/07_fsm/`
