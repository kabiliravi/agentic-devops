# infra-agent-skills

[![License: GPL v3 or later](https://img.shields.io/badge/License-GPLv3%2B-blue.svg)](LICENSE)

SPDX-License-Identifier: GPL-3.0-or-later

A library of portable [Agent Skills](https://agentskills.io/) for safe DevOps and
infrastructure work. Skills are Markdown instructions, not autonomous deployment
tools: the agent still needs appropriate tools, scoped access, and human approval.

## Environments

- **Public cloud:** AWS, Azure, and Google Cloud accounts and managed services.
- **Local machine/desktop:** Linux, macOS, Windows/WSL2, and disposable dev clusters.
- **On-prem datacenters:** physical servers, hypervisors, networking, and storage.

## Skills

| Name | Category | Purpose |
| --- | --- | --- |
| [aws-infra](skills/cloud/aws-infra/SKILL.md) | cloud | Provision AWS with least-privilege IAM, safe networking, and cost controls. |
| [azure-infra](skills/cloud/azure-infra/SKILL.md) | cloud | Manage Azure resources, RBAC, networks, and budgets. |
| [gcp-infra](skills/cloud/gcp-infra/SKILL.md) | cloud | Manage Google Cloud projects, IAM, networks, and spending. |
| [terraform-opentofu](skills/iac/terraform-opentofu/SKILL.md) | iac | Plan and apply modular infrastructure with protected remote state. |
| [ansible-config](skills/iac/ansible-config/SKILL.md) | iac | Configure hosts using scoped inventories and idempotent playbooks. |
| [docker-build](skills/containers/docker-build/SKILL.md) | containers | Build minimal, multi-stage, hardened container images. |
| [kubernetes-ops](skills/containers/kubernetes-ops/SKILL.md) | containers | Deploy, debug, and operate Kubernetes and Helm safely. |
| [github-actions-pipelines](skills/cicd/github-actions-pipelines/SKILL.md) | cicd | Design least-privilege GitHub Actions delivery pipelines. |
| [gitlab-ci-pipelines](skills/cicd/gitlab-ci-pipelines/SKILL.md) | cicd | Design gated GitLab CI pipelines with protected credentials. |
| [local-dev-env](skills/local/local-dev-env/SKILL.md) | local | Set up desktop tools, Compose, and kind/minikube environments. |
| [onprem-provisioning](skills/onprem/onprem-provisioning/SKILL.md) | onprem | Provision bare metal, PXE, and Proxmox/VMware workloads. |
| [linux-server-admin](skills/onprem/linux-server-admin/SKILL.md) | onprem | Maintain Linux services, networking, storage, and patches. |
| [monitoring-logging](skills/observability/monitoring-logging/SKILL.md) | observability | Operate Prometheus, Grafana, Loki, and OpenTelemetry. |
| [secrets-management](skills/security/secrets-management/SKILL.md) | security | Manage Vault, SOPS, and cloud secret stores without exposing values. |
| [infra-security-scanning](skills/security/infra-security-scanning/SKILL.md) | security | Triage infrastructure and image findings with Trivy, Checkov, and tfsec. |

## Use with coding agents

Choose a skill's **leaf folder**, not its category folder. Native discovery paths
vary with client version; category nesting in this library is for organization,
not a promise that every client searches recursively. Copy the selected leaf
folder, including any `scripts/`, `references/`, and `assets/`, into a supported
skill location in your target project:

| Agent | Project-local installation |
| --- | --- |
| Claude Code | `.claude/skills/<name>/SKILL.md`; ask Claude to use the skill or invoke `/<name>` where supported. |
| GitHub Copilot | `.github/skills/<name>/SKILL.md` in a client supporting Agent Skills; ask Copilot to use the named skill. |
| OpenAI Codex | `.agents/skills/<name>/SKILL.md` in current clients; request the skill by name (for example `$terraform-opentofu`). |
| Cursor | `.cursor/skills/<name>/SKILL.md` in clients with Agent Skills support; ask the agent to use the named skill. |

If native discovery is unavailable, explicitly attach the chosen `SKILL.md` and
its referenced files to the conversation and ask the agent to follow it.
Do not treat `AGENTS.md` as a replacement for loading a skill. Review instructions
and scripts before allowing any execution; copying a skill does not grant consent.

Example from a local checkout (set these paths for your machine):

```sh
LIBRARY=/absolute/path/to/infra-agent-skills
PROJECT=/absolute/path/to/your-project
mkdir -p "$PROJECT/.claude/skills"
cp -R "$LIBRARY/skills/iac/terraform-opentofu" "$PROJECT/.claude/skills/"
```

Then ask: “Use terraform-opentofu to inspect this staging workspace and propose a
plan. Do not apply anything until I approve the exact plan and target.”

## Repository layout

```text
skills/<category>/<name>/SKILL.md
  scripts/       # optional reviewed helpers
  references/    # optional longer documentation
  assets/        # optional templates
templates/SKILL.template.md
scripts/validate_skills.py
.github/workflows/validate.yml
AGENTS.md
CONTRIBUTING.md
SECURITY.md
```

## Safety principles

1. Identify the environment first: cloud account/subscription/project, cluster
   context and namespace, or host/hypervisor and storage targets.
2. Prefer read-only inspection and dry runs (`terraform plan`, `kubectl diff`,
   Ansible `--check`) before proposing changes.
3. Require explicit user confirmation before any destructive or production-affecting
   action. Approval is specific to the target, scope, and reviewed change.
4. Never print, log, or commit secrets; redact diagnostics and use scoped,
   short-lived credentials. State, plans, and rendered configuration can be sensitive.
5. Always provide verification and rollback steps. Back up stateful data first;
   reverting configuration cannot recover deleted data.

## Contributing and validation

See [CONTRIBUTING.md](CONTRIBUTING.md) to add a skill or run the same checks as CI.
Participation follows our [Code of Conduct](CODE_OF_CONDUCT.md). Report
vulnerabilities using [SECURITY.md](SECURITY.md), not public issues.

## License

This project is licensed under the GNU General Public License, version 3 or
(at your option) any later version (**GPL-3.0-or-later**). See the full, unmodified
license text in [LICENSE](LICENSE).
