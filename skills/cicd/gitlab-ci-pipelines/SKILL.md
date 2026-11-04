---
name: gitlab-ci-pipelines
description: Design and troubleshoot GitLab CI pipelines using protected deployment paths, immutable inputs, and scoped OIDC authentication. Use for merge-request validation, reusable jobs, and controlled environment promotion.
---

# GitLab CI pipelines

## When to use

Build or repair `.gitlab-ci.yml`, runner execution, artifact flow, or deployments to cloud and on-premises environments.

## Prerequisites

- Project access and an existing build/test toolchain.
- Access to the project's CI configuration validation UI or API, plus an approved runner.
- Identify the GitLab instance/project, branch, environment, runner executor, and cloud account/cluster/host target first. Verify cloud identity and Kubernetes context using read-only queries before deployment work.

## Inputs to gather

- Pipeline sources, merge-request behavior, default branch, protected refs, deployment approvers, and environment owners.
- Existing job images, lockfiles, included templates, cache policy, artifact retention, and target architecture.
- Cloud OIDC issuer/audience requirements, minimum deployment role, health checks, and rollback artifact.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start with read-only inspection or a supported dry run.** Read the configuration, included templates, runner settings, and relevant job logs. Use GitLab CI Lint to validate expanded configuration; linting is not a deployment simulation and does not prove scripts are safe.
2. Use `workflow: rules` and job `rules` to distinguish merge requests, default-branch builds, schedules, and releases. Check for duplicate branch/MR pipelines and unexpected deployments from tags or schedules.
3. Separate validation, build, and deployment jobs. Use `needs` and explicitly scoped artifacts; do not download all artifacts or cache credential directories by default.
4. Pin container images by digest and cross-project includes to reviewed full commit SHAs. Use existing dependency lockfiles and frozen/locked install commands appropriate to the project.
5. Restrict `CI_JOB_TOKEN` access with project allowlists and minimum supported permissions. Use protected runners/refs and protected Environments for deployment; untrusted merge-request code must not receive production variables.
6. Prefer job `id_tokens` with the provider's expected audience over stored cloud keys. Restrict the cloud trust policy to the exact GitLab issuer, project identity, and protected ref/environment claims supported by that provider. Confirm issuer reachability for self-managed GitLab.
7. Use `resource_group` to serialize deployments to the same target. Require a manual deployment job plus protected-environment approval where available; a manual button alone is not a sufficient authorization boundary.
8. Require explicit user confirmation before destructive or production-affecting actions, including pipeline triggers, production-variable changes, trust-policy edits, and deployment execution. Test first in an isolated non-production environment.
9. Promote an immutable artifact rather than rebuilding during deployment. Capture its digest and release metadata without recording credentials. Avoid privileged Docker-in-Docker or host socket mounts unless reviewed and isolated.

## Verification

- Confirm CI Lint accepts the expanded configuration, then verify the expected jobs for representative MR, branch, tag, and schedule events.
- Run existing tests and confirm artifacts are scoped, immutable, and expire according to policy.
- Verify unprotected/fork pipelines cannot access protected variables, deployment runners, or cloud deployment roles.
- Inspect federated identity audit records, deployment health, rollout status, and application smoke tests at the identified target.

## Rollback

- Revert the CI configuration or include pin through review; stop queued deployments and assess whether interrupting active jobs is safe.
- With explicit confirmation for production, deploy the previous known-good artifact using the same protected path.
- Handle database/schema changes separately using tested backups and compatibility checks. Reverting YAML does not recover deleted data.
- Revoke compromised credentials and repair trust policy if a job obtained unintended access.

## Safety notes

- Never print, log, or commit secrets. Do not use `env`, `printenv`, shell tracing, or verbose HTTP output in credential-bearing jobs.
- Masked variables can still be exfiltrated by malicious scripts; do not expose them to untrusted pipeline code.
- CI Lint and pipeline previews are not universal dry runs. Review scripts and validate in non-production before applying changes.
