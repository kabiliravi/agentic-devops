---
name: aws-infra
description: Provision and operate AWS infrastructure with scoped IAM, private networking, and cost controls. Inspect account identity and change plans before making approved changes.
---

# AWS infrastructure

All commands below are illustrative and unverified; adapt them to the approved target before use.

## When to use

Use for AWS provisioning, IAM policy changes, network design, and troubleshooting existing resources.

## Prerequisites

- AWS CLI v2 and an approved SSO session or short-lived role; use the existing infrastructure-as-code workflow when available.
- Permission to inspect the intended account and region, plus narrowly scoped deployment permissions.
- A reviewed CloudFormation template, ownership tags, budget, and recovery requirements.

## Inputs to gather

- Account ID, CLI profile, region, environment, stack name, owner, and change window.
- Required services, availability zones, CIDRs, allowed traffic, encryption keys, data retention, and estimated monthly cost.
- Existing resources, service quotas, dependencies, and backup/recovery objectives.

## Steps

1. **Identify the cloud account target first; start read-only.** Set reviewed values and confirm the account ID against the request:

   ```sh
   export AWS_PROFILE=team-dev AWS_REGION=us-east-1
   aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output table
   aws configure get region
   aws cloudformation describe-stacks --stack-name app-dev \
     --query 'Stacks[].{Name:StackName,Status:StackStatus}' --output table
   ```

   A missing stack is expected for a new deployment; distinguish that from access or region errors. Do not dump stack outputs or parameter values.

2. Design least privilege: scope IAM actions and resource ARNs, separate deployment and runtime roles, use workload roles instead of embedded access keys, and review trust policies. Avoid wildcard administrators. Use private subnets for workloads, narrowly scoped security groups, private service endpoints where appropriate, and no public management ports. Price NAT gateways, load balancers, storage, and data transfer; apply owner/environment tags and budget alerts.
3. Validate locally checked templates and inspect a change set before execution:

   ```sh
   aws cloudformation validate-template --template-body file://infra.yaml \
     --query 'Description' --output text
   aws cloudformation create-change-set --stack-name app-dev \
     --change-set-name reviewed-change --change-set-type UPDATE \
     --template-body file://infra.yaml
   aws cloudformation wait change-set-create-complete \
     --stack-name app-dev --change-set-name reviewed-change
   aws cloudformation describe-change-set --stack-name app-dev \
     --change-set-name reviewed-change --query 'Changes[].ResourceChange' --output json
   ```

   Use `CREATE` instead of `UPDATE` for a new stack. Creating a change set writes control-plane metadata but does not execute resource changes. Supply IAM capabilities only after reviewing the corresponding permissions. Use an approved secret manager reference, not plaintext parameters; keep templates and change-set output free of secrets.
4. Review replacements, deletions, ingress, IAM, downtime, and costs. **Obtain explicit user confirmation before any destructive or production-affecting action**, including production IAM/network changes or control-plane preparation that affects production. Do not execute merely because validation passed:

   ```sh
   aws cloudformation execute-change-set --stack-name app-dev --change-set-name reviewed-change
   ```

## Verification

- Inspect stack status and narrowly selected resource statuses; use `stack-create-complete` or `stack-update-complete` waiters as appropriate.
- Run application health checks from the expected network; verify denied public access, workload IAM permissions, encryption, tags, and budget coverage.
- Check service metrics and billing estimates after deployment. Record resource IDs and the approved change, not sensitive outputs.

## Rollback

Before execution, discard an unneeded change set. After execution, inspect CloudFormation events and rollback state; stop further changes if recovery is uncertain. Re-plan the previous template and obtain confirmation for destructive or production-affecting recovery. Replacement databases, deleted storage, and external side effects may not be recoverable through stack rollback: use tested backups and a reviewed restore/cutover procedure. Never blindly delete a failed stack or skip rollback resources.

## Safety notes

- Never print, log, or commit secrets; do not use shell tracing, credential dumps, or CLI debug output. Redact diagnostics before sharing.
- There is no universal AWS dry-run flag. Start with read-only inspection and supported service-specific validation/change sets.
- Budget alerts are not spending caps. Do not delete shared networking, persistent data, or IAM roles without dependency and retention review.
