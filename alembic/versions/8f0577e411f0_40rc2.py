"""upgrade to 4.0rc2

Revision ID: 8f0577e411f0
Revises: e3b50f666fbb
Create Date: 2016-10-13 13:42:05.605723

"""

# revision identifiers, used by Alembic.
revision = '8f0577e411f0'
down_revision = 'e3b50f666fbb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('imagedata',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('image', sa.Integer(), nullable=False),
                    sa.Column('fits_header', sa.String(), nullable=True),
                    sa.Column('fits_data', sa.LargeBinary(), nullable=True),
                    sa.ForeignKeyConstraint(['image'], ['image.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_imagedata_image'), 'imagedata', ['image'], unique=False)
    op.add_column('frequencyband', sa.Column('dataset', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_frequencyband_dataset'), 'frequencyband', ['dataset'], unique=False)
    op.create_foreign_key(None, 'frequencyband', 'dataset', ['dataset'], ['id'])
    op.drop_index('ix_varmetric_runcat', table_name='varmetric')
    op.create_index(op.f('ix_varmetric_runcat'), 'varmetric', ['runcat'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_varmetric_runcat'), table_name='varmetric')
    op.create_index('ix_varmetric_runcat', 'varmetric', ['runcat'], unique=False)
    op.drop_constraint(None, 'frequencyband', type_='foreignkey')
    op.drop_index(op.f('ix_frequencyband_dataset'), table_name='frequencyband')
    op.drop_column('frequencyband', 'dataset')
    op.drop_index(op.f('ix_imagedata_image'), table_name='imagedata')
    op.drop_table('imagedata')
