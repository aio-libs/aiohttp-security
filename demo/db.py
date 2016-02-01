import sqlalchemy as sa


metadata = sa.MetaData()


users = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('login', sa.String(256), nullable=False),
    sa.Column('passwd', sa.String(256), nullable=False),
    sa.Column('salt', sa.String(256), nullable=False),
    sa.Column('is_superuser', sa.Boolean, nullable=False,
              server_default='FALSE'),
    sa.Column('disabled', sa.Boolean, nullable=False,
              server_default='FALSE'),

    # indices
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('login', name='user_login_key'),
)


permissions = sa.Table(
    'permissions', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('user_id', sa.Integer, nullable=False),
    sa.Column('perm_name', sa.String(64), nullable=False),

    # indices
    sa.PrimaryKeyConstraint('id', name='permission_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [users.c.id],
                            name='user_permission_fkey',
                            ondelete='CASCADE'),
)
