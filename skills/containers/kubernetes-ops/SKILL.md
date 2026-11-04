---
name: kubernetes-ops
description: Deploy and troubleshoot Kubernetes workloads using explicit contexts, scoped permissions, and reviewed manifests or Helm releases. Verify rollout health and plan recovery around persistent data and cluster dependencies.
---

# Kubernetes operations

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for workload deployment, rollout debugging, service/network diagnosis, and Helm release operations.

## Prerequisites

- Compatible `kubectl` and, for chart-managed workloads, the project's existing Helm version.
- Approved cluster credentials and namespace-scoped RBAC; access to reviewed manifests/charts and existing health checks.
- Known-good release/manifests, persistent-data backups, and a maintenance/recovery plan.

## Inputs to gather

- Cluster/context, cloud account/project/subscription where applicable, namespace, workload/release name, environment, and owner.
- Image digest, manifest/chart version, secret references, service/ingress paths, probes, resource requests/limits, and rollout strategy.
- Storage claims, migration jobs/hooks, disruption budgets, expected replicas, and rollback compatibility.

## Steps

1. **Identify the cluster and namespace target first; start read-only.** Set `CTX` and `NS` to reviewed values:

   ```sh
   kubectl config current-context
   kubectl config get-contexts
   kubectl --context "$CTX" get namespace "$NS"
   kubectl --context "$CTX" -n "$NS" auth can-i patch deployments.apps
   kubectl --context "$CTX" -n "$NS" get deployments,pods,services
   ```

   Confirm the API endpoint/cluster mapping through the approved inventory; do not dump raw kubeconfig or credentials. Pass context and namespace on every command rather than changing shared defaults.
2. Inspect non-sensitive manifests and use digest-pinned images, non-root security contexts, disabled privilege escalation, dropped capabilities, appropriate requests/limits, readiness/startup probes, and network policies supported by the cluster's CNI. Scope service-account RBAC and avoid automatic token mounting when unnecessary. Keep secret values outside rendered/shared manifests.
3. **Preview changes before writes**, using the ownership model already in place. For plain non-secret manifests:

   ```sh
   kubectl --context "$CTX" -n "$NS" apply --dry-run=server -f k8s/workload.yaml -o name
   kubectl --context "$CTX" -n "$NS" diff -f k8s/workload.yaml
   ```

   Diff exit 1 means differences, not failure; greater than 1 indicates an error. Diff can expose values: never run it over Secret objects or manifests containing embedded credentials in shared output. Server dry-run does not persist objects, but contacts admission webhooks and is not an end-to-end rollout test.
4. For Helm-managed resources, inspect existing release metadata and use the exact chart/version and approved secret-free values:

   ```sh
   helm list --filter '^app$' --kube-context "$CTX" --namespace "$NS"
   helm upgrade app ./chart --kube-context "$CTX" --namespace "$NS" \
     --values values.dev.yaml --dry-run=server --hide-secret
   ```

   This preview requires a Helm version supporting these flags; check `helm upgrade --help` first. Otherwise use supported client dry-run in a protected environment, noting that it cannot validate live cluster behavior. `--hide-secret` hides Secret objects, not secrets embedded in other objects or notes. Do not render secret-bearing values into shared logs, use `--debug`, or put secrets in `--set`. Review hooks, migrations, deletions, and PVC changes.
5. **Obtain explicit user confirmation before any destructive or production-affecting action**, including deployment, restart, scaling, Helm hooks, or changes to cluster-wide resources. After approval, apply the reviewed non-secret manifest or upgrade the reviewed Helm release with appropriate `--wait --timeout 5m`. Do not mix direct edits with Helm ownership or use force replacement to bypass immutable-field errors.

   Choose only the command matching the existing ownership model:

   ```sh
   kubectl --context "$CTX" -n "$NS" apply -f k8s/workload.yaml
   # Alternative for the existing Helm release:
   helm upgrade app ./chart --kube-context "$CTX" --namespace "$NS" \
     --values values.dev.yaml --wait --timeout 5m
   ```

## Verification

- For a Deployment, run `kubectl --context "$CTX" -n "$NS" rollout status deployment/app --timeout=180s`; check replicas, readiness, service endpoints, and real application health.
- Inspect scoped events and selected pod status fields. For debugging, fetch only necessary container logs in a protected channel after considering secret exposure; redact before sharing. Do not dump pod environment, Secrets, or full chart values.
- Check probe failures, scheduling/resource constraints, image pulls, DNS/network policy, and ingress routing. `exec` and debug containers can affect production: obtain explicit confirmation before production use.

## Rollback

For compatible stateless changes, preview the known-good manifest or inspect available Helm/Deployment revisions, then obtain confirmation for destructive or production-affecting recovery. Use a reviewed `helm rollback` or Deployment rollback scoped to context and namespace; verify rollout and health again. Deployment rollback does not revert Services or ConfigMaps; Helm rollback may run hooks and does not restore persistent data or undo CRD/schema changes. Restore stateful services through tested backup/cutover procedures. Never delete PVCs or namespaces as default recovery.

## Safety notes

- Never print, log, or commit secrets; avoid raw kubeconfig, `get secret -o yaml`, unredacted logs, and debug output.
- Always start read-only/dry-run. Dry-run cannot prove capacity, application correctness, or migration safety.
- Treat drains, CRD updates, RBAC/network changes, and namespace deletion as high-impact operations requiring explicit confirmation when destructive or production-affecting.
