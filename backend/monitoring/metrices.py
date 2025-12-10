"""
Cloud Monitoring Integration for PropBot
Tracks model performance, API metrics, and system health
"""
import time
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and tracks metrics for monitoring"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'successful_responses': 0,
            'failed_responses': 0,
            'avg_response_time': [],
            'chromadb_queries': 0,
            'properties_returned': [],
            'query_types': {}
        }
        self.start_time = datetime.now()
    
    def record_api_call(self, success: bool, response_time: float, 
                       properties_count: int, query_type: str):
        """Record an API call with metrics"""
        self.metrics['api_calls'] += 1
        
        if success:
            self.metrics['successful_responses'] += 1
        else:
            self.metrics['failed_responses'] += 1
        
        self.metrics['avg_response_time'].append(response_time)
        self.metrics['properties_returned'].append(properties_count)
        self.metrics['chromadb_queries'] += 1
        
        # Track query types
        if query_type not in self.metrics['query_types']:
            self.metrics['query_types'][query_type] = 0
        self.metrics['query_types'][query_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response = (
            sum(self.metrics['avg_response_time']) / len(self.metrics['avg_response_time'])
            if self.metrics['avg_response_time'] else 0
        )
        
        avg_properties = (
            sum(self.metrics['properties_returned']) / len(self.metrics['properties_returned'])
            if self.metrics['properties_returned'] else 0
        )
        
        success_rate = (
            (self.metrics['successful_responses'] / self.metrics['api_calls'] * 100)
            if self.metrics['api_calls'] > 0 else 0
        )
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_api_calls': self.metrics['api_calls'],
            'successful_responses': self.metrics['successful_responses'],
            'failed_responses': self.metrics['failed_responses'],
            'success_rate_percent': round(success_rate, 2),
            'avg_response_time_seconds': round(avg_response, 3),
            'avg_properties_returned': round(avg_properties, 1),
            'chromadb_queries': self.metrics['chromadb_queries'],
            'query_types': self.metrics['query_types'],
            'uptime_seconds': round(uptime, 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health based on metrics"""
        metrics = self.get_metrics()
        
        # Health thresholds
        healthy = True
        issues = []
        
        # Check success rate
        if metrics['success_rate_percent'] < 95:
            healthy = False
            issues.append(f"Low success rate: {metrics['success_rate_percent']}%")
        
        # Check response time
        if metrics['avg_response_time_seconds'] > 3.0:
            healthy = False
            issues.append(f"High response time: {metrics['avg_response_time_seconds']}s")
        
        # Check if system is responding
        if metrics['total_api_calls'] > 0 and metrics['successful_responses'] == 0:
            healthy = False
            issues.append("No successful responses")
        
        return {
            'healthy': healthy,
            'issues': issues,
            'metrics': metrics
        }

# Global metrics collector
metrics_collector = MetricsCollector()

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    return metrics_collector