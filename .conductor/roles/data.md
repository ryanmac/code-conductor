# Data Engineer Role

## Overview
Specialist role focused on designing and implementing scalable data pipelines, ensuring data quality, and managing data infrastructure.

## Core Principles
Reference: `.conductor/roles/_core.md` for the Agentic Workflow Loop.

## Responsibilities
- Design and implement scalable data pipelines
- Ensure data quality and reliability
- Monitor pipeline performance and health
- Implement data governance and security
- Optimize data processing and storage

## Pipeline Monitoring & Quality Gates

### Real-Time Pipeline Monitoring
```bash
# Monitor active pipelines
airflow dags list --output=table
airflow tasks states-for-dag-run $DAG_ID $RUN_ID

# Check pipeline metrics
python -c "
from prometheus_client import CollectorRegistry, Gauge
registry = CollectorRegistry()
pipeline_latency = Gauge('pipeline_latency_seconds', 'Pipeline processing latency', registry=registry)
pipeline_throughput = Gauge('pipeline_throughput_records', 'Records processed per minute', registry=registry)
pipeline_errors = Gauge('pipeline_error_rate', 'Error rate percentage', registry=registry)
"

# Monitor data freshness
dbt source freshness
```

### Data Quality Gates
```yaml
# dbt tests configuration
version: 2
models:
  - name: fact_orders
    tests:
      - not_null:
          columns: [order_id, customer_id, order_date]
      - unique:
          columns: [order_id]
      - relationships:
          column: customer_id
          to: ref('dim_customers')
          field: customer_id
    columns:
      - name: order_amount
        tests:
          - not_null
          - accepted_values:
              values: ['pending', 'completed', 'cancelled']
      - name: order_total
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
```

### Pipeline Health Checks
```python
# pipeline_monitor.py
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

class PipelineMonitor:
    def __init__(self):
        self.thresholds = {
            'latency_p95': 300,  # 5 minutes
            'error_rate': 0.01,  # 1%
            'data_freshness': 3600,  # 1 hour
            'schema_drift': 0.05  # 5% tolerance
        }
    
    def check_pipeline_health(self, pipeline_id: str) -> Dict:
        health_status = {
            'pipeline_id': pipeline_id,
            'timestamp': datetime.utcnow(),
            'checks': {}
        }
        
        # Latency check
        latency = self.get_latency_p95(pipeline_id)
        health_status['checks']['latency'] = {
            'value': latency,
            'threshold': self.thresholds['latency_p95'],
            'status': 'pass' if latency < self.thresholds['latency_p95'] else 'fail'
        }
        
        # Error rate check
        error_rate = self.get_error_rate(pipeline_id)
        health_status['checks']['error_rate'] = {
            'value': error_rate,
            'threshold': self.thresholds['error_rate'],
            'status': 'pass' if error_rate < self.thresholds['error_rate'] else 'fail'
        }
        
        # Data freshness check
        freshness = self.get_data_freshness(pipeline_id)
        health_status['checks']['freshness'] = {
            'value': freshness,
            'threshold': self.thresholds['data_freshness'],
            'status': 'pass' if freshness < self.thresholds['data_freshness'] else 'fail'
        }
        
        return health_status
```

## Data Validation Framework

### Schema Validation
```python
# schema_validator.py
from great_expectations.core import ExpectationSuite
from great_expectations.dataset import PandasDataset

def validate_schema(df: pd.DataFrame, expected_schema: dict) -> bool:
    """Validate dataframe against expected schema"""
    dataset = PandasDataset(df)
    
    # Column existence
    for col in expected_schema['required_columns']:
        result = dataset.expect_column_to_exist(col)
        if not result['success']:
            return False
    
    # Data types
    for col, dtype in expected_schema['column_types'].items():
        result = dataset.expect_column_values_to_be_of_type(col, dtype)
        if not result['success']:
            return False
    
    # Value constraints
    for col, constraints in expected_schema['constraints'].items():
        if 'min' in constraints:
            dataset.expect_column_values_to_be_between(
                col, min_value=constraints['min'], max_value=constraints['max']
            )
    
    return True
```

### Data Profiling
```python
# data_profiler.py
import pandas_profiling
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataQualityMetrics:
    completeness: float
    uniqueness: float
    validity: float
    consistency: float
    timeliness: float
    accuracy: float

def profile_data(df: pd.DataFrame, output_path: str) -> DataQualityMetrics:
    """Generate comprehensive data profile"""
    profile = pandas_profiling.ProfileReport(
        df,
        title="Data Quality Report",
        explorative=True,
        interactions={
            "continuous": True,
            "targets": ["target_column"]
        },
        correlations={
            "pearson": {"calculate": True},
            "spearman": {"calculate": True},
            "kendall": {"calculate": False}
        }
    )
    
    profile.to_file(output_path)
    
    # Calculate quality metrics
    metrics = DataQualityMetrics(
        completeness=1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1]),
        uniqueness=df.nunique().mean() / len(df),
        validity=validate_business_rules(df),
        consistency=check_referential_integrity(df),
        timeliness=check_data_freshness(df),
        accuracy=validate_against_source(df)
    )
    
    return metrics
```

## Data Lineage & Governance

### Lineage Tracking
```yaml
# lineage.yml
pipelines:
  customer_360:
    sources:
      - database: raw_db
        tables: [customers, orders, interactions]
    transformations:
      - step: deduplicate_customers
        input: raw_db.customers
        output: staging.clean_customers
      - step: enrich_with_orders
        inputs: [staging.clean_customers, raw_db.orders]
        output: staging.customer_orders
    outputs:
      - table: analytics.customer_360
        consumers: [marketing_team, sales_dashboard]
```

### Access Control
```sql
-- Data access policies
CREATE POLICY customer_data_policy ON analytics.customer_360
FOR SELECT
TO data_analysts
USING (
    CASE 
        WHEN current_user IN ('senior_analyst', 'data_admin') THEN true
        WHEN current_user = 'analyst' THEN region = current_setting('app.user_region')
        ELSE false
    END
);
```

## Performance Optimization

### Query Optimization
```sql
-- Optimize slow queries
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.customer_id, 
       c.customer_name,
       COUNT(o.order_id) as order_count,
       SUM(o.total_amount) as lifetime_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY c.customer_id, c.customer_name;

-- Create optimized indexes
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date) 
WHERE order_date >= CURRENT_DATE - INTERVAL '1 year';
```

### Resource Management
```python
# resource_optimizer.py
def optimize_spark_job(df_size_gb: float) -> dict:
    """Calculate optimal Spark configuration"""
    # Estimate partitions
    optimal_partitions = int(df_size_gb * 1024 / 128)  # 128MB per partition
    
    # Calculate executor resources
    executor_memory = "4g" if df_size_gb < 100 else "8g"
    executor_cores = 4
    num_executors = max(10, int(df_size_gb / 10))
    
    return {
        "spark.sql.shuffle.partitions": optimal_partitions,
        "spark.executor.memory": executor_memory,
        "spark.executor.cores": executor_cores,
        "spark.executor.instances": num_executors,
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true"
    }
```

## Incident Response

### Pipeline Failure Playbook
1. **Immediate Actions**
   ```bash
   # Check pipeline status
   airflow dags state $DAG_ID $EXECUTION_DATE
   
   # View recent logs
   airflow logs -t $TASK_ID -d $DAG_ID -e $EXECUTION_DATE
   
   # Check resource utilization
   kubectl top pods -n data-pipeline
   ```

2. **Root Cause Analysis**
   ```python
   # failure_analyzer.py
   def analyze_failure(pipeline_id: str, execution_time: datetime):
       failure_patterns = {
           'OOM': r'java.lang.OutOfMemoryError|MemoryError',
           'Schema': r'schema mismatch|column.*not found',
           'Connection': r'connection refused|timeout',
           'Permission': r'permission denied|access denied'
       }
       
       logs = fetch_pipeline_logs(pipeline_id, execution_time)
       for pattern_name, pattern in failure_patterns.items():
           if re.search(pattern, logs, re.IGNORECASE):
               return trigger_remediation(pattern_name, pipeline_id)
   ```

3. **Recovery Procedures**
   ```bash
   # Retry failed tasks
   airflow tasks retry -d $DAG_ID -t $TASK_ID -e $EXECUTION_DATE
   
   # Backfill missing data
   airflow dags backfill -s $START_DATE -e $END_DATE $DAG_ID
   ```

## Success Criteria
- Pipeline uptime ≥ 99.5%
- Data quality score ≥ 95%
- P95 latency < 5 minutes
- Zero data loss incidents
- 100% schema compatibility
- All quality gates passing

## Escalation Protocol
When encountering:
- **Production data loss** → Immediate escalation to data lead + incident commander
- **Security breach** → Security team + pause all pipelines
- **Compliance violation** → Legal team + audit trail preservation
- **Infrastructure failure** → DevOps team + failover activation

## Tools & Technologies
- **Orchestration**: Airflow, Prefect, Dagster
- **Processing**: Spark, Flink, Beam
- **Quality**: Great Expectations, dbt, Soda
- **Monitoring**: Datadog, Prometheus, Grafana
- **Lineage**: DataHub, Apache Atlas, Amundsen
- **Storage**: S3, BigQuery, Snowflake, Delta Lake