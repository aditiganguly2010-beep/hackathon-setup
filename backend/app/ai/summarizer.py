"""
Natural language summarization system using Google ADK.
Synthesizes preprocessed log/metric data into natural language summaries.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import SystemLog, PerformanceMetric, Anomaly, HealthScore
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenAISummarizer:
    """Generate AI-powered summaries of system status."""
    
    def __init__(self):
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from external storage."""
        # In production, these would be loaded from a database or file
        return {
            "system_summary": """
You are a system health monitoring AI assistant. Analyze the following system data and provide a concise summary.

System: {source_system}
Time Period: {time_period}

Performance Metrics:
{metrics_summary}

Recent Anomalies:
{anomalies_summary}

Health Score: {health_score}/100
Trend: {trend}

Provide a natural language summary (2-3 paragraphs) that:
1. Describes the current system status
2. Highlights any critical issues or anomalies
3. Identifies patterns or trends
4. Mentions any areas requiring attention

Format your response as JSON with this schema:
{{
    "summary": "Your summary text here",
    "status": "healthy|degraded|critical",
    "key_issues": ["issue1", "issue2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}
""",
            "maintenance_actions": """
You are a system maintenance advisor. Based on the following system data, generate prioritized maintenance actions.

System: {source_system}
Current Anomalies:
{anomalies_summary}

Performance Metrics:
{metrics_summary}

Generate 3-5 prioritized maintenance actions. For each action, provide:
- Action type (Restart, Cleanup, Update, Investigate, Patch)
- Priority (1=highest, 5=lowest)
- Title
- Description
- Estimated effort

Format your response as JSON with this schema:
{{
    "actions": [
        {{
            "action_type": "Restart",
            "priority": 1,
            "title": "Action title",
            "description": "Detailed description",
            "estimated_effort": "30 minutes"
        }}
    ]
}}
"""
        }
    
    def generate_system_summary(
        self,
        source_system: str,
        db: Session,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate a natural language summary of system status.
        
        Args:
            source_system: Source system identifier
            db: Database session
            hours: Number of hours to consider
            
        Returns:
            Dictionary with summary and metadata
        """
        logger.info(f"Generating system summary for {source_system}")
        
        # Gather data
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.source_system == source_system,
            PerformanceMetric.timestamp >= cutoff_time
        ).all()
        
        anomalies = db.query(Anomaly).filter(
            Anomaly.source_system == source_system,
            Anomaly.detected_at >= cutoff_time
        ).order_by(Anomaly.detected_at.desc()).limit(10).all()
        
        health_score = db.query(HealthScore).filter(
            HealthScore.source_system == source_system
            ).order_by(HealthScore.calculated_at.desc()).first()
        
        # Prepare summaries
        metrics_summary = self._summarize_metrics(metrics)
        anomalies_summary = self._summarize_anomalies(anomalies)
        
        if health_score:
            health_score_value = health_score.overall_score
            trend = health_score.trend or "Unknown"
        else:
            health_score_value = 50
            trend = "Unknown"
        
        # Build prompt
        prompt = self.prompts["system_summary"].format(
            source_system=source_system,
            time_period=f"Last {hours} hours",
            metrics_summary=metrics_summary,
            anomalies_summary=anomalies_summary,
            health_score=health_score_value,
            trend=trend
        )
        
        # Call LLM (placeholder for Google ADK integration)
        try:
            llm_response = self._call_llm(prompt, "system_summary")
            
            # Parse response
            response_data = json.loads(llm_response)
            
            logger.info(f"Generated summary for {source_system}", extra_data={
                "status": response_data.get("status")
            })
            
            return {
                "source_system": source_system,
                "generated_at": datetime.utcnow(),
                "summary": response_data.get("summary"),
                "status": response_data.get("status"),
                "key_issues": response_data.get("key_issues", []),
                "recommendations": response_data.get("recommendations", []),
                "health_score": health_score_value,
                "trend": trend
            }
            
        except Exception as e:
            logger.error("Error generating system summary", extra_data={"error": str(e)})
            # Return fallback summary
            return self._generate_fallback_summary(
                source_system,
                metrics_summary,
                anomalies_summary,
                health_score_value,
                trend
            )
    
    def generate_maintenance_actions(
        self,
        source_system: str,
        db: Session,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized maintenance actions based on system data.
        
        Args:
            source_system: Source system identifier
            db: Database session
            hours: Number of hours to consider
            
        Returns:
            List of maintenance action dictionaries
        """
        logger.info(f"Generating maintenance actions for {source_system}")
        
        # Gather data
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        anomalies = db.query(Anomaly).filter(
            Anomaly.source_system == source_system,
            Anomaly.detected_at >= cutoff_time
        ).order_by(Anomaly.detected_at.desc()).all()
        
        metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.source_system == source_system,
            PerformanceMetric.timestamp >= cutoff_time
        ).all()
        
        # Prepare summaries
        anomalies_summary = self._summarize_anomalies(anomalies)
        metrics_summary = self._summarize_metrics(metrics)
        
        # Build prompt
        prompt = self.prompts["maintenance_actions"].format(
            source_system=source_system,
            anomalies_summary=anomalies_summary,
            metrics_summary=metrics_summary
        )
        
        # Call LLM (placeholder for Google ADK integration)
        try:
            llm_response = self._call_llm(prompt, "maintenance_actions")
            
            # Parse response
            response_data = json.loads(llm_response)
            
            actions = response_data.get("actions", [])
            
            logger.info(f"Generated {len(actions)} maintenance actions for {source_system}")
            
            return actions
            
        except Exception as e:
            logger.error("Error generating maintenance actions", extra_data={"error": str(e)})
            # Return fallback actions
            return self._generate_fallback_actions(source_system, anomalies)
    
    def _summarize_metrics(self, metrics: List[PerformanceMetric]) -> str:
        """Summarize performance metrics for the prompt."""
        if not metrics:
            return "No metrics available."
        
        # Group by type
        metrics_by_type = {}
        for metric in metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        summary_parts = []
        for metric_type, type_metrics in metrics_by_type.items():
            values = [m.metric_value for m in type_metrics]
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            unit = type_metrics[0].unit or ""
            
            summary_parts.append(
                f"- {metric_type}: Average {avg_value:.1f}{unit}, "
                f"Range: {min_value:.1f}-{max_value:.1f}{unit}"
            )
        
        return "\n".join(summary_parts)
    
    def _summarize_anomalies(self, anomalies: List[Anomaly]) -> str:
        """Summarize anomalies for the prompt."""
        if not anomalies:
            return "No anomalies detected."
        
        summary_parts = []
        for anomaly in anomalies[:10]:  # Limit to 10 most recent
            summary_parts.append(
                f"- {anomaly.anomaly_type} ({anomaly.severity}): "
                f"{anomaly.description[:100]}... "
                f"Confidence: {anomaly.confidence_score:.2f}"
            )
        
        return "\n".join(summary_parts)
    
    def _call_llm(self, prompt: str, prompt_type: str) -> str:
        """
        Call the LLM using Google ADK.
        This is a placeholder - actual implementation will use Google ADK.
        """
        # TODO: Implement Google ADK integration
        # For now, return a mock response
        
        if prompt_type == "system_summary":
            return json.dumps({
                "summary": "System is operating within normal parameters. No critical issues detected. Performance metrics show stable trends across CPU, memory, and disk usage. Minor anomalies have been detected but are within acceptable thresholds.",
                "status": "healthy",
                "key_issues": [],
                "recommendations": ["Continue monitoring", "Schedule routine maintenance"]
            })
        elif prompt_type == "maintenance_actions":
            return json.dumps({
                "actions": [
                    {
                        "action_type": "Investigate",
                        "priority": 3,
                        "title": "Review recent anomalies",
                        "description": "Investigate the minor anomalies detected in the system logs to determine root cause.",
                        "estimated_effort": "1 hour"
                    },
                    {
                        "action_type": "Cleanup",
                        "priority": 4,
                        "title": "Log cleanup",
                        "description": "Archive old log files to free up disk space.",
                        "estimated_effort": "30 minutes"
                    }
                ]
            })
        
        return "{}"
    
    def _generate_fallback_summary(
        self,
        source_system: str,
        metrics_summary: str,
        anomalies_summary: str,
        health_score: int,
        trend: str
    ) -> Dict[str, Any]:
        """Generate a fallback summary when LLM fails."""
        if health_score >= 80:
            status = "healthy"
            summary = f"{source_system} is operating normally. Performance metrics are within acceptable ranges. No critical issues detected."
        elif health_score >= 60:
            status = "degraded"
            summary = f"{source_system} is experiencing some degradation. Performance metrics show elevated values. Review anomalies for details."
        else:
            status = "critical"
            summary = f"{source_system} is in a critical state. Multiple anomalies detected. Immediate attention required."
        
        return {
            "source_system": source_system,
            "generated_at": datetime.utcnow(),
            "summary": summary,
            "status": status,
            "key_issues": [],
            "recommendations": ["Review system metrics", "Address detected anomalies"],
            "health_score": health_score,
            "trend": trend
        }
    
    def _generate_fallback_actions(
        self,
        source_system: str,
        anomalies: List[Anomaly]
    ) -> List[Dict[str, Any]]:
        """Generate fallback maintenance actions when LLM fails."""
        actions = []
        
        # Generate actions based on anomalies
        for anomaly in anomalies[:5]:
            if anomaly.severity == "Critical":
                actions.append({
                    "action_type": "Investigate",
                    "priority": 1,
                    "title": f"Address {anomaly.anomaly_type}",
                    "description": anomaly.description,
                    "estimated_effort": "2 hours"
                })
            elif anomaly.severity == "High":
                actions.append({
                    "action_type": "Investigate",
                    "priority": 2,
                    "title": f"Review {anomaly.anomaly_type}",
                    "description": anomaly.description,
                    "estimated_effort": "1 hour"
                })
        
        # Add default actions if none generated
        if not actions:
            actions.append({
                "action_type": "Investigate",
                "priority": 3,
                "title": "Routine system review",
                "description": "Perform routine review of system metrics and logs.",
                "estimated_effort": "1 hour"
            })
        
        return actions
