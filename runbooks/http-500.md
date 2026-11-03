
# HTTP 500 Incident Runbook

## Initial Investigation

HTTP 500 errors indicate server-side request failures.
Check application logs, affected endpoints, error rates
and request timestamps.

## Deployment Correlation

If HTTP 500 errors appear after a deployment, compare
the deployment timestamp with the error timeline.

Inspect version changes and configuration differences.
Temporal correlation alone does not prove causation.

## Dependency Checks

Check database connectivity, connection pool exhaustion,
upstream API failures and request timeouts.

Collect exception details and dependency metrics
before identifying a root cause.

## Recommended Actions

Compare error rates before and after the incident.
Inspect failed request traces and affected replicas.

Do not perform restart or rollback without
appropriate authorization and supporting evidence.
