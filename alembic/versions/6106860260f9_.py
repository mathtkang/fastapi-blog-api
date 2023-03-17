"""empty message

Revision ID: 6106860260f9
Revises: b4ade7829125
Create Date: 2023-03-17 18:41:28.642827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6106860260f9'
down_revision = 'b4ade7829125'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('connect_post_hashtag', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('connect_post_hashtag', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('like', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('like', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('like', 'updated_at')
    op.drop_column('like', 'created_at')
    op.drop_column('connect_post_hashtag', 'updated_at')
    op.drop_column('connect_post_hashtag', 'created_at')
    # ### end Alembic commands ###