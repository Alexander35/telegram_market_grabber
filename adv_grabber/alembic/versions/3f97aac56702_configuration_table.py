"""configuration table

Revision ID: 3f97aac56702
Revises: dca5b06a2941
Create Date: 2024-05-22 16:21:07.865128

"""
from typing import Sequence, Union

import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3f97aac56702'
down_revision: Union[str, None] = 'dca5b06a2941'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configuration',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('telegram_grabber_api_id', sa.Integer(), nullable=True),
    sa.Column('telegram_grabber_api_hash', sa.String(), nullable=True),
    sa.Column('telegram_grabber_conf', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('configuration')
    # ### end Alembic commands ###