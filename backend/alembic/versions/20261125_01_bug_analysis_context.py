"""Create durable multi-agent intake context handoff.

Revision ID: 20261125_01
Revises:
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = "20261125_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bug_analysis_contexts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("submission_id", sa.String(length=36), sa.ForeignKey("bug_submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schema_version", sa.String(length=16), nullable=False, server_default="1.0"),
        sa.Column("orchestration_status", sa.String(length=24), nullable=False, server_default="completed"),
        sa.Column("triage_status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("log_analysis_status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("triage_output", sa.JSON(), nullable=True),
        sa.Column("log_analysis_output", sa.JSON(), nullable=True),
        sa.Column("combined_context", sa.JSON(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_bug_analysis_contexts_submission_id", "bug_analysis_contexts", ["submission_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_bug_analysis_contexts_submission_id", table_name="bug_analysis_contexts")
    op.drop_table("bug_analysis_contexts")
