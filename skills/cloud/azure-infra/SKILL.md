---
name: azure-infra
description: Plan and provision Azure resources with scoped identities, private connectivity, and cost-aware resource groups. Use deployment previews and health checks to control infrastructure changes.
---

# Azure infrastructure

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for Azure resource provisioning, Bicep deployments, managed identity/RBAC design, and network operations.

## Prerequisites

- Azure CLI and the project's existing Bicep tooling, with approved federated or interactive authentication.
- Read access to the subscription and resource group; deployment access scoped to the required resources.
- A reviewed template, approved region, budget, and data-recovery requirements.

## Inputs to gather

- Tenant ID, subscription ID, resource group, location, environment, deployment name, and owner.
- Resource SKUs, availability requirements, CIDRs, private endpoints, DNS, permitted traffic, and identity assignments.
- Expected costs, policy restrictions, existing dependencies, retention, and backup objectives.

## Steps

1. **Identify the cloud account target first; begin read-only.**

   ```sh
   az account show --query '{tenant:tenantId,subscription:id,name:name}' -o table
   az group show --subscription "$SUBSCRIPTION_ID" --name "$RESOURCE_GROUP" \
     --query '{name:name,location:location,id:id}' -o table
   ```

   Set `SUBSCRIPTION_ID` and `RESOURCE_GROUP` to approved values before use. Verify the tenant and subscription; pass the subscription explicitly on subsequent commands. For a new group, inspect subscription policies and planned location first; group creation is a separate approved write.
2. Scope RBAC at the smallest practical resource scope; prefer managed identities and custom or narrow built-in roles over Owner. Avoid long-lived service-principal secrets. Plan private endpoints, DNS resolution, NSGs with only necessary flows, and restricted public access. Estimate compute, disks, egress, and gateway costs; include tags, budgets, and alerts.
3. Preview a resource-group deployment without provisioning resources:

   ```sh
   az deployment group validate --subscription "$SUBSCRIPTION_ID" \
     --resource-group "$RESOURCE_GROUP" --template-file main.bicep \
     --parameters @parameters.json --query 'properties.provisioningState' -o tsv
   az deployment group what-if --subscription "$SUBSCRIPTION_ID" \
     --resource-group "$RESOURCE_GROUP" --template-file main.bicep \
     --parameters @parameters.json --result-format ResourceIdOnly
   ```

   Keep parameter files secret-free, use Key Vault references where supported, and treat diagnostics as sensitive. Resolve policy errors and investigate deletions/replacements; what-if can be incomplete for runtime-resolved values.
4. **Obtain explicit user confirmation before destructive or production-affecting actions**, including group creation, RBAC/network updates, or deployments affecting production. Confirm scope, preview, cost, recovery plan, and downtime, then deploy:

   ```sh
   az deployment group create --subscription "$SUBSCRIPTION_ID" \
     --resource-group "$RESOURCE_GROUP" --name reviewed-change \
     --template-file main.bicep --parameters @parameters.json \
     --query 'properties.provisioningState' -o tsv
   ```

   Prefer incremental deployments; do not switch to complete mode to remove unexpected resources.

## Verification

- Check deployment provisioning state and specific resource health without dumping outputs or credentials.
- Test application health, private DNS resolution, intended allowed/denied network paths, managed identity access, encryption, tags, and budget alerts.
- Inspect relevant Azure Monitor metrics and compare actual resource SKUs with the reviewed plan.

## Rollback

Re-preview and redeploy a known-good template only after reviewing live drift and obtaining confirmation for destructive or production-affecting changes. Incremental deployment does not automatically remove newly added resources or restore deleted data. For stateful services, use tested backups and a separately reviewed restore/cutover plan. Do not delete the resource group as a general rollback technique; it can contain shared infrastructure and retained data.

## Safety notes

- Never print, log, or commit secrets. Avoid `az account get-access-token`, storage-key listing, secret-value reads, shell tracing, and debug logs in shared diagnostics.
- Start read-only and use supported `what-if`/validation, not invented universal dry-run flags.
- RBAC changes may propagate slowly; do not widen permissions to work around transient authorization errors. Cost budgets alert rather than enforce a hard limit.
