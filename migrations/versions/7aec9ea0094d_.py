"""empty message

Revision ID: 7aec9ea0094d
Revises: 5d997d38ea79
Create Date: 2018-03-21 15:36:05.969273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7aec9ea0094d'
down_revision = '5d997d38ea79'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        insert into message_type (uuid, created, modified, value) 
        values ('DHOS-MESSAGES-ACTIVATION-CODE', NOW(), NOW(), 6)
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-GENERAL' WHERE uuid = 'General'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-DOSAGE' WHERE uuid = 'Dosage'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-DIETARY' WHERE uuid = 'Dietary'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-CALLBACK' WHERE uuid = 'Callback'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-URGENT-CALLBACK'
        WHERE uuid = 'Urgent_Callback'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'DHOS-MESSAGES-FEEDBACK' WHERE uuid = 'Feedback'
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
        DELETE FROM message_type WHERE uuid= 'DHOS-MESSAGES-ACTIVATION-CODE'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'General' WHERE uuid = 'DHOS-MESSAGES-GENERAL'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'Dosage' WHERE uuid = 'DHOS-MESSAGES-DOSAGE'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'Dietary' WHERE uuid = 'DHOS-MESSAGES-DIETARY'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'Callback' WHERE uuid = 'DHOS-MESSAGES-CALLBACK'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'Urgent_Callback'
        WHERE uuid = 'DHOS-MESSAGES-URGENT-CALLBACK'
    """)
    connection.execute("""
        UPDATE message_type SET uuid = 'Feedback' WHERE uuid = 'DHOS-MESSAGES-FEEDBACK'
    """)
