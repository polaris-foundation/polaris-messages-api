"""remove_urgent_callback

Revision ID: de4a9a336b30
Revises: 87c5547f76b3
Create Date: 2018-06-11 13:52:19.553015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de4a9a336b30'
down_revision = '87c5547f76b3'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        UPDATE message SET message_type_id = '5' WHERE message_type_id = '4';
        DELETE FROM message_type WHERE value = 4;
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-CALLBACK' 
        WHERE uuid = 'DHOS-MESSAGES-URGENT-CALLBACK';
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-URGENT-CALLBACK'
        WHERE uuid = 'DHOS-MESSAGES-CALLBACK';
        INSERT INTO message_type (uuid, created, modified, value)
        VALUES ('DHOS-MESSAGES-CALLBACK', NOW(), NOW(), 4);
    """)
