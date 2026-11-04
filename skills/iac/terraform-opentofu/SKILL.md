---
name: terraform-opentofu
description: Build and operate Terraform or OpenTofu infrastructure using reviewed modules, protected remote state, and saved plans. Detect drift and manage changes without treating state edits or destruction as routine recovery.
---

# Terraform and OpenTofu

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for infrastructure modules, provider upgrades, remote-state setup, drift analysis, and planned provisioning.

## Prerequisites

- The repository's supported Terraform or OpenTofu version and provider lockfile; choose one engine for the workflow rather than alternating untested versions.
- Approved short-lived provider credentials and access to an existing protected backend.
- Reviewed modules, existing validation commands, and a backup/recovery procedure.

## Inputs to gather

- Engine/version, root module directory, workspace, backend account/bucket/container/key, cloud account/project/subscription, region, and environment.
- Module/provider versions, secret-input mechanism, expected changes, budget, maintenance window, and state ownership.
- Locking support, state versioning, encryption/access controls, resource dependencies, and data recovery objectives.

## Steps

1. **Identify the cloud account and state target first; start read-only.** Inspect backend and provider configuration, then verify the effective provider principal with the appropriate cloud CLI identity command. Check workspace mappings and deployment-specific provider aliases; local CLI identity alone does not prove provider identity. Do not initialize against an ambiguous backend.
2. Select the existing engine (examples use Terraform; use `tofu` consistently for an OpenTofu project):

   ```sh
   terraform version
   terraform fmt -check
   terraform init -input=false -lockfile=readonly
   terraform workspace show
   terraform validate
   ```

   Initialization downloads the already-declared providers/modules and connects to the backend; inspect those sources first. Do not automatically accept migration or reconfiguration prompts. Backend creation or state migration is a separate reviewed change, with explicit confirmation if destructive or production-affecting.
3. Use encrypted, access-controlled remote state with supported locking and recovery/versioning. Never share credentials via backend configuration arguments or checked-in files. Keep state, plans, credentials, and secret variable files out of version control. Pin module releases/commits and provider constraints; preserve the lockfile. Design modules around coherent ownership boundaries with typed inputs, validated constraints, and minimal outputs.
4. **Generate a dry-run plan before applying:**

   ```sh
   terraform plan -input=false -out=reviewed.tfplan
   terraform show -no-color reviewed.tfplan
   ```

   Run in an approved protected workspace: saved plans and rendered output can contain secrets even when some values are marked sensitive. Prefer secret references over plaintext inputs and audit sensitivity handling before planning. If the plan could reveal secret values, do not render it; use the approved secret-safe review workflow. Do not send plan/state output to shared logs. Review account, workspace, backend key, deletions, replacements, IAM, networking, costs, and unexpected drift. Avoid routine `-target`, `-lock=false`, and `-refresh=false`; they weaken review or concurrency protections.
5. **Obtain explicit user confirmation before destructive or production-affecting actions.** Bind approval to the plan, target, costs, and recovery strategy, then:

   ```sh
   terraform apply reviewed.tfplan
   ```

   Applying a saved plan does not prompt for approval. Regenerate and reapprove if configuration, variables, provider versions, state, or live conditions changed.

## Verification

- Check resource health and application behavior with read-only service-specific commands.
- Run `terraform plan -input=false -detailed-exitcode` in the protected workspace: exit 0 means no diff, 2 means changes remain, and 1 means an error.
- Investigate differences rather than repeatedly applying. Confirm expected access restrictions, costs, and retained data; clean up sensitive plan artifacts using the approved retention policy.

## Rollback

Revert configuration, not state, and create a fresh reviewed plan. Obtain confirmation for destructive or production-affecting recovery. A previous configuration may replace resources or fail after schema/provider changes; persistent data needs tested backup/restore and cutover procedures. State restoration is an expert recovery action requiring exclusive access and reconciliation with real resources, not infrastructure rollback. Never blindly use `state rm`, `state push`, force-unlock, or destroy.

## Safety notes

- Never print, log, or commit secrets. Avoid `terraform show -json`, full state dumps, `output -raw` on secrets, shell tracing, and debug logs in shared channels.
- Sensitive markings hide some display values but do not remove secrets from state or plans.
- Import, backend migration, unlocks, and destroy require a separate scoped review; production-affecting or destructive operations always require explicit user confirmation.
