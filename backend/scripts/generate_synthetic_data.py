"""
Synthetic data generation script for the Legacy System Health Monitor.
Generates realistic legacy system logs, performance metrics, and incident records.
"""
import random
import json
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import (
    SystemLog,
    PerformanceMetric,
    IncidentRecord,
    Anomaly,
    MaintenanceAction,
    HealthScore
)
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)
fake = Faker()

# Configuration
SOURCE_SYSTEMS = ["legacy-crm", "legacy-erp", "legacy-inventory", "legacy-payroll", "legacy-hris"]
LOG_LEVELS = ["INFO", "WARNING", "ERROR", "CRITICAL"]
METRIC_TYPES = ["CPU", "Memory", "Disk", "Network"]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
ANOMALY_TYPES = ["Log Spike", "High Memory", "CPU Saturation", "Disk Space Low", "Network Latency"]
ACTION_TYPES = ["Restart", "Cleanup", "Update", "Investigate", "Patch"]
STATUSES = ["Pending", "In Progress", "Scheduled", "Completed"]


def generate_system_logs(num_logs: int = 1000) -> list:
    """Generate synthetic system logs."""
    logs = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_logs):
        # 80% normal logs, 20% error/critical logs
        if random.random() < 0.8:
            log_level = random.choice(["INFO", "WARNING"])
        else:
            log_level = random.choice(["ERROR", "CRITICAL"])
        
        source_system = random.choice(SOURCE_SYSTEMS)
        timestamp = base_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )
        
        # Generate realistic log messages
        if log_level == "INFO":
            message = fake.sentence()
        elif log_level == "WARNING":
            message = f"Warning: {fake.sentence()}"
        elif log_level == "ERROR":
            message = f"Error in module {fake.word()}: {fake.sentence()}"
        else:  # CRITICAL
            message = f"CRITICAL: System failure in {fake.word()} - {fake.sentence()}"
        
        # Create raw data (simulating various log formats)
        raw_data = json.dumps({
            "timestamp": timestamp.isoformat(),
            "level": log_level,
            "source": source_system,
            "message": message,
            "thread_id": random.randint(1000, 9999),
            "process_id": random.randint(100, 999)
        })
        
        # Create normalized data
        normalized_data = json.dumps({
            "timestamp": timestamp.isoformat(),
            "level": log_level,
            "source_system": source_system,
            "message": message,
            "severity": log_level
        })
        
        log = SystemLog(
            source_system=source_system,
            log_level=log_level,
            message=message,
            timestamp=timestamp,
            raw_data=raw_data,
            normalized_data=normalized_data,
            metadata=json.dumps({"generated": True})
        )
        logs.append(log)
    
    logger.info(f"Generated {num_logs} system logs")
    return logs


def generate_performance_metrics(num_metrics: int = 5000) -> list:
    """Generate synthetic performance metrics with anomalies."""
    metrics = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for source_system in SOURCE_SYSTEMS:
        for metric_type in METRIC_TYPES:
            # Generate time series data
            for i in range(num_metrics // len(SOURCE_SYSTEMS) // len(METRIC_TYPES)):
                timestamp = base_time + timedelta(
                    minutes=random.randint(0, 30 * 24 * 60)
                )
                
                # Generate metric values with occasional anomalies
                if random.random() < 0.05:  # 5% anomaly rate
                    # Inject statistical outliers
                    if metric_type == "CPU":
                        metric_value = random.uniform(85, 100)  # High CPU
                    elif metric_type == "Memory":
                        metric_value = random.uniform(85, 100)  # High Memory
                    elif metric_type == "Disk":
                        metric_value = random.uniform(90, 100)  # High Disk
                    else:  # Network
                        metric_value = random.uniform(500, 1000)  # High latency
                else:
                    # Normal values
                    if metric_type == "CPU":
                        metric_value = random.uniform(10, 60)
                    elif metric_type == "Memory":
                        metric_value = random.uniform(20, 70)
                    elif metric_type == "Disk":
                        metric_value = random.uniform(30, 80)
                    else:  # Network
                        metric_value = random.uniform(10, 100)
                
                unit = {
                    "CPU": "%",
                    "Memory": "%",
                    "Disk": "%",
                    "Network": "Mbps"
                }[metric_type]
                
                metric = PerformanceMetric(
                    source_system=source_system,
                    metric_type=metric_type,
                    metric_value=metric_value,
                    unit=unit,
                    timestamp=timestamp
                )
                metrics.append(metric)
    
    logger.info(f"Generated {len(metrics)} performance metrics")
    return metrics


def generate_incident_records(num_incidents: int = 50) -> list:
    """Generate synthetic incident records."""
    incidents = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_incidents):
        source_system = random.choice(SOURCE_SYSTEMS)
        severity = random.choices(SEVERITIES, weights=[0.1, 0.2, 0.4, 0.3])[0]
        detected_at = base_time + timedelta(
            days=random.randint(0, 30)
        )
        
        incident_id = f"INC-{fake.uuid4()[:8].upper()}"
        
        # Generate title and description based on severity
        if severity == "Critical":
            title = f"Critical system failure in {source_system}"
            description = f"System {source_system} experienced a critical failure requiring immediate attention."
        elif severity == "High":
            title = f"High severity issue in {source_system}"
            description = f"Significant degradation detected in {source_system}."
        elif severity == "Medium":
            title = f"Medium priority issue in {source_system}"
            description = f"Moderate issue detected in {source_system} requiring investigation."
        else:
            title = f"Low priority issue in {source_system}"
            description = f"Minor issue detected in {source_system}."
        
        # Randomly resolve some incidents
        status = random.choices(
            ["Open", "In Progress", "Resolved"],
            weights=[0.4, 0.3, 0.3]
        )[0]
        
        resolved_at = None
        if status == "Resolved":
            resolved_at = detected_at + timedelta(
                hours=random.randint(1, 48)
            )
        
        incident = IncidentRecord(
            incident_id=incident_id,
            source_system=source_system,
            severity=severity,
            title=title,
            description=description,
            status=status,
            detected_at=detected_at,
            resolved_at=resolved_at,
            root_cause=fake.sentence() if status == "Resolved" else None,
            resolution_notes=fake.paragraph() if status == "Resolved" else None
        )
        incidents.append(incident)
    
    logger.info(f"Generated {num_incidents} incident records")
    return incidents


def generate_anomalies(num_anomalies: int = 100) -> list:
    """Generate synthetic anomalies."""
    anomalies = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_anomalies):
        source_system = random.choice(SOURCE_SYSTEMS)
        anomaly_type = random.choice(ANOMALY_TYPES)
        severity = random.choices(SEVERITIES, weights=[0.15, 0.25, 0.35, 0.25])[0]
        detected_at = base_time + timedelta(
            days=random.randint(0, 30)
        )
        
        confidence_score = random.uniform(0.6, 0.99)
        
        description = f"{anomaly_type} detected in {source_system}. Confidence: {confidence_score:.2f}"
        
        anomaly = Anomaly(
            source_system=source_system,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence_score=confidence_score,
            description=description,
            detected_at=detected_at,
            related_metrics=json.dumps([random.randint(1, 100) for _ in range(random.randint(1, 5))]),
            related_logs=json.dumps([random.randint(1, 500) for _ in range(random.randint(1, 10))]),
            is_false_positive=random.choice([0, 1]),
            acknowledged=random.choice([0, 1])
        )
        anomalies.append(anomaly)
    
    logger.info(f"Generated {num_anomalies} anomalies")
    return anomalies


def generate_maintenance_actions(num_actions: int = 200) -> list:
    """Generate synthetic maintenance actions."""
    actions = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_actions):
        source_system = random.choice(SOURCE_SYSTEMS)
        action_type = random.choice(ACTION_TYPES)
        priority = random.randint(1, 5)
        status = random.choices(STATUSES, weights=[0.4, 0.2, 0.2, 0.2])[0]
        
        title = f"{action_type} {source_system}"
        description = f"Perform {action_type.lower()} operation on {source_system} to address identified issues."
        
        estimated_effort = random.choice(["30 minutes", "1 hour", "2 hours", "4 hours"])
        
        due_date = base_time + timedelta(days=random.randint(1, 14))
        
        completed_at = None
        if status == "Completed":
            completed_at = base_time + timedelta(days=random.randint(0, 7))
        
        action = MaintenanceAction(
            source_system=source_system,
            action_type=action_type,
            priority=priority,
            title=title,
            description=description,
            estimated_effort=estimated_effort,
            related_anomaly_id=random.randint(1, 100) if random.random() < 0.5 else None,
            status=status,
            due_date=due_date,
            completed_at=completed_at,
            notes=fake.sentence() if status == "Completed" else None
        )
        actions.append(action)
    
    logger.info(f"Generated {num_actions} maintenance actions")
    return actions


def generate_health_scores() -> list:
    """Generate health scores for each source system."""
    scores = []
    calculated_at = datetime.utcnow()
    
    for source_system in SOURCE_SYSTEMS:
        # Generate scores with some correlation
        base_score = random.randint(60, 95)
        cpu_score = base_score + random.randint(-10, 10)
        memory_score = base_score + random.randint(-10, 10)
        disk_score = base_score + random.randint(-10, 10)
        network_score = base_score + random.randint(-10, 10)
        log_anomaly_score = base_score + random.randint(-15, 15)
        
        # Calculate overall score
        overall_score = int((cpu_score + memory_score + disk_score + network_score + log_anomaly_score) / 5)
        overall_score = max(0, min(100, overall_score))
        
        # Determine trend
        if overall_score >= 80:
            trend = "Stable"
        elif overall_score >= 60:
            trend = random.choice(["Stable", "Degrading"])
        else:
            trend = "Degrading"
        
        score = HealthScore(
            source_system=source_system,
            overall_score=overall_score,
            cpu_score=max(0, min(100, cpu_score)),
            memory_score=max(0, min(100, memory_score)),
            disk_score=max(0, min(100, disk_score)),
            network_score=max(0, min(100, network_score)),
            log_anomaly_score=max(0, min(100, log_anomaly_score)),
            calculated_at=calculated_at,
            trend=trend
        )
        scores.append(score)
    
    logger.info(f"Generated health scores for {len(SOURCE_SYSTEMS)} systems")
    return scores


def main():
    """Main function to generate and insert synthetic data."""
    logger.info("Starting synthetic data generation")
    
    db = SessionLocal()
    try:
        # Generate all data
        logs = generate_system_logs(1000)
        metrics = generate_performance_metrics(5000)
        incidents = generate_incident_records(50)
        anomalies = generate_anomalies(100)
        actions = generate_maintenance_actions(200)
        scores = generate_health_scores()
        
        # Insert data in batches
        logger.info("Inserting data into database")
        
        db.bulk_save_objects(logs)
        db.bulk_save_objects(metrics)
        db.bulk_save_objects(incidents)
        db.bulk_save_objects(anomalies)
        db.bulk_save_objects(actions)
        db.bulk_save_objects(scores)
        
        db.commit()
        
        logger.info("Synthetic data generation completed successfully")
        logger.info(f"Inserted: {len(logs)} logs, {len(metrics)} metrics, {len(incidents)} incidents, "
                   f"{len(anomalies)} anomalies, {len(actions)} actions, {len(scores)} health scores")
        
    except Exception as e:
        db.rollback()
        logger.error("Error generating synthetic data", extra_data={"error": str(e)})
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
