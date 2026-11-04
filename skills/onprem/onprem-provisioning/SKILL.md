---
name: onprem-provisioning
description: Plan and provision on-premises bare-metal or virtual infrastructure using reviewed inventory, isolated bootstrap networks, and repeatable configuration. Covers Proxmox, VMware, and PXE workflows with explicit safeguards for storage and shared networks.
---

# On-premises provisioning

## When to use

Prepare physical servers, create approved VMs, or automate OS installation and post-install configuration in a datacenter or lab.

## Prerequisites

- Authorized management access, an approved maintenance window, inventory, and out-of-band console access.
- Existing provisioning tooling, trusted OS images, verified backups, and documented network/storage ownership.
- Identify the cloud account if hybrid, cluster/datacenter, hypervisor or BMC host, hardware serial number, and intended disks first. Confirm identities against inventory, not only IP addresses.

## Inputs to gather

- Bare-metal versus Proxmox versus VMware target; CPU/RAM, firmware mode, Secure Boot requirements, and OS image checksum.
- Management/workload VLANs, IPAM reservations, DNS/NTP, gateway, MTU, DHCP ownership, and PXE scope.
- Disk serials, RAID/HBA mode, datastore/pool, redundancy, backup/restore objectives, and remote-console recovery path.
- VM ID/name, template version, access roles, configuration source, and acceptance checks.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start read-only or with a supported dry run.** Review inventory, current guests, datastore capacity, switch ports, and DHCP/PXE configuration. On the confirmed Linux host, read-only checks include:

   ```sh
   hostnamectl
   ip -brief address
   ip route
   lsblk -o NAME,SIZE,MODEL,SERIAL,TYPE,MOUNTPOINTS
   ```

   On Proxmox, use authorized `pvesh get /cluster/resources` or `qm list`. On VMware, inspect inventory, tasks, and datastore usage in the approved vCenter interface. Do not expose BMC credentials in commands.
2. Produce a reviewed host/VM-to-network-and-disk mapping. Check spare capacity, failure domains, licensing, and whether storage is shared. Confirm backups can be restored before touching existing workloads.
3. Require explicit user confirmation before destructive or production-affecting actions: imaging, disk/RAID changes, guest creation on production clusters, firmware updates, power operations, DHCP changes, and VLAN changes.
4. For **bare metal**, verify serial numbers through BMC and physical inventory, test console access, inspect firmware compatibility, and choose only the approved install disks. Do not execute unattended disk wiping from guessed device names.
5. For **Proxmox**, clone a reviewed cloud-init template into an unused VM ID, set approved CPU/RAM/storage/VLAN settings, and review the resulting hardware configuration before first boot. Do not resize or attach shared disks without confirming ownership.
6. For **VMware**, deploy the approved template through vCenter with the selected cluster, datastore, port group, and customization specification. Confirm unique guest identity and IP allocation before connecting the workload network.
7. For **PXE**, isolate the provisioning VLAN and restrict boot eligibility to approved MAC addresses. Verify signed/trusted boot artifacts and image checksums. Do not introduce a competing DHCP server; coordinate relay and next-server settings with the network owner. Treat unattended-install files as sensitive and remove bootstrap credentials after enrollment.
8. Apply existing configuration management only after checking its target inventory and diff. For Ansible, `ansible-playbook -i inventory site.yml --check --diff --limit approved-host` is useful only when those files exist and tasks support check mode. Diffs can expose secrets: require appropriate `no_log`/diff suppression for sensitive tasks and do not share raw output. Check mode cannot simulate every module.
9. Provision first on an isolated pilot target. After review and required confirmation, apply the same reviewed configuration to the approved targets and record non-sensitive inventory changes.

## Verification

- Confirm host/VM identity, unique addressing, DNS/NTP, VLAN isolation, storage mapping, and console access.
- Verify patch level, SSH access policy, service health, monitoring enrollment, and backup enrollment.
- Test guest reboot and recovery only within the approved window; check application acceptance and capacity on the surrounding cluster.
- Confirm PXE no longer reimages the installed host and bootstrap credentials are revoked.

## Rollback

- Before changes, record original network/firmware/VM settings and verify off-host backups.
- For a failed new guest, disconnect it and remove only its confirmed resources after explicit confirmation; preserve diagnostic data without credentials.
- Restore network or boot settings through the console using the recorded configuration.
- Reimaging, RAID initialization, and disk destruction cannot be undone by reverting automation. Recovery requires tested backups and may still lose data since the last recovery point.
- Hypervisor snapshots are not substitutes for backups and may not cover external disks or application consistency.

## Safety notes

- Never print, log, or commit secrets, BMC passwords, cloud-init credentials, or unattended-install tokens.
- Use scoped management roles and isolated management networks; never place passwords in CLI arguments or URLs.
- No universal provisioning dry-run exists. Read-only inventory and tool-specific previews precede all real changes.
