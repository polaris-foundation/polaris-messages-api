"""clear_alerts

Revision ID: f907f620abdc
Revises: e807f620ab5f
Create Date: 2021-01-21 16:42:05.751866

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f907f620abdc"
down_revision = "e807f620ab5f"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        insert into message_type (uuid, created, modified, value)
        values ('DHOS-MESSAGES-CLEAR-ALERTS', NOW(), NOW(), 10)
    """
    )


def downgrade():
    connection = op.get_bind()

    connection.execute(
        """
        DELETE FROM message_type WHERE UUID = 'DHOS-MESSAGES-CLEAR-ALERTS'
    """
    )
