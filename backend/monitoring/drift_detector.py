"""
Data Drift Detection for PropBot
Monitors query patterns and detects distribution shifts
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    """Detects data drift in user queries and system behavior"""
    
    def __init__(self, window_size: int = 100, drift_threshold: float = 0.3):
        """
        Args:
            window_size: Number of recent queries to analyze
            drift_threshold: Threshold for detecting drift (0-1)
        """
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        
        # Store recent queries and their characteristics
        self.recent_queries = []
        self.baseline_stats = None
        self.drift_history = []
    
    def record_query(self, query_data: Dict[str, Any]):
        """Record a query for drift analysis"""
        query_data['timestamp'] = datetime.now()
        self.recent_queries.append(query_data)
        
        # Keep only recent window
        if len(self.recent_queries) > self.window_size:
            self.recent_queries = self.recent_queries[-self.window_size:]
        
        # Set baseline after collecting enough data
        if self.baseline_stats is None and len(self.recent_queries) >= 50:
            self.baseline_stats = self._calculate_statistics(self.recent_queries)
            logger.info("📊 Baseline statistics established")
    
    def detect_drift(self) -> Dict[str, Any]:
        """Detect if data drift has occurred"""
        if len(self.recent_queries) < 50:
            return {
                'drift_detected': False,
                'reason': 'Insufficient data for drift detection',
                'samples': len(self.recent_queries)
            }
        
        if self.baseline_stats is None:
            self.baseline_stats = self._calculate_statistics(self.recent_queries[:50])
        
        # Calculate current statistics
        current_stats = self._calculate_statistics(self.recent_queries[-50:])
        
        # Compare distributions
        drift_score = self._calculate_drift_score(self.baseline_stats, current_stats)
        drift_detected = drift_score > self.drift_threshold
        
        result = {
            'drift_detected': drift_detected,
            'drift_score': round(drift_score, 3),
            'threshold': self.drift_threshold,
            'baseline_stats': self.baseline_stats,
            'current_stats': current_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Record drift event
        if drift_detected:
            self.drift_history.append(result)
            logger.warning(f"⚠️ Data drift detected! Score: {drift_score:.3f}")
        
        return result
    
    def _calculate_statistics(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistical features of queries"""
        # Extract features
        query_lengths = [len(q.get('query', '')) for q in queries]
        properties_counts = [q.get('properties_count', 0) for q in queries]
        response_times = [q.get('response_time', 0) for q in queries]
        
        # Query type distribution
        query_types = [q.get('query_type', 'unknown') for q in queries]
        type_distribution = dict(Counter(query_types))
        
        # Neighborhood distribution (if available)
        neighborhoods = [q.get('neighborhood', 'unknown') for q in queries if 'neighborhood' in q]
        neighborhood_dist = dict(Counter(neighborhoods))
        
        return {
            'avg_query_length': np.mean(query_lengths) if query_lengths else 0,
            'std_query_length': np.std(query_lengths) if query_lengths else 0,
            'avg_properties_returned': np.mean(properties_counts) if properties_counts else 0,
            'avg_response_time': np.mean(response_times) if response_times else 0,
            'query_type_distribution': type_distribution,
            'neighborhood_distribution': neighborhood_dist,
            'total_queries': len(queries)
        }
    
    def _calculate_drift_score(self, baseline: Dict[str, Any], 
                               current: Dict[str, Any]) -> float:
        """Calculate drift score between two distributions"""
        scores = []
        
        # Compare numerical features
        numerical_features = ['avg_query_length', 'avg_properties_returned', 'avg_response_time']
        for feature in numerical_features:
            baseline_val = baseline.get(feature, 0)
            current_val = current.get(feature, 0)
            
            if baseline_val > 0:
                # Relative difference
                diff = abs(current_val - baseline_val) / baseline_val
                scores.append(min(diff, 1.0))  # Cap at 1.0
        
        # Compare distributions (KL divergence approximation)
        baseline_types = baseline.get('query_type_distribution', {})
        current_types = current.get('query_type_distribution', {})
        
        if baseline_types and current_types:
            type_drift = self._distribution_difference(baseline_types, current_types)
            scores.append(type_drift)
        
        # Average drift score
        return np.mean(scores) if scores else 0.0
    
    def _distribution_difference(self, dist1: Dict[str, int], 
                                 dist2: Dict[str, int]) -> float:
        """Calculate difference between two distributions"""
        # Normalize distributions
        total1 = sum(dist1.values())
        total2 = sum(dist2.values())
        
        if total1 == 0 or total2 == 0:
            return 0.0
        
        norm_dist1 = {k: v/total1 for k, v in dist1.items()}
        norm_dist2 = {k: v/total2 for k, v in dist2.items()}
        
        # Calculate Jensen-Shannon divergence (simplified)
        all_keys = set(norm_dist1.keys()) | set(norm_dist2.keys())
        
        diff_sum = 0
        for key in all_keys:
            p = norm_dist1.get(key, 0)
            q = norm_dist2.get(key, 0)
            diff_sum += abs(p - q)
        
        return diff_sum / 2  # Normalize to [0, 1]
    
    def should_trigger_retraining(self) -> bool:
        """Determine if retraining should be triggered"""
        # Check recent drift history
        recent_drifts = [d for d in self.drift_history 
                        if datetime.fromisoformat(d['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        # Trigger if multiple drifts detected in last 24 hours
        if len(recent_drifts) >= 3:
            logger.warning("🔄 Multiple drift events detected - retraining recommended")
            return True
        
        return False

# Global drift detector
drift_detector = DriftDetector(window_size=100, drift_threshold=0.3)

def get_drift_detector() -> DriftDetector:
    """Get the global drift detector"""
    return drift_detector