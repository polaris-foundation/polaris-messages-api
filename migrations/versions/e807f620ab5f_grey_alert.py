"""grey_alert

Revision ID: e807f620ab5f
Revises: c7b4052bd405
Create Date: 2018-06-20 09:42:05.852266

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e807f620ab5f'
down_revision = 'c7b4052bd405'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        insert into message_type (uuid, created, modified, value)
        values ('DHOS-MESSAGES-GREY-ALERT', NOW(), NOW(), 9)
    """)


def downgrade():
    connection = op.get_bind()

    connection.execute("""
        DELETE FROM message_type WHERE UUID = 'DHOS-MESSAGES-GREY-ALERT'
    """)
