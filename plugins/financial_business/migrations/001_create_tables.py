"""
Alembic migration script for financial_business plugin: create complete schema.

This script creates all necessary tables for the Financial Business plugin including:
- accounts - For storing account information
- admin_users - For storing admin user information
- transactions - For storing transaction history
- audit_log - For tracking actions for compliance
- metrics - For storing performance metrics
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Create accounts table with comprehensive fields
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_number', sa.String(64), nullable=False, unique=True),
        sa.Column('balance', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('currency', sa.String(8), nullable=False, server_default='USD'),
        sa.Column('owner_id', sa.Integer, nullable=False),
        sa.Column('account_type', sa.String(32), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata', sa.JSON, nullable=True),
    )
    # Add indexes for frequent queries
    op.create_index('idx_accounts_owner', 'accounts', ['owner_id'])
    op.create_index('idx_accounts_status', 'accounts', ['status'])
    
    # Create admin_users table with comprehensive fields
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('role', sa.String(64), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('permissions', sa.JSON, nullable=True),
    )
    # Add indexes for frequent queries
    op.create_index('idx_admin_users_email', 'admin_users', ['email'])
    op.create_index('idx_admin_users_role', 'admin_users', ['role'])
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('transaction_ref', sa.String(64), nullable=False, unique=True),
        sa.Column('source_account_id', sa.Integer, nullable=True),
        sa.Column('destination_account_id', sa.Integer, nullable=True),
        sa.Column('amount', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('currency', sa.String(8), nullable=False),
        sa.Column('transaction_type', sa.String(32), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata', sa.JSON, nullable=True),
        # Foreign keys
        sa.ForeignKeyConstraint(['source_account_id'], ['accounts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['destination_account_id'], ['accounts.id'], ondelete='SET NULL'),
    )
    # Add indexes for frequent queries
    op.create_index('idx_transactions_source', 'transactions', ['source_account_id'])
    op.create_index('idx_transactions_destination', 'transactions', ['destination_account_id'])
    op.create_index('idx_transactions_created_at', 'transactions', ['created_at'])
    op.create_index('idx_transactions_status', 'transactions', ['status'])
    
    # Create audit_log table for compliance tracking
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('entity_type', sa.String(64), nullable=False),
        sa.Column('entity_id', sa.String(64), nullable=False),
        sa.Column('actor_id', sa.Integer, nullable=True),
        sa.Column('actor_type', sa.String(32), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(64), nullable=True),
        sa.Column('details', sa.JSON, nullable=True),
    )
    # Add indexes for audit queries
    op.create_index('idx_audit_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_timestamp', 'audit_log', ['timestamp'])
    op.create_index('idx_audit_action', 'audit_log', ['action'])

    # Create metrics table for performance tracking
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('metric_name', sa.String(128), nullable=False),
        sa.Column('metric_value', sa.Float, nullable=False),
        sa.Column('dimensions', sa.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expiry', sa.DateTime, nullable=True),
    )
    # Add indexes for metrics queries
    op.create_index('idx_metrics_name', 'metrics', ['metric_name'])
    op.create_index('idx_metrics_timestamp', 'metrics', ['timestamp'])
    op.create_unique_constraint('uq_metrics_name_dimensions', 'metrics', ['metric_name', 'dimensions'])

def downgrade():
    """Revert all schema changes"""
    op.drop_table('metrics')
    op.drop_table('audit_log')
    op.drop_table('transactions')
    op.drop_table('admin_users')
    op.drop_table('accounts')
