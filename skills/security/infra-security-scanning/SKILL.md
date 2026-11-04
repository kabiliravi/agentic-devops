---
name: infra-security-scanning
description: Assess container images and infrastructure configuration using existing Trivy, Checkov, or tfsec workflows. Use to triage actionable findings, enforce reviewable CI gates, and verify remediation without changing live infrastructure during scanning.
---

# Infrastructure security scanning

## When to use

Review IaC or container risks, investigate a CI security-gate failure, or validate a focused infrastructure security fix.

## Prerequisites

- Authorized source/image access and at least one of the project's existing scanners; do not add dependencies during this workflow.
- Known scanner version, existing policy/configuration, approved advisory-database access, and a private report destination.
- Identify the cloud account, Kubernetes cluster/context, host, environment, repository revision, and image registry/digest relevant to the assessment first. Local scanning must not be mistaken for permission to inspect or alter production.

## Inputs to gather

- Scope: Terraform, Kubernetes, Helm, container image, or filesystem; exact paths and immutable revisions/digests.
- Required severity threshold, exploitability criteria, accepted exceptions, and remediation owners.
- Whether network egress, registry authentication, code upload, or sensitive report retention is allowed.
- Existing baseline findings, deployment plan, and known-good configuration/image.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Begin read-only or with a supported dry run.** Inspect scanner configuration, ignore files, local target files, and existing reports. Use local analysis before any live-cluster/cloud scan. Scanners may write caches/reports and download advisory data; confirm these side effects and egress policy.
2. Choose only the existing scanner(s) relevant to the target. Consult their installed `--help` for supported flags and configuration precedence. Do not execute arbitrary repository hooks or third-party modules while merely collecting findings.
3. For **Trivy**, examples using a reviewed `infra/` directory and an approved public image are:

   ```sh
   trivy config --severity HIGH,CRITICAL --exit-code 1 infra/
   trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 registry.example.com/team/app@sha256:REPLACE_WITH_VERIFIED_DIGEST
   ```

   The image reference is a template, not an executable valid digest: substitute the approved digest first. Use an existing credential helper for private registries; never put tokens in arguments. Confirm the scanner uses the intended image source and current advisory data.
4. For **Checkov**, a local Terraform check can use:

   ```sh
   checkov -d infra/ --framework terraform --compact
   ```

   Review config/environment settings so the invocation does not upload source or findings to an unapproved remote service. External module downloads and remote integrations require explicit policy review; local output may still contain sensitive resource details.
5. For an existing **tfsec** workflow:

   ```sh
   tfsec infra/ --minimum-severity HIGH
   ```

   Interpret results with the installed version and ruleset. Where the project already uses Trivy's configuration scanner, avoid introducing a second gate solely to duplicate tfsec coverage.
6. Keep output local and private. Misconfiguration snippets or secret findings can reveal credentials; never paste raw reports into logs, PRs, or tickets. Prefer sanitized rule IDs, locations, severity, and remediation summaries; do not scan secret-bearing files into public CI output.
7. Triage each relevant finding against reachability, actual deployed settings, compensating controls, and fixed versions. Treat an exit code as a gate result, not a diagnosis: distinguish tool/database/network failures from policy failures. Exceptions need a narrow rule/resource scope, owner, justification, and expiry.
8. Propose surgical fixes such as restricted ingress, encryption, workload permissions, or a reviewed image digest. Require explicit user confirmation before destructive or production-affecting actions, including deployment, credential changes, live scans with operational impact, and weakening production security gates.
9. Run existing tests and the same targeted scan again. For IaC deployment review, inspect the existing tool's plan, not an invented scanner `--dry-run`. Terraform plans/state can contain secrets; use the project's protected plan workflow and never share raw plan output.

## Verification

- Verify scanner version, rules/configuration, advisory-database freshness, target revision/digest, and exit status.
- Confirm the targeted finding is fixed rather than hidden by a broad exclusion; check that required CI jobs still run and fail on policy violations.
- Re-run existing IaC/application tests and review the deployment plan for unintended resource replacement or broader access.
- After separately approved deployment, verify the actual target configuration and application health using read-only checks. Passing static scans does not prove an environment is secure.

## Rollback

- Revert the focused configuration/image change through review and restore the known-good immutable revision after required production confirmation.
- Assess whether reverting reintroduces a vulnerability; use an approved temporary compensating control instead where appropriate.
- Remove only newly introduced exceptions that are no longer needed, preserving audit history.
- Scanner runs do not undo live infrastructure changes. Resource destruction, key deletion, or data loss requires the deployment's tested recovery plan and may not be reversible.

## Safety notes

- Never print, log, or commit secrets, registry credentials, raw secret findings, or secret-bearing Terraform plans/state.
- Do not claim universal dry-run support or auto-fix live infrastructure based solely on a scanner finding.
- Use least-privilege read-only identities for authorized remote assessment; never broaden access simply to make a scan pass.
