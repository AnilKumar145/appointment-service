"""Create appointments table with status enum

Revision ID: 11a79f2c969c
Revises: 
Create Date: 2025-09-19 15:27:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '11a79f2c969c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create ENUM type for AppointmentStatus if it doesn't exist
    connection = op.get_bind()
    
    # Check if enum already exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'appointmentstatus'
        )
    """)).scalar()
    
    if not result:
        # Create enum only if it doesn't exist
        appointmentstatus_enum = postgresql.ENUM(
            'SCHEDULED', 
            'COMPLETED', 
            'CANCELLED', 
            'PENDING',
            name='appointmentstatus',
            create_type=True
        )
        appointmentstatus_enum.create(connection)
    
    # Create appointments table
    op.create_table('appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.String(), nullable=False),
        sa.Column('doctor_id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('facility_id', sa.String(), nullable=False),
        sa.Column('doctor_name', sa.String(), nullable=False),
        sa.Column('patient_name', sa.String(), nullable=False),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('appointment_start_time', sa.Time(), nullable=False),
        sa.Column('appointment_end_time', sa.Time(), nullable=False),
        sa.Column('purpose_of_visit', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('SCHEDULED', 'COMPLETED', 'CANCELLED', 'PENDING', name='appointmentstatus', create_type=False), nullable=False, server_default='SCHEDULED'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appointment_id')
    )
    
    # Create indexes
    op.create_index('ix_appointments_appointment_id', 'appointments', ['appointment_id'], unique=True)
    op.create_index('ix_appointments_doctor_id', 'appointments', ['doctor_id'], unique=False)
    op.create_index('ix_appointments_facility_id', 'appointments', ['facility_id'], unique=False)
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'], unique=False)

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_appointments_patient_id', table_name='appointments')
    op.drop_index('ix_appointments_facility_id', table_name='appointments')
    op.drop_index('ix_appointments_doctor_id', table_name='appointments')
    op.drop_index('ix_appointments_appointment_id', table_name='appointments')
    
    # Drop table
    op.drop_table('appointments')
    
    # Drop enum only if no other tables are using it
    connection = op.get_bind()
    try:
        connection.execute(sa.text('DROP TYPE appointmentstatus'))
    except Exception:
        # Ignore if enum is still being used elsewhere
        pass
