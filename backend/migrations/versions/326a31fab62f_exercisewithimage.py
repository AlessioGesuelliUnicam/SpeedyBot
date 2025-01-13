"""ExerciseWithimage

Revision ID: 326a31fab62f
Revises: 
Create Date: 2024-11-10 19:30:04.364478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '326a31fab62f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exercise_whit_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=200), nullable=False),
    sa.Column('exercise_type', sa.String(length=100), nullable=False),
    sa.Column('description_it', sa.String(length=200), nullable=False),
    sa.Column('description_en', sa.String(length=200), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('exercise_whit_image')
    # ### end Alembic commands ###
