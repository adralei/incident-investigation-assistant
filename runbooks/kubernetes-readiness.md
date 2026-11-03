
# Kubernetes Readiness Runbook

## Replica Health

When ready replicas are fewer than desired replicas,
inspect pod readiness status and recent events.

A degraded service may have unavailable pods.

## Readiness Probe Investigation

Check readiness probe failures, application startup,
resource pressure and dependency availability.

A failed readiness probe does not identify
the root cause by itself.

## Deployment Health

Compare the deployment timeline with changes
in pod readiness and replica availability.

Inspect rollout status and configuration changes.

## Recommended Actions

Collect pod events, readiness probe results,
container restart counts and relevant application logs.

Do not modify production resources during
read-only incident investigation.
