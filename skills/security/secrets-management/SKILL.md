---
name: secrets-management
description: Manage secret storage, delivery, and rotation with Vault, SOPS, and cloud secret managers. Use to replace plaintext credentials with scoped identities, encrypted configuration, and verifiable rotation procedures.
---

# Secrets management

## When to use

Migrate plaintext credentials, design application secret delivery, rotate a credential, or investigate secret-access failures.

## Prerequisites

- Authorized access to an existing Vault, SOPS key infrastructure, or cloud secret manager.
- Approved workload identity, audit logging, recovery ownership, and a private operator environment.
- Identify the cloud account/project/subscription, Vault namespace/cluster or secret-manager region, application cluster/host, and environment first. Verify identity using read-only metadata, not by displaying secret values.

## Inputs to gather

- Secret owner, consuming workloads, current delivery mechanism, rotation interval, and expiry.
- Required read/write paths, encryption key ownership, audit requirements, and emergency access procedure.
- Whether the backend supports multiple active credentials, versioning, dynamic leases, and delayed deletion.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start with read-only metadata inspection or a supported dry run.** Inspect access policy, version metadata, key recipients, and consumer identity. Do not retrieve values just to prove access. With an already approved Vault session and the correct mount/path, `vault kv metadata get -mount=secret app/config` inspects KV v2 metadata rather than secret values; adapt the mount and path to the inventory.
2. Classify data and define minimal read paths per workload. Separate production/non-production identities and encryption keys. Prefer short-lived workload federation over human access keys or shared application credentials.
3. For **Vault**, use the existing Kubernetes/JWT/cloud auth method with tightly bound audience, role, namespace, and service-account claims. Prefer dynamic database credentials when supported; set lease TTLs and confirm consumers renew or refresh. Restrict policies to required capabilities and review audit-device redaction settings.
4. For **SOPS**, review `.sops.yaml` creation rules and recipients/KMS keys against environment ownership. Use `sops edit` with an approved editor that does not persist plaintext swap, backups, or telemetry. Keep decrypted material out of Git, logs, shell history, and shared storage. Encryption metadata and key paths may still reveal sensitive infrastructure details.
5. For **cloud secret managers**, use the provider's native SDK/CSI/agent with a scoped workload identity. Verify the exact account, region, resource, and version/alias. Enforce least privilege for read, rotation, and deletion separately; review cross-account access and KMS permissions.
6. Plan rotation as create new credential → deliver new version → refresh consumers → verify health → revoke old credential. Confirm whether overlapping credentials are supported; otherwise arrange an approved outage or compatible cutover.
7. Obtain explicit user confirmation before destructive or production-affecting actions, including rotation, revocation, key-recipient changes, access-policy edits, secret/version deletion, and consumer restarts. Explain who loses access and the recovery window before executing.
8. Use an approved secret-management UI or SDK to transfer values directly into the backend without printing them or putting plaintext in CLI arguments. Use existing secure input mechanisms and disable shell tracing. Do not paste credentials into chat or tickets.
9. Test delivery and rotation in non-production first. Use an application-level authenticated operation that returns only a pass/fail result and non-sensitive version metadata. Redact error messages that may echo connection strings.

## Verification

- Confirm authorized consumers authenticate using their own identities and can perform the intended operation without displaying the credential.
- Confirm an unauthorized identity is denied through a controlled non-production access test; review audit metadata for the expected principal/path.
- Verify workloads refresh before lease expiry and no plaintext appears in repository changes, artifacts, deployment output, or logs.
- After rotation, verify all consumers use the new version before revoking the old one; then confirm the old credential no longer authenticates.

## Rollback

- Before revocation, an approved version/alias rollback may restore the previous still-valid credential. Require explicit confirmation for production changes.
- After revocation or expiry, issue a replacement credential; do not assume restoring secret-manager text reactivates the upstream credential.
- For SOPS recipient changes, retain an authorized recovery recipient and tested key recovery path. Restore the encrypted revision only if its keys remain available and approved.
- Deleted secrets or destroyed encryption keys may be unrecoverable after provider recovery windows. Git history of ciphertext is not a substitute for key recovery.

## Safety notes

- Never print, log, or commit secrets. Only policy-approved encrypted SOPS artifacts may be committed; plaintext, private keys, tokens, and recovery material must never be committed.
- Avoid `vault kv get`, `sops decrypt` to stdout, environment dumps, and secret-reading CLI examples in diagnostics.
- No universal secret-rotation dry run exists. Inspect metadata/policy first and use non-production lifecycle tests.
- If a secret was exposed, rotate/revoke it and follow incident procedures; deleting a file or rewriting history alone does not invalidate it.
