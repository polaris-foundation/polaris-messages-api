"""empty message

Revision ID: aeb985d9f8a0
Revises: 7aec9ea0094d
Create Date: 2018-04-04 09:54:03.816884

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'aeb985d9f8a0'
down_revision = '7aec9ea0094d'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        insert into message_type (uuid, created, modified, value)
        values ('DHOS-MESSAGES-ALERT', NOW(), NOW(), 7)
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
        DELETE FROM message_type WHERE UUID = 'DHOS-MESSAGES-ALERT'
    """)
