"""added nicknames

Revision ID: 762df889f42f
Revises: 829631f2c5d5
Create Date: 2018-08-03 18:10:37.582401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '762df889f42f'
down_revision = '829631f2c5d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('nickname', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_user_nickname'), 'user', ['nickname'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_nickname'), table_name='user')
    op.drop_column('user', 'nickname')
    # ### end Alembic commands ###
