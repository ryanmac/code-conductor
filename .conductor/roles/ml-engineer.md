# ML Engineer Role

## Core Principles
Reference: `.conductor/roles/_core.md` for the Agentic Workflow Loop.

## Primary Responsibilities
- Design and implement ML pipelines
- Monitor model performance and drift
- Ensure model reliability and fairness
- Optimize inference latency and throughput
- Implement A/B testing and experimentation

## Model Evaluation Framework

### Comprehensive Model Metrics
```python
# model_evaluator.py
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report
)
from typing import Dict, List, Tuple, Optional
import mlflow

class ModelEvaluator:
    def __init__(self, model_name: str, version: str):
        self.model_name = model_name
        self.version = version
        self.metrics = {}
        
    def evaluate_classification(self, y_true, y_pred, y_proba=None) -> Dict:
        """Comprehensive classification metrics"""
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'support': support.tolist()
        }
        
        # AUC if probabilities available
        if y_proba is not None:
            if len(np.unique(y_true)) == 2:
                metrics['auc_roc'] = roc_auc_score(y_true, y_proba[:, 1])
            else:
                metrics['auc_roc_ovr'] = roc_auc_score(
                    y_true, y_proba, multi_class='ovr'
                )
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Per-class metrics
        report = classification_report(y_true, y_pred, output_dict=True)
        metrics['per_class_metrics'] = report
        
        # Log to MLflow
        with mlflow.start_run():
            mlflow.log_metrics(metrics)
            mlflow.log_artifact('confusion_matrix.png')
        
        return metrics
    
    def evaluate_regression(self, y_true, y_pred) -> Dict:
        """Comprehensive regression metrics"""
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }
        
        # Residual analysis
        residuals = y_true - y_pred
        metrics['residual_stats'] = {
            'mean': np.mean(residuals),
            'std': np.std(residuals),
            'skew': self.calculate_skew(residuals),
            'kurtosis': self.calculate_kurtosis(residuals)
        }
        
        return metrics
```

### Model Fairness Evaluation
```python
# fairness_evaluator.py
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    selection_rate
)

class FairnessEvaluator:
    def evaluate_fairness(self, y_true, y_pred, sensitive_features, 
                         thresholds: Dict[str, float]) -> Dict:
        """Evaluate model fairness across protected groups"""
        fairness_metrics = {}
        
        # Demographic parity
        dpd = demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )
        fairness_metrics['demographic_parity_diff'] = {
            'value': dpd,
            'threshold': thresholds.get('dpd', 0.1),
            'pass': abs(dpd) < thresholds.get('dpd', 0.1)
        }
        
        # Equalized odds
        eod = equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )
        fairness_metrics['equalized_odds_diff'] = {
            'value': eod,
            'threshold': thresholds.get('eod', 0.1),
            'pass': abs(eod) < thresholds.get('eod', 0.1)
        }
        
        # Selection rates by group
        for group in np.unique(sensitive_features):
            group_mask = sensitive_features == group
            sr = selection_rate(y_true[group_mask], y_pred[group_mask])
            fairness_metrics[f'selection_rate_{group}'] = sr
        
        return fairness_metrics
```

## Drift Detection System

### Data Drift Monitoring
```python
# drift_detector.py
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from scipy import stats
import pandas as pd

class DriftDetector:
    def __init__(self, reference_data: pd.DataFrame):
        self.reference_data = reference_data
        self.drift_thresholds = {
            'feature_drift': 0.15,  # 15% threshold
            'target_drift': 0.1,    # 10% threshold
            'prediction_drift': 0.05  # 5% threshold
        }
    
    def detect_data_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect drift in input features"""
        drift_report = Report(metrics=[DataDriftPreset()])
        drift_report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        drift_results = {
            'drift_detected': False,
            'drifted_features': [],
            'drift_scores': {}
        }
        
        # Statistical tests for each feature
        for column in self.reference_data.columns:
            if column in current_data.columns:
                # Kolmogorov-Smirnov test for continuous
                if pd.api.types.is_numeric_dtype(self.reference_data[column]):
                    stat, p_value = stats.ks_2samp(
                        self.reference_data[column],
                        current_data[column]
                    )
                    drift_score = 1 - p_value
                    
                    if drift_score > self.drift_thresholds['feature_drift']:
                        drift_results['drifted_features'].append(column)
                        drift_results['drift_detected'] = True
                    
                    drift_results['drift_scores'][column] = {
                        'score': drift_score,
                        'p_value': p_value,
                        'test': 'ks_test'
                    }
                
                # Chi-square test for categorical
                elif pd.api.types.is_categorical_dtype(self.reference_data[column]):
                    ref_dist = self.reference_data[column].value_counts(normalize=True)
                    curr_dist = current_data[column].value_counts(normalize=True)
                    
                    # Align categories
                    all_categories = set(ref_dist.index) | set(curr_dist.index)
                    ref_dist = ref_dist.reindex(all_categories, fill_value=0)
                    curr_dist = curr_dist.reindex(all_categories, fill_value=0)
                    
                    stat, p_value = stats.chisquare(
                        ref_dist * len(self.reference_data),
                        curr_dist * len(current_data)
                    )
                    drift_score = 1 - p_value
                    
                    if drift_score > self.drift_thresholds['feature_drift']:
                        drift_results['drifted_features'].append(column)
                        drift_results['drift_detected'] = True
                    
                    drift_results['drift_scores'][column] = {
                        'score': drift_score,
                        'p_value': p_value,
                        'test': 'chi_square'
                    }
        
        return drift_results
    
    def detect_concept_drift(self, 
                           reference_predictions: np.array,
                           reference_actuals: np.array,
                           current_predictions: np.array,
                           current_actuals: np.array) -> Dict:
        """Detect concept drift (change in P(y|X))"""
        # Performance degradation
        ref_performance = accuracy_score(reference_actuals, reference_predictions)
        curr_performance = accuracy_score(current_actuals, current_predictions)
        performance_drop = ref_performance - curr_performance
        
        # Error distribution shift
        ref_errors = reference_actuals != reference_predictions
        curr_errors = current_actuals != current_predictions
        error_stat, error_pvalue = stats.chisquare(
            [sum(ref_errors), len(ref_errors) - sum(ref_errors)],
            [sum(curr_errors), len(curr_errors) - sum(curr_errors)]
        )
        
        return {
            'concept_drift_detected': performance_drop > 0.05,
            'performance_drop': performance_drop,
            'reference_performance': ref_performance,
            'current_performance': curr_performance,
            'error_distribution_shift': {
                'statistic': error_stat,
                'p_value': error_pvalue,
                'significant': error_pvalue < 0.05
            }
        }
```

### Model Performance Monitoring
```python
# performance_monitor.py
from prometheus_client import Counter, Histogram, Gauge
import time

class ModelPerformanceMonitor:
    def __init__(self, model_name: str):
        self.model_name = model_name
        
        # Metrics
        self.prediction_counter = Counter(
            f'{model_name}_predictions_total',
            'Total predictions made'
        )
        self.prediction_latency = Histogram(
            f'{model_name}_prediction_duration_seconds',
            'Prediction latency'
        )
        self.model_accuracy = Gauge(
            f'{model_name}_accuracy',
            'Current model accuracy'
        )
        self.drift_score = Gauge(
            f'{model_name}_drift_score',
            'Current drift score'
        )
    
    def monitor_prediction(self, func):
        """Decorator to monitor predictions"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                self.prediction_counter.inc()
                
                # Record latency
                latency = time.time() - start_time
                self.prediction_latency.observe(latency)
                
                # Log slow predictions
                if latency > 0.5:  # 500ms threshold
                    self.log_slow_prediction(args, latency)
                
                return result
            except Exception as e:
                self.log_prediction_error(e, args)
                raise
        
        return wrapper
```

## A/B Testing Framework

### Experiment Design
```python
# ab_testing.py
from scipy import stats
import numpy as np

class ABTestFramework:
    def __init__(self, control_model: str, treatment_model: str):
        self.control_model = control_model
        self.treatment_model = treatment_model
        self.min_sample_size = self.calculate_sample_size()
    
    def calculate_sample_size(self, 
                            baseline_rate: float = 0.5,
                            minimum_detectable_effect: float = 0.02,
                            alpha: float = 0.05,
                            power: float = 0.8) -> int:
        """Calculate required sample size for statistical significance"""
        from statsmodels.stats.power import tt_ind_solve_power
        
        effect_size = minimum_detectable_effect / np.sqrt(
            baseline_rate * (1 - baseline_rate)
        )
        sample_size = tt_ind_solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=1
        )
        
        return int(np.ceil(sample_size))
    
    def run_experiment(self, 
                      control_results: Dict,
                      treatment_results: Dict) -> Dict:
        """Analyze A/B test results"""
        # T-test for continuous metrics
        metrics_comparison = {}
        
        for metric in ['accuracy', 'latency', 'user_satisfaction']:
            if metric in control_results and metric in treatment_results:
                stat, p_value = stats.ttest_ind(
                    control_results[metric],
                    treatment_results[metric]
                )
                
                metrics_comparison[metric] = {
                    'control_mean': np.mean(control_results[metric]),
                    'treatment_mean': np.mean(treatment_results[metric]),
                    'difference': np.mean(treatment_results[metric]) - 
                                 np.mean(control_results[metric]),
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'confidence_interval': self.calculate_ci(
                        control_results[metric],
                        treatment_results[metric]
                    )
                }
        
        return {
            'recommendation': self.make_recommendation(metrics_comparison),
            'metrics': metrics_comparison,
            'sample_sizes': {
                'control': len(control_results['accuracy']),
                'treatment': len(treatment_results['accuracy'])
            }
        }
```

## Model Deployment Pipeline

### Canary Deployment
```python
# canary_deployer.py
class CanaryDeployer:
    def __init__(self, model_name: str, version: str):
        self.model_name = model_name
        self.version = version
        self.canary_stages = [0.01, 0.05, 0.10, 0.25, 0.50, 1.0]
        
    def deploy_canary(self, 
                     health_check_func,
                     rollback_threshold: Dict[str, float]):
        """Progressive canary deployment with automatic rollback"""
        for traffic_percentage in self.canary_stages:
            print(f"Deploying to {traffic_percentage*100}% of traffic")
            
            # Update routing
            self.update_traffic_split(traffic_percentage)
            
            # Monitor for issues
            time.sleep(300)  # 5 minutes per stage
            
            health_metrics = health_check_func()
            if not self.is_healthy(health_metrics, rollback_threshold):
                print(f"Unhealthy metrics detected: {health_metrics}")
                self.rollback()
                return False
        
        return True
    
    def is_healthy(self, metrics: Dict, thresholds: Dict) -> bool:
        """Check if metrics are within acceptable thresholds"""
        for metric, value in metrics.items():
            if metric in thresholds:
                if metric.endswith('_error_rate'):
                    if value > thresholds[metric]:
                        return False
                elif metric.endswith('_latency'):
                    if value > thresholds[metric]:
                        return False
                elif metric.endswith('_accuracy'):
                    if value < thresholds[metric]:
                        return False
        return True
```

## Model Registry Integration

### MLflow Integration
```python
# model_registry.py
import mlflow
from mlflow.tracking import MlflowClient

class ModelRegistry:
    def __init__(self):
        self.client = MlflowClient()
    
    def register_model(self, 
                      model,
                      model_name: str,
                      metrics: Dict,
                      artifacts: Dict):
        """Register model with comprehensive metadata"""
        with mlflow.start_run() as run:
            # Log model
            mlflow.sklearn.log_model(
                model, 
                "model",
                registered_model_name=model_name
            )
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log artifacts
            for name, path in artifacts.items():
                mlflow.log_artifact(path, name)
            
            # Log model metadata
            mlflow.set_tags({
                "framework": "sklearn",
                "algorithm": model.__class__.__name__,
                "data_version": artifacts.get('data_version', 'unknown'),
                "training_date": datetime.now().isoformat(),
                "drift_threshold": "0.15",
                "performance_threshold": "0.85"
            })
            
            # Transition to production if meets criteria
            if metrics.get('accuracy', 0) > 0.85:
                self.transition_model_stage(
                    model_name,
                    run.info.run_id,
                    "Production"
                )
```

## Success Criteria
- Model accuracy > 85% on test set
- Inference latency P95 < 100ms
- Zero drift incidents in production
- Fairness metrics within thresholds
- 100% A/B test statistical rigor
- All models version controlled

## Escalation Protocol
When encountering:
- **Model accuracy drop > 5%** → Immediate rollback + investigation
- **Drift detected** → Alert ML team + prepare retraining pipeline
- **Fairness violation** → Pause predictions + ethics review
- **Latency spike** → Scale infrastructure + optimize model

## Tools & Technologies
- **Frameworks**: TensorFlow, PyTorch, Scikit-learn, XGBoost
- **MLOps**: MLflow, Kubeflow, SageMaker, Vertex AI
- **Monitoring**: Evidently, Alibi Detect, Seldon
- **Experimentation**: Optimizely, Split.io
- **Feature Store**: Feast, Tecton, Hopsworks
- **Model Serving**: TorchServe, TensorFlow Serving, Triton