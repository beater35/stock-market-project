"""Add transaction_amount, broker_commission_rate, and sebon_fee_rate to transactions

Revision ID: f7d7af7f80ba
Revises: 6e28e358051f
Create Date: 2024-10-18 02:15:19.894894

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f7d7af7f80ba'
down_revision = '6e28e358051f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('transactions', sa.Column('transaction_amount', sa.Numeric(10, 2), nullable=False))
    op.add_column('transactions', sa.Column('broker_commission_rate', sa.Numeric(5, 3), nullable=False))
    op.add_column('transactions', sa.Column('sebon_fee_rate', sa.Numeric(5, 3), nullable=False))
    op.add_column('transactions', sa.Column('total_amount_paid', sa.Numeric(10, 2), nullable=True))
    op.add_column('transactions', sa.Column('total_amount_received', sa.Numeric(10, 2), nullable=True))
    op.add_column('transactions', sa.Column('profit_or_loss', sa.Numeric(10, 2), nullable=True))

def downgrade():
    op.drop_column('transactions', 'transaction_amount')
    op.drop_column('transactions', 'broker_commission_rate')
    op.drop_column('transactions', 'sebon_fee_rate')
    op.drop_column('transactions', 'total_amount_paid')
    op.drop_column('transactions', 'total_amount_received')
    op.drop_column('transactions', 'profit_or_loss')
