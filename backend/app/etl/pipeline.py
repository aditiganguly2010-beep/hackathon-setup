"""
ETL Pipeline for ingesting and processing legacy system data.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.etl.log_parser import LogParser
from app.etl.metric_parser import MetricParser
from app.etl.noise_filter import NoiseFilter
from app.models import SystemLog, PerformanceMetric
from app.core.logging import get_logger

logger = get_logger(__name__)


class ETLPipeline:
    """ETL pipeline for processing legacy system data."""
    
    def __init__(self):
        self.log_parser = LogParser()
        self.metric_parser = MetricParser()
        self.noise_filter = NoiseFilter()
    
    def ingest_logs(
        self, 
        raw_logs: List[str], 
        source_system: str,
        db: Session,
        batch_size: int = 100
    ) -> int:
        """
        Ingest and process raw log data.
        
        Args:
            raw_logs: List of raw log strings
            source_system: Source system identifier
            db: Database session
            batch_size: Number of logs to insert per batch
            
        Returns:
            Number of logs successfully ingested
        """
        logger.info(f"Starting log ingestion for {source_system}", extra_data={
            "log_count": len(raw_logs)
        })
        
        # Parse logs
        parsed_logs = []
        for raw_log in raw_logs:
            try:
                parsed_log = self.log_parser.parse_log(raw_log, source_system)
                parsed_logs.append(parsed_log)
            except Exception as e:
                logger.error("Error parsing log", extra_data={"error": str(e)})
                continue
        
        # Filter noise
        filtered_logs = self.noise_filter.filter_logs(parsed_logs)
        
        # Convert to database models
        log_models = []
        for log_data in filtered_logs:
            try:
                log_model = SystemLog(
                    source_system=log_data['source_system'],
                    log_level=log_data['log_level'],
                    message=log_data['message'],
                    timestamp=log_data['timestamp'],
                    raw_data=log_data.get('raw_data'),
                    normalized_data=log_data.get('normalized_data'),
                    metadata=log_data.get('metadata')
                )
                log_models.append(log_model)
            except Exception as e:
                logger.error("Error creating log model", extra_data={"error": str(e)})
                continue
        
        # Insert in batches
        ingested_count = 0
        for i in range(0, len(log_models), batch_size):
            batch = log_models[i:i + batch_size]
            try:
                db.bulk_save_objects(batch)
                db.commit()
                ingested_count += len(batch)
                logger.debug(f"Inserted batch of {len(batch)} logs")
            except Exception as e:
                db.rollback()
                logger.error("Error inserting log batch", extra_data={"error": str(e)})
                continue
        
        logger.info(f"Log ingestion completed: {ingested_count}/{len(raw_logs)} logs ingested")
        
        return ingested_count
    
    def ingest_metrics(
        self, 
        raw_metrics: List[str], 
        source_system: str,
        db: Session,
        batch_size: int = 100
    ) -> int:
        """
        Ingest and process raw metric data.
        
        Args:
            raw_metrics: List of raw metric strings
            source_system: Source system identifier
            db: Database session
            batch_size: Number of metrics to insert per batch
            
        Returns:
            Number of metrics successfully ingested
        """
        logger.info(f"Starting metric ingestion for {source_system}", extra_data={
            "metric_count": len(raw_metrics)
        })
        
        # Parse metrics
        parsed_metrics = []
        for raw_metric in raw_metrics:
            try:
                parsed_metric = self.metric_parser.parse_metric(raw_metric, source_system)
                parsed_metrics.append(parsed_metric)
            except Exception as e:
                logger.error("Error parsing metric", extra_data={"error": str(e)})
                continue
        
        # Filter noise
        filtered_metrics = self.noise_filter.filter_metrics(parsed_metrics)
        
        # Convert to database models
        metric_models = []
        for metric_data in filtered_metrics:
            try:
                metric_model = PerformanceMetric(
                    source_system=metric_data['source_system'],
                    metric_type=metric_data['metric_type'],
                    metric_value=metric_data['metric_value'],
                    unit=metric_data.get('unit'),
                    timestamp=metric_data['timestamp'],
                    raw_data=metric_data.get('raw_data'),
                    normalized_data=metric_data.get('normalized_data'),
                    metadata=metric_data.get('metadata')
                )
                metric_models.append(metric_model)
            except Exception as e:
                logger.error("Error creating metric model", extra_data={"error": str(e)})
                continue
        
        # Insert in batches
        ingested_count = 0
        for i in range(0, len(metric_models), batch_size):
            batch = metric_models[i:i + batch_size]
            try:
                db.bulk_save_objects(batch)
                db.commit()
                ingested_count += len(batch)
                logger.debug(f"Inserted batch of {len(batch)} metrics")
            except Exception as e:
                db.rollback()
                logger.error("Error inserting metric batch", extra_data={"error": str(e)})
                continue
        
        logger.info(f"Metric ingestion completed: {ingested_count}/{len(raw_metrics)} metrics ingested")
        
        return ingested_count
    
    def ingest_from_file(
        self,
        file_path: str,
        source_system: str,
        data_type: str,
        db: Session
    ) -> int:
        """
        Ingest data from a file.
        
        Args:
            file_path: Path to the file
            source_system: Source system identifier
            data_type: Type of data ('logs' or 'metrics')
            db: Database session
            
        Returns:
            Number of records successfully ingested
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Remove empty lines and strip whitespace
            lines = [line.strip() for line in lines if line.strip()]
            
            if data_type == 'logs':
                return self.ingest_logs(lines, source_system, db)
            elif data_type == 'metrics':
                return self.ingest_metrics(lines, source_system, db)
            else:
                logger.error("Unknown data type", extra_data={"data_type": data_type})
                return 0
                
        except Exception as e:
            logger.error("Error reading file", extra_data={
                "error": str(e),
                "file_path": file_path
            })
            return 0
