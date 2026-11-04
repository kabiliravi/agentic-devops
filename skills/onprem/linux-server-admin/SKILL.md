---
name: linux-server-admin
description: Diagnose and maintain Linux servers through targeted systemd, networking, storage, and package-management operations. Use for incident triage and planned maintenance with explicit access and recovery safeguards.
---

# Linux server administration

## When to use

Investigate unhealthy services, network failures, disk pressure, or patching needs on an authorized Linux server.

## Prerequisites

- Approved SSH/sudo access, distribution-specific runbooks, maintenance authorization, and console access for risky changes.
- Verified backups and application owners for stateful systems.
- Identify the cloud account if applicable, cluster role, host/FQDN, and environment first. Compare host identity and network addresses to inventory before running commands.

## Inputs to gather

- Symptoms, timestamps, recent changes, distribution/version, affected services, and availability requirements.
- Systemd unit name, network manager, filesystem/LVM/RAID layout, package repositories, and reboot constraints.
- Known-good configuration, backup recovery point, redundancy/failover status, and rollback owner.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start with read-only inspection or a genuine supported dry run:**

   ```sh
   hostnamectl
   uptime
   systemctl --failed
   ip -brief address
   ip route
   df -hT
   df -i
   lsblk -f
   ```

   Gather only relevant output. Hostnames, mounts, and logs can be sensitive; redact before sharing.
2. For **systemd**, set `UNIT` to the confirmed service name, then inspect `systemctl status "$UNIT" --no-pager` and `journalctl -u "$UNIT" --since "-30 min" --no-pager`. Review logs locally; services may have logged credentials. Inspect the unit configuration privately if necessary because environment settings can contain secrets. Use the application's own configuration validator before restart.
3. For **networking**, inspect `ss -lnt`, route selection, resolver status, and the active manager (NetworkManager, systemd-networkd, or another approved tool). Diagnose DNS versus routing versus firewall problems separately. Keep console access and a second session before changing SSH, interfaces, routes, or firewall rules.
4. For **storage**, distinguish exhausted blocks from inodes and deleted-but-open files. Use `du -xhd1 /var` only if its I/O cost is acceptable. Identify files by ownership and retention policy; do not delete database files or truncate active logs blindly. Verify disk serials and mount dependencies before storage operations.
5. For **patching**, review configured repositories, pending changes, available disk space, kernel compatibility, and application constraints. Use `apt-get -s upgrade` on Debian-family systems; on supported DNF systems, use `dnf upgrade --assumeno` to inspect the proposed transaction. These previews are not permission to proceed and may need repository access. Do not assume package changes can always be downgraded.
6. Present the exact target, commands, downtime, and recovery plan. Obtain explicit user confirmation before any destructive or production-affecting action, including service restarts, package installation, reboot, network/firewall changes, storage edits, and file removal.
7. Back up affected configuration with the existing secure backup mechanism. Apply one bounded change at a time using the distribution's supported tools. Avoid a combined patch/reboot/storage change that obscures cause and recovery.
8. Reload systemd only when unit definitions changed; restart or reload the service only if approved and supported. Coordinate drain/failover before rebooting cluster members, and respect quorum.

## Verification

- Re-run the relevant read-only checks and verify service readiness, not just process existence.
- Confirm application health, listener availability, DNS/routes, filesystem headroom, and error rates from an independent client.
- After a reboot, verify the expected kernel, required mounts, systemd failures, cluster membership, and scheduled jobs.
- Record changed package/config versions without collecting secrets or full environment dumps.

## Rollback

- Restore known-good service/network configuration and validate syntax before applying it, with explicit confirmation for production impact.
- Recover network access via console if remote connectivity fails; do not repeatedly apply speculative firewall changes.
- Use the previous kernel or distribution-supported package recovery only after compatibility review. Database and package migrations may prevent a safe downgrade.
- Restore lost files/data from tested backups. Filesystem formatting, destructive partition edits, and deletion are not undone by reverting a config file.

## Safety notes

- Never print, log, or commit secrets. Avoid shell tracing, environment dumps, credential-bearing process arguments, and public raw journal output.
- Do not disable SSH authentication safeguards, SELinux/AppArmor, or firewalls as a blanket diagnostic step.
- There is no universal dry run for `systemctl`, network changes, or disk operations. Inspect first and use only documented tool-specific preview modes.
