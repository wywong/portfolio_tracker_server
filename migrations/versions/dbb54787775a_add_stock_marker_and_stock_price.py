"""Add stock marker and stock price

Revision ID: dbb54787775a
Revises: cd0b2ace96a5
Create Date: 2019-10-26 13:15:28.631760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbb54787775a'
down_revision = 'cd0b2ace96a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock_marker',
    sa.Column('stock_symbol', sa.String(length=16), nullable=False),
    sa.Column('exists', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('stock_symbol')
    )
    op.create_table('stock_price',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_symbol', sa.String(length=16), nullable=False),
    sa.Column('price_date', sa.DateTime(), nullable=False),
    sa.Column('close_price', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stock_price')
    op.drop_table('stock_marker')
    # ### end Alembic commands ###
