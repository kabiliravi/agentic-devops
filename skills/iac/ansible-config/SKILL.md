---
name: ansible-config
description: Apply repeatable host configuration with explicit Ansible inventories, scoped privilege escalation, and check-mode review. Verify idempotence and service health while protecting credentials and planning recovery.
---

# Ansible configuration

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for host configuration, package/service management, application configuration, and controlled rolling changes.

## Prerequisites

- The project's supported Ansible installation and existing roles/collections.
- Approved SSH access, verified host keys, and least-privilege escalation where needed.
- A versioned inventory/playbook, approved secret source, and tested recovery access.

## Inputs to gather

- Inventory path, environment, group/host limit, expected host identities, SSH user, and escalation scope.
- Playbook, role versions, tags, package versions, service health checks, and maintenance window.
- Secret handling, configuration backups, rollout batches, and recovery requirements for persistent data.

## Steps

1. **Identify the host target first; begin read-only.** Verify inventory source and selected hosts before connecting:

   ```sh
   ansible-playbook -i inventories/dev/hosts.yml site.yml --limit app --list-hosts
   ansible-playbook -i inventories/dev/hosts.yml site.yml --limit app --list-tasks
   ansible-playbook -i inventories/dev/hosts.yml site.yml --limit app --syntax-check
   ```

   Check inventory addresses against approved host identities and environment. Dynamic inventories can execute code or contact APIs; review their configuration first. Do not dump all inventory variables, which may contain secrets.
2. Prefer idempotent modules (`package`, `template`, `service`, `user`) to shell commands. For unavoidable commands, define accurate `changed_when`/`failed_when` and safe guards; never label a mutating command unchanged just to pass idempotence checks. Validate templates before replacing live configuration, use handlers for restarts, narrow `become` to necessary tasks, and use `serial` with health gates for rolling deployments.
3. Keep credentials in the approved vault/secret source, not inventory or command-line extra variables. Use `no_log: true` and `diff: false` on secret-bearing tasks; protect controller logs and backups. Never debug secret variables or registered results.
4. **Run check mode before applying:**

   ```sh
   ansible-playbook -i inventories/dev/hosts.yml site.yml --limit app --check
   ```

   Check mode is not a sandbox: some modules cannot predict changes, lookups still execute, and `check_mode: false` tasks can write. Audit those tasks first and exclude or redesign unsafe ones. Use `--diff` only for confirmed non-sensitive files; never enable it globally over secrets. Inspect service restarts, removals, privileges, and unsupported/skipped checks.
5. **Obtain explicit user confirmation before any destructive or production-affecting action**, including restarts and check-mode exceptions that could write to production. Approve an exact inventory/limit and batch; then apply to a canary:

   ```sh
   ansible-playbook -i inventories/dev/hosts.yml site.yml --limit app_canary
   ```

   Confirm `app_canary` resolves to the intended subset of `app`. Verify health before explicitly approved expansion to the remaining hosts; do not casually override limits or rerun only failed tasks without dependency review.

## Verification

- Inspect recap for unreachable/failed hosts and expected changes.
- Run approved read-only service checks on each changed host, including availability and configuration validity.
- Rerun check mode against the same scope: configuration tasks should report no changes unless documented as inherently non-idempotent. Inspect exceptions instead of hiding them.

## Rollback

Restore reviewed previous configuration or run a dedicated recovery playbook first in check mode, then obtain confirmation for destructive or production-affecting recovery. Use protected backups, validate restored configuration, and restart only affected services. Package downgrades and database/schema changes may not be reversible; restore persistent data only through a tested recovery plan. Do not assume rerunning an older playbook undoes all changes.

## Safety notes

- Never print, log, or commit secrets; avoid verbose/debug output, shell tracing, secret diffs, and plaintext vault passwords.
- Never disable SSH host-key checking as a shortcut. Keep broad groups such as `all` out of routine write operations.
- Configuration backups can contain credentials and need encryption, restricted access, and retention controls.
