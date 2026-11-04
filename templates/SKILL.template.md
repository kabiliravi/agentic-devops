---
name: example-skill
description: Describe the infrastructure task this skill performs. Use when the user needs this specific outcome.
---

# Example skill

SPDX-License-Identifier: GPL-3.0-or-later

## When to use

Describe the supported environments and use cases, and when not to use this skill.
Copy this file to `skills/<category>/example-skill/SKILL.md` and replace placeholders.

## Prerequisites

List tools, supported versions/platforms, scoped permissions, and recovery access.

## Inputs to gather

- Target environment: cloud account/project/subscription, cluster context and
  namespace, or host/hypervisor and storage identifiers.
- Requested outcome, production status, change window, cost limits, and approvals.
- Current configuration, backup location, and restoration procedure (no secrets).

## Steps

1. Confirm the exact target with read-only identity and inventory commands.
2. Inspect current state and run supported dry-run/check commands first.
3. Explain the proposed change, impact, cost, and recovery limits.
4. Require explicit user confirmation before destructive or production-affecting
   actions; re-confirm if the target or plan changes.
5. Apply only the approved scope. Include practical, platform-specific commands
   here; mark examples illustrative until tested in a disposable lab.

## Verification

Specify read-only health, configuration, and functional checks, expected results,
and conditions for stopping or escalating.

## Rollback

Specify how to restore prior configuration and verify recovery. Identify backup
requirements, irreversible steps, and stateful data that cannot be recovered by
reverting configuration. Rollback mutations need the same approval as deployment.

## Safety notes

- Prefer read-only and dry-run commands first (for example `terraform plan`,
  `kubectl diff`, or Ansible `--check`, where supported).
- Require explicit user confirmation before destructive or production-affecting actions.
- Never print, log, or commit secrets; redact diagnostics and protect artifacts.
- Identify the target environment (cloud account, cluster context, or host) before acting.
- Always provide verification and rollback steps; confirm backups before risky changes.
