# Contributing

## Add a skill

1. Open a new skill request to discuss scope and overlap.
2. Pick an existing category or propose a focused new one.
3. Copy `templates/SKILL.template.md` to `skills/<category>/<name>/SKILL.md`.
4. Replace the frontmatter and every placeholder. Use a unique lowercase,
   hyphenated name matching the leaf folder, such as `network-diagnostics`.
   Names may contain digits, must be at most 64 characters, and cannot start/end
   with a hyphen or contain consecutive hyphens.
5. Write one or two description sentences explaining what it does and when to use
   it. Fill every section with practical instructions, platform/tool prerequisites,
   target selection, safe examples, and realistic recovery limits.
6. Put optional helpers in `scripts/`, longer docs in `references/`, and templates
   in `assets/`. Use relative references, quote shell variables, and avoid extra
   dependencies unless justified.
7. Update the README skill table.

## Required checklist

- [ ] Valid YAML frontmatter; name matches folder and description is non-empty.
- [ ] Safety notes are present with all five mandatory rules from `AGENTS.md`.
- [ ] Commands tested in a disposable, non-production environment, or explicitly
      marked illustrative/unverified with version and platform limitations.
- [ ] Verification and rollback steps cover partial failure and stateful data.
- [ ] No secrets, credentials, private endpoints, state, or sensitive logs committed.
- [ ] README table and relative links updated; validation passes.

Never run destructive or production-affecting commands without explicit approval.
For live command testing, record the tool versions, platform, safe target type,
and sanitized outcome in the PR; do not include secret output.

## Validation

CI checks all category-nested skills recursively, Markdown, and shell scripts.
Use Python 3.12, Node.js 22, and ShellCheck, matching the workflow:

```sh
python -m pip install PyYAML==6.0.3
npm install --global markdownlint-cli@0.50.0
python scripts/validate_skills.py
markdownlint '**/*.md' --ignore node_modules
find skills scripts -type f -name '*.sh' -print0 | xargs -0 -r shellcheck
```

The validator also checks that all required instruction sections exist and that
skill names are unique. A repository with no skills fails validation. ShellCheck
is a no-op until `.sh` helpers exist. Markdown rules are in `.markdownlint.json`;
line lengths and duplicate section titles across documents are not constrained.
No cloud access is needed for these checks.

## Pull requests

Use the PR template. Explain the problem, skill scope, safety decisions, testing,
and compatibility. Keep unrelated refactors out of the PR. Maintainers review
portability, command safety, and documentation before merging; address feedback
and rerun validation. Do not attach real credentials or raw sensitive diagnostics.

Contributions are provided under GPL-3.0-or-later, the project's license.
Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and report vulnerabilities privately
as described in [SECURITY.md](SECURITY.md).
