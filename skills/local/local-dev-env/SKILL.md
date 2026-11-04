---
name: local-dev-env
description: Set up and troubleshoot reproducible local development with Compose and optional kind or minikube clusters. Covers Linux, macOS, Windows, and WSL2 while keeping local work separate from production targets.
---

# Local development environment

## When to use

Start a project's existing local stack, diagnose container networking or file-sharing issues, or validate Kubernetes manifests on an isolated local cluster.

## Prerequisites

- The project's documented runtime and existing Compose/container or Kubernetes tooling.
- Sufficient CPU, RAM, disk, virtualization support, and permission to use the container runtime.
- Identify the checkout, container daemon/context, cloud account if used, Kubernetes context/cluster, and host target first. A local shell can still point at a remote production daemon.

## Inputs to gather

- OS and architecture, runtime versions, service ports, local volumes, health checks, and dependency lockfiles.
- Whether Kubernetes is needed; choose the project's existing kind or minikube path rather than running both.
- Approved secret injection method, development data requirements, and whether any services contact production.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Begin read-only or with a supported dry run.** Inspect project instructions and manifests before starting anything:

   ```sh
   git status --short
   docker context show
   docker compose version
   docker compose config --quiet
   docker compose ps
   kubectl config current-context
   ```

   Run Kubernetes commands only if Kubernetes is in use. `config --quiet` validates Compose without rendering interpolated secrets; do not publish rendered configuration.
2. Check platform prerequisites:
   - **Linux:** confirm runtime service health and bind-mount ownership. Docker socket access is effectively root access; do not add users to its group casually.
   - **macOS:** confirm the runtime VM has resources and project directories are shared; check ARM64 versus AMD64 image support before enabling emulation.
   - **Windows:** use the project's supported PowerShell or WSL2 workflow, not a mixture of path syntaxes. Confirm virtualization and runtime integration.
   - **WSL2:** check `wsl --status` from Windows, runtime integration for the chosen distribution, Linux-side file permissions, line endings, and port forwarding. Prefer the Linux filesystem for Linux-heavy builds.
3. Use a local-only, ignored environment file or approved secret provider. Check ignore behavior without displaying its contents: `git check-ignore .env`. Do not copy production secrets or datasets into development.
4. Resolve port conflicts and constrain published services to loopback where possible. Review mounts and startup scripts: `compose up` can execute migrations and contact remote services.
5. Obtain explicit user confirmation before any destructive or production-affecting action, including volume deletion, database resets, runtime/context changes affecting shared workloads, or contacting a production endpoint.
6. For the reviewed local Compose target, use the project's documented profile; a typical startup is `docker compose up -d`. This is a real mutation, not a dry run. Use `docker compose ps` and service-specific health checks afterward.
7. If Kubernetes is required, create a clearly named isolated cluster using one existing tool:

   ```sh
   kind create cluster --name dev-sandbox
   # Alternative, not an additional required cluster:
   minikube start -p dev-sandbox
   ```

   Review resource use first. Verify the resulting context and use explicit `--context` on subsequent commands. For reviewed manifests, run `kubectl --context kind-dev-sandbox diff -f k8s/` if that path/context exists. Diff may contact admission webhooks and reveal Secret values; exclude Secret manifests and keep output private.
8. Run the repository's existing dependency installation and smoke-test instructions; do not introduce new tools or dependencies just to bootstrap.

## Verification

- Confirm container/Kubernetes context remains local; verify ports, service health, and a representative application request.
- For kind, inspect `kubectl --context kind-dev-sandbox get pods -A`; for minikube, use the verified profile's actual context.
- Confirm hot reload, volume ownership, DNS between services, and expected architecture.
- Check `git status --short` and ensure secrets, generated credentials, and local data are not staged.

## Rollback

- Stop the reviewed Compose project with `docker compose stop`; `docker compose down` removes its containers/networks but normally preserves named volumes. Review external resources and scripts separately.
- Preserve databases with the project's tested backup method before resets. Never use `down -v`, volume pruning, or cluster deletion without explicit confirmation and a data-retention decision.
- Remove only the confirmed local cluster when appropriate, for example `kind delete cluster --name dev-sandbox` or `minikube delete -p dev-sandbox`. Cluster-local data can be lost permanently.
- Restore the previous context and configuration; deleting containers does not undo remote calls or migrations.

## Safety notes

- Never print, log, or commit secrets. Avoid `docker inspect`, rendered Compose output, or Kubernetes Secret output when collecting diagnostics.
- There is no universal safe dry-run for startup scripts. Inspect them and their endpoint configuration first.
- Do not use broad prune/reset commands on a shared daemon or disable TLS verification to make connectivity work.
