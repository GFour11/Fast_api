"""user_update

Revision ID: 1c0041ae36c1
Revises: 1950595eb7ee
Create Date: 2023-08-06 20:49:30.736317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c0041ae36c1'
down_revision = '1950595eb7ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('access_token', sa.String(length=300), nullable=True))
    op.add_column('Users', sa.Column('refresh_token', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'refresh_token')
    op.drop_column('Users', 'access_token')
    # ### end Alembic commands ###
