"""
Quick verification script to check all monitoring dependencies
Run this before deployment to ensure everything imports correctly
"""
import sys
import os
import logging

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports"""
    logger.info("🔍 Testing monitoring system imports...")

    errors = []
    warnings = []

    # Test core dependencies
    try:
        import numpy
        logger.info("✅ numpy imported successfully")
    except ImportError as e:
        errors.append(f"❌ numpy: {e}")

    try:
        import requests
        logger.info("✅ requests imported successfully")
    except ImportError as e:
        errors.append(f"❌ requests: {e}")

    try:
        import mlflow
        logger.info("✅ mlflow imported successfully")
    except ImportError as e:
        warnings.append(f"⚠️  mlflow: {e} (optional)")

    # Test monitoring modules
    try:
        from monitoring.metrics import get_metrics_collector
        collector = get_metrics_collector()
        logger.info("✅ metrics module imported successfully")
    except Exception as e:
        errors.append(f"❌ metrics module: {e}")

    try:
        from monitoring.drift_detector import get_drift_detector
        detector = get_drift_detector()
        logger.info("✅ drift_detector module imported successfully")
    except Exception as e:
        errors.append(f"❌ drift_detector: {e}")

    try:
        from monitoring.cloud_logger import get_structured_logger
        logger_obj = get_structured_logger()
        logger.info("✅ cloud_logger module imported successfully")
    except Exception as e:
        errors.append(f"❌ cloud_logger: {e}")

    try:
        from retraining.trigger import get_retraining_trigger
        trigger = get_retraining_trigger()
        logger.info("✅ retraining.trigger module imported successfully")
    except Exception as e:
        errors.append(f"❌ retraining.trigger: {e}")

    try:
        from notifications.alerts import get_notification_manager
        notif = get_notification_manager()
        logger.info("✅ notifications.alerts module imported successfully")
    except Exception as e:
        errors.append(f"❌ notifications.alerts: {e}")

    try:
        from mlflow_tracking.tracker import get_mlflow_tracker
        tracker = get_mlflow_tracker()
        logger.info("✅ mlflow_tracking.tracker module imported successfully")
    except Exception as e:
        warnings.append(f"⚠️  mlflow_tracking.tracker: {e} (optional)")

    # Print summary
    logger.info("="*60)

    if warnings:
        logger.warning(f"⚠️  {len(warnings)} optional dependency warnings:")
        for warning in warnings:
            logger.warning(f"   {warning}")

    if errors:
        logger.error(f"❌ {len(errors)} critical import errors found:")
        for error in errors:
            logger.error(f"   {error}")
        return False
    else:
        logger.info("✅ All critical monitoring modules imported successfully!")
        logger.info("   Monitoring system ready for deployment")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
