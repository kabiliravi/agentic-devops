# Security policy

## Responsible disclosure

Report vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/kabiliravi/agentic-devops/security/advisories/new).
Do not open a public issue or PR containing exploit details, credentials, or
sensitive infrastructure information. If private reporting is unavailable, ask
the maintainer through their GitHub profile for a private reporting channel,
without posting vulnerability details publicly.

Include the affected skill/file and revision, impact, prerequisites, and minimal
sanitized reproduction steps. Use a disposable lab, never another person's
infrastructure. Coordinate public disclosure with maintainers after remediation;
there is no guaranteed response SLA. Security fixes target the current default
branch; older copied skills must be updated by their users.

## Credentials and infrastructure data

Never commit credentials, tokens, private keys, `.env` files, Terraform state or
plans, variable secrets, or kubeconfigs. Never print or log secret values.
Use secret stores, short-lived credentials, and least privilege. Ignore rules are
only a backstop, not a substitute for reviewing every staged file.

If a credential is exposed, revoke/rotate it immediately, notify its owner through
a private channel, and review access logs. Removing a file or rewriting history
does not invalidate the credential or remove copies already made.

Skills are instructions, not a security sandbox. Review all scripts and proposed
commands, verify the target environment, start read-only, and require explicit
approval for destructive or production-affecting changes.
