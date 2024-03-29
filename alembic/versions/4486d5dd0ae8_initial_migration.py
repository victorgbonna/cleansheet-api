"""Initial migration

Revision ID: 4486d5dd0ae8
Revises: 
Create Date: 2024-02-09 11:51:23.005598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4486d5dd0ae8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seasons', sa.Column('csvFileLink', sa.String(), nullable=True))
    op.drop_index('ix_seasons_league', table_name='seasons')
    op.drop_index('ix_seasons_year', table_name='seasons')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_seasons_year', 'seasons', ['year'], unique=False)
    op.create_index('ix_seasons_league', 'seasons', ['league'], unique=False)
    op.drop_column('seasons', 'csvFileLink')
    # ### end Alembic commands ###
