"""amber_alert

Revision ID: c7b4052bd405
Revises: 87c5547f76b3
Create Date: 2018-06-13 08:34:57.554339

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c7b4052bd405'
down_revision = 'de4a9a336b30'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        update message_type SET uuid='DHOS-MESSAGES-RED-ALERT'
        WHERE UUID = 'DHOS-MESSAGES-ALERT'
    """)
    connection.execute("""
        insert into message_type (uuid, created, modified, value)
        values ('DHOS-MESSAGES-AMBER-ALERT', NOW(), NOW(), 8)
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
        update message_type SET UUID='DHOS-MESSAGES-ALERT'
        WHERE UUID = 'DHOS-MESSAGES-RED-ALERT'
    """)
    connection.execute("""
        update message SET message_type_id='7'
        WHERE message_type_id = '8'
    """)
    connection.execute("""
        DELETE FROM message_type WHERE UUID = 'DHOS-MESSAGES-AMBER-ALERT'
    """)
