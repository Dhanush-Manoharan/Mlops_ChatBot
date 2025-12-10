"""
Google Cloud Logging Integration
Structured logging for production monitoring
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StructuredLogger:
    """Structured logging for Cloud Logging"""
    
    @staticmethod
    def log_api_request(query: str, response_time: float, 
                       success: bool, properties_count: int):
        """Log API request with structured data"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'api_request',
            'query': query[:100],  # Truncate long queries
            'response_time_seconds': round(response_time, 3),
            'success': success,
            'properties_returned': properties_count,
            'severity': 'INFO' if success else 'ERROR'
        }
        
        logger.info(json.dumps(log_entry))
    
    @staticmethod
    def log_chromadb_query(collection: str, query: str, 
                          results_count: int, query_time: float):
        """Log ChromaDB query"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'chromadb_query',
            'collection': collection,
            'query': query[:50],
            'results_count': results_count,
            'query_time_seconds': round(query_time, 3),
            'severity': 'INFO'
        }
        
        logger.info(json.dumps(log_entry))
    
    @staticmethod
    def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log error with context"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'severity': 'ERROR'
        }
        
        logger.error(json.dumps(log_entry))
    
    @staticmethod
    def log_drift_detection(drift_detected: bool, metrics: Dict[str, Any]):
        """Log data drift detection results"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'drift_detection',
            'drift_detected': drift_detected,
            'metrics': metrics,
            'severity': 'WARNING' if drift_detected else 'INFO'
        }
        
        logger.warning(json.dumps(log_entry)) if drift_detected else logger.info(json.dumps(log_entry))
    
    @staticmethod
    def log_retraining_trigger(reason: str, metrics: Dict[str, Any]):
        """Log model retraining trigger"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'retraining_trigger',
            'reason': reason,
            'metrics': metrics,
            'severity': 'WARNING'
        }
        
        logger.warning(json.dumps(log_entry))

# Global structured logger
structured_logger = StructuredLogger()

def get_structured_logger() -> StructuredLogger:
    """Get the global structured logger"""
    return structured_logger