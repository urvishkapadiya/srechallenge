# SRE Challenge: `dumbkv` Service – Service Level Objectives (SLOs) & Monitoring Plan

**Author:** Urvishkumar Kapadiya  
**Date:** 2025-10-19  
**Application:** `dumbkv` a Key-Value Store Service  

---

## Application Overview

`dumbkv` is a lightweight key-value store service exposed via a REST API, supporting **SQLite** (base) and **PostgreSQL** (overlay) backends.  

- **SQLite backend:** Single replica, minimal configuration, suitable for dev/test environments.  
- **PostgreSQL backend:** Production-ready with separate PVC, secrets-managed credentials, and independent service deployment.  

**Exposure:**  
- Kubernetes Service for internal access  
- Ingress for external HTTPS access (`dumbkv.example.com`)  
- TLS handled via cert-manager using `letsencrypt` ClusterIssuer  

**Observability:**  
- Metrics available at `/metrics` for Prometheus scraping  
- Liveness and readiness probes ensure pod health and auto-restart  

---

## 1. Service Level Objectives (SLOs)

### 1.1 Availability
- **Definition:** Successful HTTP responses (2xx, 3xx) versus total requests.  
- **Target:** 99.9% uptime over a 30-day rolling window (~43 minutes downtime/month).  
- **Rationale:** Ensures client reliability; downtime directly impacts users and automated clients.  
- **Monitoring:** K8s readiness probes, Prometheus uptime metrics  

### 1.2 Latency
- **Definition:** Time taken to process each API request.  
- **Target:**  
  - 95th percentile ≤ 200ms  
  - 99th percentile ≤ 500ms  
- **Rationale:** Most requests should be served quickly; rare spikes tolerated in the 99th percentile.  
- **Monitoring:** Prometheus histograms, Grafana dashboards  

### 1.3 Error Rate
- **Definition:** Fraction of failed requests (HTTP 5xx or DB errors).  
- **Target:** < 1% per month  
- **Rationale:** Ensures reliability while allowing small, manageable failures.  
- **Monitoring:** Prometheus, Alertmanager  

### 1.4 Error Budget
- **Definition:** Permitted fraction of failed requests or latency violations in a given period  
- **Target:** 0.1% of total requests per month  
- **Usage:** Guides safe deployment decisions and remediation priorities  

### 1.5 Storage Persistence
- **Definition:** PVC mount availability and database integrity  
- **Target:** 100% PVC availability and successful DB writes  
- **Monitoring:** K8s PV/PVC events, container logs  

### 1.6 Ingress Success Rate
- **Definition:** Percentage of successful HTTPS requests through Ingress  
- **Target:** 99.9% success rate  
- **Monitoring:** Nginx ingress metrics via Prometheus  

## 2. Key Metrics to Collect

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Source</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>HTTP request count by status code</td>
      <td><code>/metrics</code> via Prometheus</td>
      <td>Segregate 2xx, 4xx, 5xx</td>
    </tr>
    <tr>
      <td>Response latency</td>
      <td><code>/metrics</code> histograms</td>
      <td>p50, p95, p99 for alerting</td>
    </tr>
    <tr>
      <td>Database connection pool usage</td>
      <td>DB exporter or app metrics</td>
      <td>Detect saturation</td>
    </tr>
    <tr>
      <td>Active keys / store size</td>
      <td>Application metrics</td>
      <td>Monitor data growth trends</td>
    </tr>
    <tr>
      <td>Pod health</td>
      <td>Liveness/Readiness probes</td>
      <td>Ensures only healthy pods serve traffic</td>
    </tr>
    <tr>
      <td>PVC/storage usage</td>
      <td>K8s PV/PVC metrics</td>
      <td>Detects storage exhaustion</td>
    </tr>
  </tbody>
</table>

## 3. Monitoring Components**

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Purpose</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Prometheus ServiceMonitor</td>
      <td>Scrape <code>/metrics</code></td>
      <td>Interval 15s, timeout 10s, sample limit 10k</td>
    </tr>
    <tr>
      <td>Grafana Dashboards</td>
      <td>Visualize latency, error rate, DB metrics</td>
      <td>Optional alert panels</td>
    </tr>
    <tr>
      <td>Alertmanager</td>
      <td>Notify on SLO breach</td>
      <td>Slack / email / webhook</td>
    </tr>
  </tbody>
</table>

## 4. Alerts and Remediation

<table>
  <thead>
    <tr>
      <th>Alert</th>
      <th>Trigger</th>
      <th>Remediation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>High Error Rate</td>
      <td>&gt;1% 5xx over 10 min</td>
      <td>Investigate logs, restart pods if necessary</td>
    </tr>
    <tr>
      <td>Latency Spike</td>
      <td>p99 &gt; 500ms over 5 min</td>
      <td>Check DB health, scale pods, review resources</td>
    </tr>
    <tr>
      <td>PVC Unavailable</td>
      <td>Volume not mounted</td>
      <td>Check storage class / EFS availability</td>
    </tr>
    <tr>
      <td>Pod CrashLoop</td>
      <td>Pod restarts &gt; 3 times</td>
      <td>Inspect logs, possible rollback</td>
    </tr>
    <tr>
      <td>TLS Expiry</td>
      <td>Cert expires in 7 days</td>
      <td>Renew certificate via cert-manager</td>
    </tr>
  </tbody>
</table>

## 5. Deployment Considerations

- **SQLite backend:** Single replica, ensures minimal configuration
- **PostgreSQL backend:** Monitor database separately; Postgres exporter recommended
- **Probes:** Liveness and readiness probes protect traffic routing
- **Ingress:** TLS termination via cert-manager ensures secure external access
- **Storage:** PVCs for persistent data (EFS for shared access)

## 6. Continuous Improvement

- Review error budgets monthly to balance reliability vs. deployment velocity
- Adjust SLO thresholds based on traffic and latency distributions
- Use canary deployments to minimize risk on updates
- Leverage automated rollbacks on SLO violations