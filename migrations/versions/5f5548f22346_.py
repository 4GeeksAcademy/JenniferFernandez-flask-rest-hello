"""empty message

Revision ID: 5f5548f22346
Revises: a3fd498ec6fa
Create Date: 2025-02-21 10:46:55.396969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5548f22346'
down_revision = 'a3fd498ec6fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites_people', schema=None) as batch_op:
        batch_op.drop_column('name')

    with op.batch_alter_table('favorites_planets', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites_planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))

    with op.batch_alter_table('favorites_people', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
