"""'TgAuth'

Revision ID: 71f1b8a581b3
Revises: 1011b757d078
Create Date: 2021-03-23 05:25:46.860026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71f1b8a581b3'
down_revision = '1011b757d078'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tg_auth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tgUser_id', sa.Integer(), nullable=True),
    sa.Column('temp_password', sa.String(length=128), nullable=True),
    sa.Column('pass_timestamp', sa.DateTime(), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['tgUser_id'], ['tg_user.tg_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tg_auth_pass_timestamp'), 'tg_auth', ['pass_timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tg_auth_pass_timestamp'), table_name='tg_auth')
    op.drop_table('tg_auth')
    # ### end Alembic commands ###
