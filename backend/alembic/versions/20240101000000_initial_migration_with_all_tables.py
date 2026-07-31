"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create system_logs table
    op.create_table(
        'system_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('log_level', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('raw_data', sa.Text(), nullable=True),
        sa.Column('normalized_data', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
    op.create_index(op.f('ix_system_logs_source_system'), 'system_logs', ['source_system'], unique=False)
    op.create_index(op.f('ix_system_logs_log_level'), 'system_logs', ['log_level'], unique=False)
    op.create_index(op.f('ix_system_logs_timestamp'), 'system_logs', ['timestamp'], unique=False)
    
    # Create performance_metrics table
    op.create_table(
        'performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_metrics_id'), 'performance_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_performance_metrics_source_system'), 'performance_metrics', ['source_system'], unique=False)
    op.create_index(op.f('ix_performance_metrics_metric_type'), 'performance_metrics', ['metric_type'], unique=False)
    op.create_index(op.f('ix_performance_metrics_timestamp'), 'performance_metrics', ['timestamp'], unique=False)
    
    # Create incident_records table
    op.create_table(
        'incident_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.String(length=255), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id')
    )
    op.create_index(op.f('ix_incident_records_id'), 'incident_records', ['id'], unique=False)
    op.create_index(op.f('ix_incident_records_incident_id'), 'incident_records', ['incident_id'], unique=True)
    op.create_index(op.f('ix_incident_records_source_system'), 'incident_records', ['source_system'], unique=False)
    op.create_index(op.f('ix_incident_records_severity'), 'incident_records', ['severity'], unique=False)
    op.create_index(op.f('ix_incident_records_status'), 'incident_records', ['status'], unique=False)
    op.create_index(op.f('ix_incident_records_detected_at'), 'incident_records', ['detected_at'], unique=False)
    
    # Create anomalies table
    op.create_table(
        'anomalies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('anomaly_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('related_metrics', sa.Text(), nullable=True),
        sa.Column('related_logs', sa.Text(), nullable=True),
        sa.Column('is_false_positive', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('acknowledged', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_anomalies_id'), 'anomalies', ['id'], unique=False)
    op.create_index(op.f('ix_anomalies_source_system'), 'anomalies', ['source_system'], unique=False)
    op.create_index(op.f('ix_anomalies_anomaly_type'), 'anomalies', ['anomaly_type'], unique=False)
    op.create_index(op.f('ix_anomalies_severity'), 'anomalies', ['severity'], unique=False)
    op.create_index(op.f('ix_anomalies_detected_at'), 'anomalies', ['detected_at'], unique=False)
    
    # Create maintenance_actions table
    op.create_table(
        'maintenance_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('estimated_effort', sa.String(length=100), nullable=True),
        sa.Column('related_anomaly_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Pending'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['related_anomaly_id'], ['anomalies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_actions_id'), 'maintenance_actions', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_actions_source_system'), 'maintenance_actions', ['source_system'], unique=False)
    op.create_index(op.f('ix_maintenance_actions_priority'), 'maintenance_actions', ['priority'], unique=False)
    op.create_index(op.f('ix_maintenance_actions_status'), 'maintenance_actions', ['status'], unique=False)
    
    # Create health_scores table
    op.create_table(
        'health_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=255), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('cpu_score', sa.Integer(), nullable=True),
        sa.Column('memory_score', sa.Integer(), nullable=True),
        sa.Column('disk_score', sa.Integer(), nullable=True),
        sa.Column('network_score', sa.Integer(), nullable=True),
        sa.Column('log_anomaly_score', sa.Integer(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('trend', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_system')
    )
    op.create_index(op.f('ix_health_scores_id'), 'health_scores', ['id'], unique=False)
    op.create_index(op.f('ix_health_scores_source_system'), 'health_scores', ['source_system'], unique=True)
    op.create_index(op.f('ix_health_scores_calculated_at'), 'health_scores', ['calculated_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_health_scores_calculated_at'), table_name='health_scores')
    op.drop_index(op.f('ix_health_scores_source_system'), table_name='health_scores')
    op.drop_index(op.f('ix_health_scores_id'), table_name='health_scores')
    op.drop_table('health_scores')
    
    op.drop_index(op.f('ix_maintenance_actions_status'), table_name='maintenance_actions')
    op.drop_index(op.f('ix_maintenance_actions_priority'), table_name='maintenance_actions')
    op.drop_index(op.f('ix_maintenance_actions_source_system'), table_name='maintenance_actions')
    op.drop_index(op.f('ix_maintenance_actions_id'), table_name='maintenance_actions')
    op.drop_table('maintenance_actions')
    
    op.drop_index(op.f('ix_anomalies_detected_at'), table_name='anomalies')
    op.drop_index(op.f('ix_anomalies_severity'), table_name='anomalies')
    op.drop_index(op.f('ix_anomalies_anomaly_type'), table_name='anomalies')
    op.drop_index(op.f('ix_anomalies_source_system'), table_name='anomalies')
    op.drop_index(op.f('ix_anomalies_id'), table_name='anomalies')
    op.drop_table('anomalies')
    
    op.drop_index(op.f('ix_incident_records_detected_at'), table_name='incident_records')
    op.drop_index(op.f('ix_incident_records_status'), table_name='incident_records')
    op.drop_index(op.f('ix_incident_records_severity'), table_name='incident_records')
    op.drop_index(op.f('ix_incident_records_source_system'), table_name='incident_records')
    op.drop_index(op.f('ix_incident_records_incident_id'), table_name='incident_records')
    op.drop_index(op.f('ix_incident_records_id'), table_name='incident_records')
    op.drop_table('incident_records')
    
    op.drop_index(op.f('ix_performance_metrics_timestamp'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_metric_type'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_source_system'), table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_id'), table_name='performance_metrics')
    op.drop_table('performance_metrics')
    
    op.drop_index(op.f('ix_system_logs_timestamp'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_log_level'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_source_system'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_id'), table_name='system_logs')
    op.drop_table('system_logs')
