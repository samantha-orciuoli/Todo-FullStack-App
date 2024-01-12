"""empty message

Revision ID: afb9a6e6b5c7
Revises: 
Create Date: 2023-12-21 15:31:53.359964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afb9a6e6b5c7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completed', sa.Boolean(), nullable=True)) # changed nullable=True to add column to existing data that automatically sets to null
    op.execute('UPDATE todos SET completed = False WHERE completed IS NULL;') # upgrading existing data to have complete value equal to false
    op.alter_column('todos','completed', nullable =False) # updates column to set nullable contraint back to false

    


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.drop_column('completed')

    # ### end Alembic commands ###
