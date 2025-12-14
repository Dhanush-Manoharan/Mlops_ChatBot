"""
Automated Model Retraining Trigger System
Monitors performance and triggers retraining when needed
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import os
import json

logger = logging.getLogger(__name__)

class RetrainingTrigger:
    """Manages automated model retraining triggers"""
    
    def __init__(self):
        self.performance_threshold = 0.85  # Success rate threshold
        self.drift_threshold = 0.3  # Drift score threshold
        self.min_samples_for_evaluation = 100
        
        self.retraining_history = []
        self.last_retraining = None
        self.min_retraining_interval_hours = 24  # Minimum time between retrainings
    
    def evaluate_retraining_need(self, metrics: Dict[str, Any], 
                                 drift_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if retraining should be triggered
        
        Args:
            metrics: Current performance metrics
            drift_info: Data drift detection results
        
        Returns:
            Dictionary with retraining decision and reasoning
        """
        should_retrain = False
        reasons = []
        
        # Check if enough time has passed since last retraining
        if self.last_retraining:
            time_since_last = datetime.now() - self.last_retraining
            if time_since_last.total_seconds() / 3600 < self.min_retraining_interval_hours:
                return {
                    'should_retrain': False,
                    'reasons': ['Too soon since last retraining'],
                    'time_since_last_hours': time_since_last.total_seconds() / 3600
                }
        
        # Check 1: Performance degradation
        success_rate = metrics.get('success_rate_percent', 100) / 100
        if success_rate < self.performance_threshold:
            should_retrain = True
            reasons.append(f'Performance below threshold: {success_rate:.2%} < {self.performance_threshold:.2%}')
        
        # Check 2: Data drift detected
        if drift_info.get('drift_detected'):
            drift_score = drift_info.get('drift_score', 0)
            if drift_score > self.drift_threshold:
                should_retrain = True
                reasons.append(f'Significant data drift detected: {drift_score:.3f}')
        
        # Check 3: High error rate
        total_calls = metrics.get('total_api_calls', 0)
        failed_responses = metrics.get('failed_responses', 0)
        
        if total_calls >= self.min_samples_for_evaluation:
            error_rate = failed_responses / total_calls
            if error_rate > 0.15:  # More than 15% error rate
                should_retrain = True
                reasons.append(f'High error rate: {error_rate:.2%}')
        
        # Check 4: Response time degradation
        avg_response_time = metrics.get('avg_response_time_seconds', 0)
        if avg_response_time > 5.0:  # More than 5 seconds average
            should_retrain = True
            reasons.append(f'Response time degraded: {avg_response_time:.2f}s')
        
        result = {
            'should_retrain': should_retrain,
            'reasons': reasons,
            'timestamp': datetime.now().isoformat(),
            'metrics_evaluated': {
                'success_rate': success_rate,
                'drift_score': drift_info.get('drift_score', 0),
                'error_rate': failed_responses / total_calls if total_calls > 0 else 0,
                'avg_response_time': avg_response_time
            }
        }
        
        if should_retrain:
            logger.warning(f"🔄 Retraining triggered! Reasons: {', '.join(reasons)}")
            self._record_retraining_event(result)
        
        return result
    
    def trigger_retraining_pipeline(self, reason: str) -> bool:
        """
        Trigger the retraining pipeline

        Executes the automated retraining script which:
        1. Pulls latest data from database
        2. Retrains the model
        3. Validates new model
        4. Deploys if better than current
        """
        logger.info(f"🚀 Initiating retraining pipeline...")
        logger.info(f"📋 Reason: {reason}")

        try:
            import subprocess

            retraining_job = {
                'job_id': f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'triggered_at': datetime.now().isoformat(),
                'reason': reason,
                'status': 'initiated',
                'steps': [
                    'data_collection',
                    'preprocessing',
                    'training',
                    'validation',
                    'deployment'
                ]
            }

            # Save retraining job
            self._save_retraining_job(retraining_job)

            logger.info(f"✅ Retraining job created: {retraining_job['job_id']}")

            # Execute retraining script
            script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'retrain_model.py')

            if os.path.exists(script_path):
                logger.info(f"🔄 Executing retraining script: {script_path}")

                # Run retraining script in background
                process = subprocess.Popen(
                    ['python', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                logger.info(f"✅ Retraining pipeline started in background (PID: {process.pid})")
                logger.info(f"   Monitor logs for progress")
            else:
                logger.warning(f"⚠️ Retraining script not found at: {script_path}")
                logger.info(f"   Job recorded but not executed")

            # Update last retraining timestamp
            self.last_retraining = datetime.now()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to trigger retraining: {e}")
            return False
    
    def _record_retraining_event(self, event: Dict[str, Any]):
        """Record retraining event"""
        self.retraining_history.append(event)
        
        # Keep only last 100 events
        if len(self.retraining_history) > 100:
            self.retraining_history = self.retraining_history[-100:]
    
    def _save_retraining_job(self, job: Dict[str, Any]):
        """Save retraining job details"""
        # In production, save to database
        # For demo, save to file
        jobs_file = '/tmp/retraining_jobs.json'
        
        try:
            # Load existing jobs
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r') as f:
                    jobs = json.load(f)
            else:
                jobs = []
            
            # Add new job
            jobs.append(job)
            
            # Save
            with open(jobs_file, 'w') as f:
                json.dump(jobs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save retraining job: {e}")
    
    def get_retraining_status(self) -> Dict[str, Any]:
        """Get current retraining status"""
        return {
            'last_retraining': self.last_retraining.isoformat() if self.last_retraining else None,
            'total_retraining_events': len(self.retraining_history),
            'recent_events': self.retraining_history[-5:],  # Last 5 events
            'thresholds': {
                'performance_threshold': self.performance_threshold,
                'drift_threshold': self.drift_threshold,
                'min_retraining_interval_hours': self.min_retraining_interval_hours
            }
        }

# Global retraining trigger
retraining_trigger = RetrainingTrigger()

def get_retraining_trigger() -> RetrainingTrigger:
    """Get the global retraining trigger"""
    return retraining_trigger