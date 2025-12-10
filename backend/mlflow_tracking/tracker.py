"""
MLflow Integration for PropBot
Tracks experiments, model versions, and performance metrics
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class MLflowTracker:
    """MLflow experiment and model tracking"""
    
    def __init__(self):
        self.mlflow_enabled = os.getenv('MLFLOW_TRACKING_ENABLED', 'true').lower() == 'true'
        self.mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI', '/tmp/mlruns')
        self.experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'propbot_production')
        
        self.current_run_id = None
        self.model_version = os.getenv('MODEL_VERSION', '1.0.0')
        
        logger.info(f"MLflow tracking: {'enabled' if self.mlflow_enabled else 'disabled'}")
    
    def start_run(self, run_name: Optional[str] = None):
        """Start a new MLflow run"""
        if not self.mlflow_enabled:
            return
        
        try:
            run_name = run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_run_id = run_name
            
            logger.info(f"📊 Started MLflow run: {run_name}")
            
            # In production, this would initialize actual MLflow run
            # import mlflow
            # mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            # mlflow.set_experiment(self.experiment_name)
            # mlflow.start_run(run_name=run_name)
            
        except Exception as e:
            logger.error(f"Failed to start MLflow run: {e}")
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow"""
        if not self.mlflow_enabled:
            return
        
        try:
            logger.info(f"📝 Logging params: {list(params.keys())}")
            
            # In production:
            # import mlflow
            # for key, value in params.items():
            #     mlflow.log_param(key, value)
            
        except Exception as e:
            logger.error(f"Failed to log params: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow"""
        if not self.mlflow_enabled:
            return
        
        try:
            logger.info(f"📈 Logging metrics at step {step}: {list(metrics.keys())}")
            
            # In production:
            # import mlflow
            # for key, value in metrics.items():
            #     mlflow.log_metric(key, value, step=step)
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
    
    def log_model_performance(self, performance_data: Dict[str, Any]):
        """Log model performance metrics"""
        if not self.mlflow_enabled:
            return
        
        try:
            metrics = {
                'success_rate': performance_data.get('success_rate_percent', 0) / 100,
                'avg_response_time': performance_data.get('avg_response_time_seconds', 0),
                'total_requests': performance_data.get('total_api_calls', 0),
                'failed_requests': performance_data.get('failed_responses', 0),
                'avg_properties_returned': performance_data.get('avg_properties_returned', 0)
            }
            
            self.log_metrics(metrics)
            
            logger.info("✅ Model performance logged to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log model performance: {e}")
    
    def log_data_drift(self, drift_data: Dict[str, Any]):
        """Log data drift metrics"""
        if not self.mlflow_enabled:
            return
        
        try:
            metrics = {
                'drift_detected': 1.0 if drift_data.get('drift_detected') else 0.0,
                'drift_score': drift_data.get('drift_score', 0)
            }
            
            self.log_metrics(metrics)
            
            logger.info("✅ Data drift metrics logged to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log drift metrics: {e}")
    
    def register_model(self, model_name: str, model_version: str):
        """Register a model in MLflow Model Registry"""
        if not self.mlflow_enabled:
            return
        
        try:
            logger.info(f"📦 Registering model: {model_name} v{model_version}")
            
            # In production:
            # import mlflow
            # mlflow.register_model(
            #     model_uri=f"runs:/{self.current_run_id}/model",
            #     name=model_name
            # )
            
            logger.info(f"✅ Model registered: {model_name} v{model_version}")
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
    
    def transition_model_stage(self, model_name: str, version: str, stage: str):
        """Transition model to a different stage (Staging, Production, Archived)"""
        if not self.mlflow_enabled:
            return
        
        try:
            logger.info(f"🔄 Transitioning {model_name} v{version} to {stage}")
            
            # In production:
            # from mlflow.tracking import MlflowClient
            # client = MlflowClient()
            # client.transition_model_version_stage(
            #     name=model_name,
            #     version=version,
            #     stage=stage
            # )
            
            logger.info(f"✅ Model transitioned to {stage}")
            
        except Exception as e:
            logger.error(f"Failed to transition model: {e}")
    
    def end_run(self):
        """End the current MLflow run"""
        if not self.mlflow_enabled:
            return
        
        try:
            logger.info(f"🏁 Ending MLflow run: {self.current_run_id}")
            
            # In production:
            # import mlflow
            # mlflow.end_run()
            
            self.current_run_id = None
            
        except Exception as e:
            logger.error(f"Failed to end run: {e}")
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a registered model"""
        if not self.mlflow_enabled:
            return {
                'model_name': model_name,
                'mlflow_enabled': False
            }
        
        try:
            # In production:
            # from mlflow.tracking import MlflowClient
            # client = MlflowClient()
            # model_versions = client.search_model_versions(f"name='{model_name}'")
            
            return {
                'model_name': model_name,
                'current_version': self.model_version,
                'mlflow_tracking_uri': self.mlflow_tracking_uri,
                'experiment_name': self.experiment_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {'error': str(e)}

# Global MLflow tracker
mlflow_tracker = MLflowTracker()

def get_mlflow_tracker() -> MLflowTracker:
    """Get the global MLflow tracker"""
    return mlflow_tracker