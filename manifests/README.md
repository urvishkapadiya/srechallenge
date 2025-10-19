## Overview

**dumbkv** is a simple key-value store web service written in Python, exposing REST APIs to store and retrieve data.  
It supports **SQLite** (default) and **PostgreSQL** backends, and exposes a `/metrics` endpoint compatible with **Prometheus** for observability.

This project demonstrates how such an application can be managed in a **Kubernetes setup**, emphasizing:

- Reproducible infrastructure using **Kustomize**
- Secure configuration management
- Storage persistence across environments
- Monitoring & alerting (Service montior)
- SLO-driven reliability objectives

---

## Implementation Summary - Kubernetes Manifests

### **Base Components**
- **Deployment:** Defines `dumbkv` container, environment variables, probes, and persistent volume mounts.
- **Service:** Exposes the app on port `8000` within the cluster.
- **PVC:** Uses `efs` (or equivalent) storage class to ensure durability.
- **Ingress:** Handles external HTTPS access via `cert-manager` and letsencrypt.
- **kustomization.yaml:** Defines reusable base for environment overlays.

### **SQLite Overlay**
- Uses local SQLite storage (PVC mounted at `/data/dumbkvstore`).
- Simplified setup suitable for local or testing environments.
- Deployment strategy: `Recreate` (ensures single-instance consistency).

### **PostgreSQL Overlay**
- Adds a full in-cluster PostgreSQL deployment.
- Includes dedicated secrets, configmaps, service, and PVC for DB persistence.
- `dumbkv` app reconfigured to use connection string via environment variables.
- Ideal for production-grade deployments.

## Ingress & Security
- Secured via TLS certificates automatically issued by `cert-manager` using the `letsencrypt` ClusterIssuer.
- Ingress exposes application under:  
  **Health endpoint:** `https://dumbkv.example.com/health`  
  **Metrics endpoint:** `https://dumbkv.example.com/metrics`

## Monitoring & Observability
- Integrated **Prometheus Operator** via `ServiceMonitor`.
- Automatically scrapes `/metrics` endpoint from `dumbkv` pods.
- Configurable scrape interval: `15s`, timeout: `10s`.
- Metrics visualized using **Grafana dashboards**:
  - Request rate
  - Error percentage
  - Latency percentiles (p50, p95, p99)
  - Pod availability
  - Storage health
- Alerts defined for:
  - High error rate
  - Latency spikes
  - Pod CrashLoop or PVC unavailability
  - TLS certificate expiry

> Full SLOs (availability, latency, error budget) are defined in [SLOs.md](../SLOs-and-Monioring.md).

---

## Deployment Guide

### **SQLite Backend (Default)**
```bash
kubectl apply -k manifests/overlays/sqlite/
```

### **PostgreSQL Backend**
Deploy the application along with a PostgreSQL database:

```bash
kubectl apply -k manifests/overlays/postgres/
```

### **Verify Deployment**
Check that all resources are running correctly:

```bash
kubectl get pods,svc,ingress,pvc
```

### **Moniroting Setup**

```bash
kubectl apply -k manifests/monitoring/
```

### **Access Application**  
**Health endpoint:** [https://dumbkv.example.com/health]  
**Metrics endpoint:** [https://dumbkv.example.com/metrics]
