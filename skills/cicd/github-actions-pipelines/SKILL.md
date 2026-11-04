---
name: github-actions-pipelines
description: Build and troubleshoot GitHub Actions pipelines with least-privilege permissions, immutable dependencies, and short-lived deployment credentials. Use for pull-request checks, artifact promotion, and gated deployments.
---

# GitHub Actions pipelines

## When to use

Create or repair repository workflows, improve build isolation, or replace long-lived cloud credentials with OIDC.

## Prerequisites

- Repository access, Git, and an existing project build/test command; use the repository's existing tooling.
- For deployment: an approved GitHub Environment, a cloud-side OIDC trust relationship, and an authorized operator.
- Identify the repository, workflow/ref, environment, cloud account/project/subscription, region, and cluster/host target first. Verify the destination using a read-only cloud identity/context query appropriate to the provider.

## Inputs to gather

- Trigger events, supported runtimes, dependency lockfiles, required status checks, and runner architecture.
- Artifact retention, deployment destination, approval owners, health checks, and known-good release identifier.
- Which external contributions can run workflows, and which steps actually need repository or cloud write access.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start read-only or with a real dry run.** Inspect existing workflow YAML, branch protections, environment gates, and recent failed-run logs. Do not execute untrusted workflow code with credentials. Logs can contain sensitive data: inspect locally and redact before sharing.
2. Plan separate validation, build, and deployment jobs. Use `pull_request` for untrusted checks without deployment secrets; never combine `pull_request_target` credentials with checkout/execution of a contributor's code.
3. Default workflow permissions to `contents: read`; grant additional permissions only on the job that needs them. Use a protected Environment for production and require explicit user confirmation before any production-affecting action or destructive action, including workflow dispatches and credential-policy changes.
4. Pin external actions to reviewed full commit SHAs and container images to digests. Retain readable version comments and update pins deliberately. Install project dependencies from committed lockfiles, for example `npm ci` for an existing npm project; do not introduce dependencies as part of diagnosis.
5. Give only the deployment job `id-token: write` and the minimum other permissions. Configure cloud trust for the exact issuer, audience, repository, and approved branch or Environment subject. OIDC removes stored access keys, not the need for restrictive cloud roles.
6. Pass untrusted event fields through environment variables rather than interpolating them into shell scripts. Use quoted variables and avoid `eval`. Never enable shell tracing around credentials.
7. Build once, identify the artifact by digest, and promote that artifact through environments. Avoid sharing privileged caches with untrusted jobs; do not place credentials in cache paths or artifacts.
8. Use a concurrency group scoped to the deployment target. Avoid canceling an in-progress migration; choose cancellation behavior based on application safety. Put timeouts on jobs.
9. Run the existing tests locally first. Review the diff, then run non-production CI with approved credentials only where required. Apply production deployment only after explicit user confirmation and required Environment approval.

## Verification

- Confirm PR checks execute without write tokens or deployment secrets, including fork behavior.
- Inspect the effective job permissions and verify cloud audit events show the expected federated identity and target.
- Confirm locked dependency installation, expected artifact digest, and required checks pass.
- Check deployment rollout, application health endpoint, error rate, and environment-specific smoke tests. Ensure logs and artifacts contain no credentials.

## Rollback

- Disable or revert the faulty workflow change through the normal review process; cancel only jobs whose interruption is safe.
- After explicit confirmation for production changes, redeploy the recorded known-good immutable artifact.
- Review database compatibility before reverting an application. Restore data only from a tested backup plan; destructive migrations and lost data are not automatically reversible.
- Revoke unexpected cloud sessions where supported and tighten OIDC trust if an unintended identity was accepted.

## Safety notes

- Never print, log, or commit secrets, OIDC tokens, or credential-bearing configuration. Masking is a secondary defense, not permission to emit secrets.
- No universal workflow deployment dry-run exists. Use read-only inspection, project-specific plan modes, and isolated non-production validation instead.
- Treat third-party actions and self-hosted runners as code execution boundaries. Isolate runners from production credentials and avoid persistent shared runners for untrusted PRs.
