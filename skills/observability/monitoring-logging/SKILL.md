---
name: monitoring-logging
description: Configure and troubleshoot metrics, dashboards, logs, and traces with Prometheus, Grafana, Loki, and OpenTelemetry. Use to establish actionable service signals without exposing sensitive telemetry or overloading production systems.
---

# Monitoring and logging

## When to use

Add service observability, diagnose missing telemetry, tune alerts, or investigate an incident across metrics, logs, and traces.

## Prerequisites

- Access to existing monitoring tooling, approved telemetry endpoints, and service ownership information.
- An agreed retention/privacy policy, authentication mechanism, and capacity budget.
- Identify the cloud account/project, Kubernetes cluster/context or host, tenant, and environment first. Confirm that read and write endpoints belong to the intended target.

## Inputs to gather

- Service inventory, SLOs, critical user journeys, dashboard/alert owners, and incident routes.
- Prometheus scrape endpoints, Grafana data sources, Loki tenant/retention, and OTel receiver/exporter endpoints.
- Expected volume/cardinality, sampling policy, storage capacity, authentication, and prohibited data fields.

## Steps

Commands in this skill are illustrative and unverified against your environment. Review targets and installed-version support before use.

1. **Start read-only or with a supported dry run.** Inspect existing dashboards, active alerts, scrape-target status, collector health, and recent configuration changes. Do not export raw telemetry or data-source configuration containing secrets.
2. Baseline request rate, error rate, latency, saturation, scrape failures, dropped spans/logs, and ingestion/storage usage. Scope queries by service/environment and a short time range to avoid expensive production scans.
3. For **Prometheus**, review scrape discovery, intervals, timeouts, relabeling, and TLS/auth settings. Avoid user IDs, request IDs, full URLs, or other unbounded label values. When the existing tooling is available, validate reviewed, non-secret files:

   ```sh
   promtool check config prometheus.yml
   promtool check rules alerts.yml
   ```

   Use actual project paths. Validators check syntax/semantics, not production capacity or target availability.
4. For **Grafana**, manage dashboards and data sources through the repository's existing provisioning process. Use scoped read-only data-source identities, folder permissions, and stable dashboard UIDs. Keep credentials in the approved secret store rather than dashboard JSON or URLs.
5. For **Loki**, choose low-cardinality labels such as service/environment and parse high-cardinality fields at query time. Define retention and ingestion limits appropriate to the installed storage/version. Filter sensitive fields before ingestion; access control and tenant isolation must be enforced at the configured gateway/backend, not assumed from a tenant header alone.
6. For **OpenTelemetry**, trace the path through receivers, processors, and exporters. Apply data allowlists/redaction before export, batch and memory limits, and an intentional sampling policy. Do not collect authorization headers, cookies, request bodies, or SQL parameter values by default. Check retry/queue behavior to prevent memory or disk exhaustion.
7. Stage configuration in non-production using existing project validators and a synthetic request with no sensitive payload. No universal cross-tool dry-run exists. Verify installed-version validation support rather than inventing flags.
8. Require explicit user confirmation before destructive or production-affecting actions, including reloads, collector rollouts, retention reductions, data deletion, broad queries with operational impact, or alert-routing changes. Roll out incrementally and watch the observability system's own health.
9. Add actionable alerts with ownership, severity, duration, and a runbook. Test notification routing in an approved test receiver; do not page production responders without coordination.

## Verification

- Confirm expected Prometheus targets are up and a bounded query returns fresh samples.
- Verify Grafana dashboards resolve the correct data source and honor access restrictions.
- Find the synthetic request's sanitized logs in Loki and trace in the intended OTel backend; check timestamps and cross-signal correlation.
- Check scrape duration, dropped telemetry, queue depth, cardinality, storage growth, and application overhead.
- Confirm alert state transitions and recovery notifications without exposing payloads or credentials.

## Rollback

- Preserve the previous configuration/dashboard revision and restore it using the same reviewed deployment mechanism.
- With required production confirmation, revert rollout or sampling/label changes and confirm ingestion recovers.
- Restore prior alert routing after a test; remove only test-specific silences.
- Retention reductions and telemetry deletion can permanently remove history; configuration rollback does not recover it. Use existing backups where supported and document gaps.

## Safety notes

- Never print, log, or commit secrets, exporter tokens, or credential-bearing telemetry. Keep incident examples redacted.
- Restrict monitoring endpoints and dashboards; they can expose infrastructure inventory and application data.
- Do not solve volume issues by silently dropping security/audit logs or disabling critical alerts.
