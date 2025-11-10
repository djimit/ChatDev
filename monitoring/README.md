# ChatDev Monitoring

This directory contains configuration files for monitoring ChatDev with Prometheus and Grafana.

## Overview

ChatDev provides comprehensive monitoring through Prometheus metrics, allowing you to track:

- Phase execution times and success rates
- API call latency and error rates
- Token usage and costs
- Agent interactions
- System resource usage
- Error rates by type

## Quick Start

### 1. Enable Monitoring in ChatDev

```python
from chatdev.monitoring import metrics

# Start Prometheus metrics server
metrics.start_http_server(port=8000)
```

### 2. Run Prometheus

```bash
# Using Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Or download and run locally
prometheus --config.file=monitoring/prometheus.yml
```

Access Prometheus at: http://localhost:9090

### 3. Set Up Grafana (Optional)

```bash
# Using Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# Import the dashboard
# 1. Open http://localhost:3000 (admin/admin)
# 2. Add Prometheus data source (http://prometheus:9090)
# 3. Import monitoring/grafana-dashboard.json
```

## Available Metrics

### Phase Metrics

- `chatdev_phase_duration_seconds` - Phase execution time histogram
- `chatdev_phase_executions_total` - Total phase executions by status

### API Metrics

- `chatdev_api_calls_total` - Total API calls by status
- `chatdev_api_duration_seconds` - API call latency histogram
- `chatdev_api_tokens_total` - Total tokens used
- `chatdev_api_cost_usd` - Estimated API costs

### Agent Metrics

- `chatdev_agent_messages_total` - Messages between agents
- `chatdev_conversation_turns` - Conversation turn count

### System Metrics

- `chatdev_active_projects` - Current active projects
- `chatdev_software_generated_total` - Total software generated
- `chatdev_errors_total` - Error count by type
- `chatdev_memory_usage_bytes` - Memory usage
- `chatdev_cpu_usage_percent` - CPU usage

## Querying Metrics

### Example Prometheus Queries

**Average phase duration:**
```promql
rate(chatdev_phase_duration_seconds_sum[5m])
/ rate(chatdev_phase_duration_seconds_count[5m])
```

**API success rate:**
```promql
sum(rate(chatdev_api_calls_total{status="success"}[5m]))
/ sum(rate(chatdev_api_calls_total[5m]))
* 100
```

**Total tokens per hour:**
```promql
increase(chatdev_api_tokens_total[1h])
```

**Error rate:**
```promql
rate(chatdev_errors_total[5m])
```

## Alerts

Alert rules are defined in `alerts.yml`:

- **HighAPIErrorRate**: API error rate > 10%
- **SlowAPIResponses**: 95th percentile latency > 30s
- **PhaseExecutionFailures**: > 3 failures in 15 minutes
- **HighMemoryUsage**: Memory usage > 2GB
- **HighErrorCount**: > 10 errors in 15 minutes
- **HighAPICost**: > $10/hour in API costs
- **ChatDevDown**: Service unreachable for > 2 minutes

## Configuration

### Prometheus Configuration

Edit `prometheus.yml` to:
- Change scrape intervals
- Add additional targets
- Configure alerting

### Alert Configuration

Edit `alerts.yml` to:
- Adjust alert thresholds
- Add custom alerts
- Modify alert labels

### Grafana Dashboard

The provided dashboard (`grafana-dashboard.json`) includes:
- Phase execution overview
- API performance metrics
- Cost tracking
- Error monitoring
- System resource usage

## Integration with ChatDev

### Automatic Tracking

```python
from chatdev.monitoring import track_phase

# Track phase execution
with track_phase("Coding"):
    execute_coding_phase()
```

### Manual Metrics

```python
from chatdev.monitoring import metrics

# Record phase execution
metrics.record_phase_execution(
    phase_name="Coding",
    duration=5.2,
    status="success"
)

# Record API call
metrics.record_api_call(
    api_name="OpenAI",
    method="chat.completions.create",
    duration=0.5,
    prompt_tokens=100,
    completion_tokens=200,
    cost=0.003
)

# Record error
metrics.record_error(
    error_type="ConfigurationError",
    component="chat_chain"
)
```

### Decorators

```python
from chatdev.monitoring import timed_operation

@timed_operation("custom_operation", {"component": "my_module"})
def my_operation():
    # Your code here
    pass
```

## Troubleshooting

### Metrics Not Showing

1. Ensure metrics server is running:
   ```python
   metrics.start_http_server(port=8000)
   ```

2. Check endpoint is accessible:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. Verify Prometheus is scraping:
   ```
   Check Prometheus UI → Status → Targets
   ```

### Prometheus Not Connecting

- Verify network connectivity
- Check firewall rules
- Ensure port 8000 is not blocked
- Check Prometheus logs

### Missing Dependencies

Install monitoring dependencies:
```bash
pip install prometheus-client structlog psutil
```

## Best Practices

1. **Production Setup**
   - Use persistent storage for Prometheus data
   - Set up Alertmanager for notifications
   - Configure retention policies
   - Use remote storage for long-term data

2. **Security**
   - Restrict metrics endpoint access
   - Use authentication for Grafana
   - Secure Prometheus with TLS

3. **Performance**
   - Adjust scrape intervals based on needs
   - Use recording rules for complex queries
   - Monitor Prometheus resource usage

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
