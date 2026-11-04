---
name: gcp-infra
description: Provision and operate Google Cloud infrastructure using explicit project targets, least-privilege service accounts, and private networking. Review infrastructure plans, quotas, and cost impacts before approved changes.
---

# Google Cloud infrastructure

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for Google Cloud provisioning, service-account/IAM configuration, VPC changes, and resource troubleshooting.

## Prerequisites

- Google Cloud CLI and approved short-lived authentication; an existing Terraform or OpenTofu workflow for repeatable provisioning.
- Read access to the intended project, and narrowly scoped deployment permissions.
- Existing billing association, reviewed infrastructure configuration, and recovery objectives.

## Inputs to gather

- Organization, project ID and number, authenticated principal, region/zone, environment, owner, and billing scope.
- Services/APIs, quotas, resource sizes, CIDRs, firewall flows, DNS, encryption, and availability requirements.
- Expected costs, labels, dependencies, data retention, and backup/restore procedures.

## Steps

1. **Identify the cloud account/project target first; start read-only.** Set approved project and region values:

   ```sh
   export PROJECT_ID=example-dev REGION=us-central1
   gcloud auth list --filter=status:ACTIVE --format='value(account)'
   gcloud projects describe "$PROJECT_ID" \
     --format='table(projectId,projectNumber,parent.type,parent.id)'
   gcloud compute networks list --project="$PROJECT_ID" --format='table(name,subnetMode)'
   gcloud services list --enabled --project="$PROJECT_ID" --format='value(config.name)'
   ```

   Confirm the active principal and project ancestry match the request. Pass `--project` explicitly; resource-list errors may indicate disabled APIs or insufficient permissions, not absent infrastructure.
2. Prefer workload identity federation or service-account impersonation over downloadable keys. Scope IAM roles to required actions/resources and avoid primitive Owner/Editor roles. Keep workloads private, use explicit subnets and narrow firewall rules, and plan Private Google Access, DNS, and approved egress. Estimate compute, persistent disks, NAT, logging, and cross-region transfer costs; define labels and billing alerts.
3. Use the existing Terraform/OpenTofu project to preview resource creation and IAM/network changes. For example, with Terraform:

   ```sh
   terraform fmt -check
   terraform init -input=false
   terraform validate
   terraform plan -input=false -out=reviewed.tfplan
   terraform show -no-color reviewed.tfplan
   ```

   Inspect configuration/backend targets before initialization and decline unapproved state migration. Ensure provider project, region, and impersonated principal match the read-only inspection; `gcloud` authentication and Terraform provider authentication can differ. Use secret-manager references rather than plaintext secret inputs and audit provider sensitivity handling before rendering a plan. Keep state and plan files access-controlled and out of version control; previews can contain sensitive data. If a preview could reveal secret values, do not render it; use the approved secret-safe review workflow rather than shared logs.
4. Review enabled APIs, resource replacements, IAM grants, public exposure, quota, and cost. **Obtain explicit user confirmation before any destructive or production-affecting action**, including API enablement or billing/IAM changes. Apply only the reviewed, still-current plan:

   ```sh
   terraform apply reviewed.tfplan
   ```

   Do not substitute ad hoc `gcloud` writes for a rejected infrastructure plan.

## Verification

- Re-list the specific resources using explicit project and region/zone flags and non-sensitive field selections.
- Test application health, authorized workload access, blocked unintended ingress, private DNS, encryption, labels, and budget alerts.
- Run another infrastructure plan to detect drift and inspect service metrics for errors. Record IDs and outcomes without sensitive state or application payloads.

## Rollback

Revert configuration to the known-good version and produce a fresh plan; obtain confirmation for destructive or production-affecting recovery before applying. This is not a guaranteed inverse: disks, databases, object retention, and IAM propagation can prevent safe restoration. Use tested backups and reviewed restore/cutover steps for persistent data. Never use project deletion, blanket IAM replacement, or `terraform destroy` as a default rollback.

## Safety notes

- Never print, log, or commit secrets; do not print access tokens, secret versions, service-account keys, or full state. Disable shell tracing.
- Begin read-only or with a supported plan. `gcloud` has no universal dry-run flag; `--quiet` suppresses prompts and is not a preview.
- Budget alerts do not cap spending. Avoid enabling services or weakening organization policy without approval.
