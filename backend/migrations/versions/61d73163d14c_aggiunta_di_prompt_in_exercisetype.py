"""Aggiunta di Prompt in ExerciseType

Revision ID: 61d73163d14c
Revises: 953974bc720f
Create Date: 2024-11-13 17:47:36.780368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61d73163d14c'
down_revision = '953974bc720f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('exercise_type') as batch_op:
        batch_op.add_column(sa.Column('prompt', sa.Text(), nullable=False, server_default=''))

def downgrade():
    with op.batch_alter_table('exercise_type') as batch_op:
        batch_op.drop_column('prompt')


    # ### end Alembic commands ###
