"""empty message

Revision ID: f77bbe0e5104
Revises: 81bceb8d4cc8
Create Date: 2018-04-13 17:24:57.458761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f77bbe0e5104'
down_revision = '81bceb8d4cc8'
branch_labels = None
depends_on = None


def upgrade():

    op.add_column('message', sa.Column('created_by_', sa.String(), nullable=False))
    op.add_column('message', sa.Column('modified_by_', sa.String(), nullable=False))
    op.add_column('message_type', sa.Column('created_by_', sa.String(), nullable=True, server_default='sys'))
    op.add_column('message_type', sa.Column('modified_by_', sa.String(), nullable=False, server_default='sys'))


def downgrade():

    op.drop_column('message_type', 'modified_by_')
    op.drop_column('message_type', 'created_by_')
    op.drop_column('message', 'modified_by_')
    op.drop_column('message', 'created_by_')
