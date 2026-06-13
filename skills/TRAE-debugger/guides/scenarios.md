## Debugging Scenarios Quick Reference

Use this guide to quickly select hypotheses and instrumentation strategies based on bug type.

### Scenario → Hypothesis Mapping

| Scenario | Typical Symptoms | Top 3 Hypotheses (High→Low Likelihood) |
|----------|------------------|----------------------------------------|
| **UI Not Responding** | Click has no effect | 1. Event handler not attached 2. Handler throws error 3. API call fails silently |
| **Data Incorrect** | Wrong values displayed | 1. API returns wrong data 2. Transform function buggy 3. Cache stale |
| **Network Failure** | Request fails/times out | 1. Request params wrong 2. Server returns error 3. CORS/Auth error |
| **Performance Issue** | Operations lag | 1. Excessive re-renders 2. Large data processing 3. Blocking sync operation |
| **Intermittent Error** | Random failures | 1. Race condition 2. State read before write 3. Handler fires multiple times |
| **Memory Leak** | Progressive slowdown | 1. Event listeners not removed 2. Subscriptions not cleaned 3. Closures holding refs |

### Instrumentation Point Selection

| Scenario | Key Instrumentation Points |
|----------|---------------------------|
| UI Not Responding | Event binding → Handler entry → Handler exit → Error boundary |
| Data Incorrect | API response → Transform input/output → Render data |
| Network Failure | Request params → Response status → Error catch |
| Performance Issue | Function entry with timestamp → Loop iteration (sampled) → Function exit |
| Intermittent Error | Async op start/end with `traceId` and `seq` → State changes |
| Memory Leak | Resource create → Resource destroy → Counter tracking |

### Hypothesis Priority Rule

Always verify hypotheses in this order: **High Likelihood + Low Effort → High Likelihood + High Effort → Low Likelihood**

### Log Analysis by Scenario

| Scenario | What to Look For |
|----------|------------------|
| UI Not Responding | Missing logs in expected sequence |
| Data Incorrect | Before/after value differences |
| Network Failure | Status codes, error messages |
| Performance Issue | Time gaps between logs |
| Intermittent Error | Out-of-order `seq` numbers, interleaved `traceId` |
| Memory Leak | Counter values increasing over operations |
