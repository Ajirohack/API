"""
Alembic migration for Human Simulator plugin: create admissions and calendar tables.
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Admissions table
    op.create_table(
        'admissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('applicant_name', sa.String(128), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, default='pending'),
        sa.Column('submitted_at', sa.DateTime, server_default=sa.func.now()),
    )
    # Calendar events
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_name', sa.String(128), nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('calendar_events')
    op.drop_table('admissions')
