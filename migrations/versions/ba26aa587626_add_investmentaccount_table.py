"""Add InvestmentAccount table

Revision ID: ba26aa587626
Revises: 55dd7a65f7f8
Create Date: 2019-10-05 22:29:01.129375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba26aa587626'
down_revision = '55dd7a65f7f8'
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
    op.add_column('stock_transaction', sa.Column('account_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'stock_transaction', 'investment_account', ['account_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'stock_transaction', type_='foreignkey')
    op.drop_column('stock_transaction', 'account_id')
    op.drop_table('investment_account')
    # ### end Alembic commands ###
