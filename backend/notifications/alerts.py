"""
Notification System for PropBot
Sends alerts for drift detection, retraining, and system issues
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications for system events"""
    
    def __init__(self):
        self.notification_history = []
        self.email_enabled = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        self.slack_enabled = os.getenv('SLACK_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
    
    def send_drift_alert(self, drift_info: Dict[str, Any]):
        """Send alert when data drift is detected"""
        message = self._format_drift_message(drift_info)
        
        notification = {
            'type': 'drift_alert',
            'severity': 'warning',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': drift_info
        }
        
        self._dispatch_notification(notification)
    
    def send_retraining_alert(self, retraining_info: Dict[str, Any]):
        """Send alert when retraining is triggered"""
        message = self._format_retraining_message(retraining_info)
        
        notification = {
            'type': 'retraining_alert',
            'severity': 'info',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': retraining_info
        }
        
        self._dispatch_notification(notification)
    
    def send_performance_alert(self, metrics: Dict[str, Any]):
        """Send alert for performance issues"""
        message = self._format_performance_message(metrics)
        
        notification = {
            'type': 'performance_alert',
            'severity': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': metrics
        }
        
        self._dispatch_notification(notification)
    
    def send_deployment_success(self, deployment_info: Dict[str, Any]):
        """Send notification for successful deployment"""
        message = f"🎉 PropBot deployed successfully!\n"
        message += f"Version: {deployment_info.get('version', 'unknown')}\n"
        message += f"Environment: {deployment_info.get('environment', 'production')}\n"
        message += f"URL: {deployment_info.get('url', 'N/A')}"
        
        notification = {
            'type': 'deployment_success',
            'severity': 'info',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': deployment_info
        }
        
        self._dispatch_notification(notification)
    
    def _format_drift_message(self, drift_info: Dict[str, Any]) -> str:
        """Format drift detection message"""
        message = "⚠️ Data Drift Detected!\n\n"
        message += f"Drift Score: {drift_info.get('drift_score', 0):.3f}\n"
        message += f"Threshold: {drift_info.get('threshold', 0):.3f}\n"
        message += f"Time: {drift_info.get('timestamp', 'N/A')}\n\n"
        message += "Action Required: Review recent data patterns and consider retraining."
        
        return message
    
    def _format_retraining_message(self, retraining_info: Dict[str, Any]) -> str:
        """Format retraining trigger message"""
        message = "🔄 Model Retraining Triggered!\n\n"
        
        if 'reasons' in retraining_info:
            message += "Reasons:\n"
            for reason in retraining_info['reasons']:
                message += f"  • {reason}\n"
        
        message += f"\nTriggered at: {retraining_info.get('timestamp', 'N/A')}"
        
        return message
    
    def _format_performance_message(self, metrics: Dict[str, Any]) -> str:
        """Format performance alert message"""
        message = "⚠️ Performance Issue Detected!\n\n"
        message += f"Success Rate: {metrics.get('success_rate_percent', 0):.1f}%\n"
        message += f"Avg Response Time: {metrics.get('avg_response_time_seconds', 0):.2f}s\n"
        message += f"Failed Responses: {metrics.get('failed_responses', 0)}\n"
        message += f"Total API Calls: {metrics.get('total_api_calls', 0)}"
        
        return message
    
    def _dispatch_notification(self, notification: Dict[str, Any]):
        """Dispatch notification through configured channels"""
        # Record notification
        self.notification_history.append(notification)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        # Log notification
        severity = notification['severity']
        message = notification['message']
        
        if severity == 'error':
            logger.error(message)
        elif severity == 'warning':
            logger.warning(message)
        else:
            logger.info(message)
        
        # Send to external services (if configured)
        if self.email_enabled:
            self._send_email(notification)
        
        if self.slack_enabled and self.slack_webhook:
            self._send_slack(notification)
    
    def _send_email(self, notification: Dict[str, Any]):
        """Send email notification"""
        # In production, integrate with SendGrid, AWS SES, or similar
        logger.info(f"📧 Email notification would be sent: {notification['type']}")
    
    def _send_slack(self, notification: Dict[str, Any]):
        """Send Slack notification"""
        # In production, send to Slack webhook
        try:
            import requests
            
            if not self.slack_webhook:
                return
            
            slack_message = {
                'text': notification['message'],
                'username': 'PropBot Monitoring',
                'icon_emoji': ':robot_face:'
            }
            
            response = requests.post(self.slack_webhook, json=slack_message, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"💬 Slack notification sent: {notification['type']}")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
    
    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        return self.notification_history[-limit:]
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        if not self.notification_history:
            return {
                'total_notifications': 0,
                'by_type': {},
                'by_severity': {}
            }
        
        # Count by type
        by_type = {}
        by_severity = {}
        
        for notif in self.notification_history:
            notif_type = notif.get('type', 'unknown')
            severity = notif.get('severity', 'unknown')
            
            by_type[notif_type] = by_type.get(notif_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_notifications': len(self.notification_history),
            'by_type': by_type,
            'by_severity': by_severity
        }

# Global notification manager
notification_manager = NotificationManager()

def get_notification_manager() -> NotificationManager:
    """Get the global notification manager"""
    return notification_manager