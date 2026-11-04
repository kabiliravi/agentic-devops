---
name: docker-build
description: Build reproducible multi-stage Docker images with small non-root runtimes and protected build inputs. Inspect build targets, test images locally, and publish only to approved registries.
---

# Docker builds

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for Dockerfile creation, image-size reduction, build troubleshooting, runtime hardening, and controlled image publishing.

## Prerequisites

- Docker with the project's existing BuildKit/buildx support and a reviewed build context.
- Existing application build/test commands, approved base images, and registry authentication through a credential helper or federated workflow.
- A non-production test environment and documented health checks.

## Inputs to gather

- Docker context/daemon, host identity, build context path, Dockerfile, platform, registry/repository, tag, and environment.
- Runtime command, ports, writable paths, UID/GID, health endpoint, dependencies, and resource needs.
- Base-image digests, secret sources, scan policy, rollback digest, and persistent-volume requirements.

## Steps

1. **Identify the host/daemon and deployment target first; begin read-only.**

   ```sh
   docker context show
   docker context inspect --format '{{.Endpoints.docker.Host}}'
   docker version --format '{{.Server.Version}}'
   docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'
   ```

   Confirm the daemon is approved for local testing, not a production remote host. Review Dockerfile instructions, build scripts, and `.dockerignore` before executing them. Docker builds execute arbitrary instructions; there is no universal safe dry-run build flag.
2. Use a multi-stage Dockerfile: install/build dependencies in a builder, then copy only runtime artifacts into a minimal supported runtime. Pin approved base digests, use the project's lockfiles, set a non-root `USER`, prefer exec-form `ENTRYPOINT`/`CMD`, and exclude source-control data, credentials, local caches, and unnecessary tooling. Remove package metadata in the same layer as package installation when applicable.
3. Never use `ARG`, `ENV`, `COPY`, image labels, or command-line literals for secrets. If a build needs credentials, use approved BuildKit secret mounts, ensure commands do not echo or persist them, and do not copy secret-derived files into the runtime. Protect build logs and caches; a mount alone does not prevent a build script leaking credentials.
4. After read-only review, build and test in an approved isolated non-production daemon:

   ```sh
   docker build --pull --target runtime -t app:reviewed .
   docker image inspect app:reviewed --format '{{.Config.User}}'
   docker run --detach --name app-review --read-only \
     --cap-drop=ALL --security-opt=no-new-privileges \
     --memory=256m --cpus=1 --pids-limit=128 \
     --tmpfs /tmp:rw,noexec,nosuid,size=64m \
     -p 127.0.0.1:18080:8080 app:reviewed
   ```

   Use the actual named final stage and application port; omit `--target` if the final stage is unnamed. These limits and writable paths must match application needs. Never mount the Docker socket, host root, or production data. A container-internal temporary filesystem is not a credential store.
5. Run existing tests and the existing image scanner if available. **Obtain explicit user confirmation before destructive or production-affecting actions**, including production-tag publication, deployment, container replacement, or pruning. Publish only the approved image to the explicit repository and record its registry digest; do not rely on mutable `latest` tags.

## Verification

- Probe the documented health endpoint, for example `curl --fail http://127.0.0.1:18080/health`, and run application smoke tests.
- Confirm non-root execution, intended architecture, minimal contents, resource limits, and required writable paths. Inspect only non-sensitive metadata; do not dump image environment variables or raw application logs.
- Verify no credentials entered the context, image layers, logs, or cache using the project's existing checks. Confirm the published digest before rollout.

## Rollback

Redeploy the prior verified digest through the approved deployment workflow, with explicit confirmation if production-affecting or destructive. Image rollback does not revert database migrations, volume writes, queues, or external side effects; use a compatibility and data-recovery plan. Remove only the uniquely identified test container after inspecting it; never run global prune or delete volumes as routine cleanup.

## Safety notes

- Never print, log, or commit secrets; disable shell tracing and do not pass registry passwords as arguments.
- Read-only inspection comes first; local builds/runs still consume resources and execute code.
- Docker daemon access is highly privileged. Avoid `--privileged`, host networking, and broad host mounts.
