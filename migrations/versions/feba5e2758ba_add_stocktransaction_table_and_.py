"""Add StockTransaction table and Investment Account table

Revision ID: feba5e2758ba
Revises: 
Create Date: 2019-10-06 15:02:33.792857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'feba5e2758ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('investment_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('taxable', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stock_transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_type', sa.Enum('buy', 'sell', name='stocktransactiontype'), nullable=False),
    sa.Column('stock_symbol', sa.String(), nullable=False),
    sa.Column('cost_per_unit', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('trade_fee', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['investment_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stock_transaction')
    op.drop_table('investment_account')
    # ### end Alembic commands ###
