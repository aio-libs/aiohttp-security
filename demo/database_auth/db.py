import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = sa.MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


class User(Base):
    """A user and their credentials."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(256), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String(256))
    is_superuser: Mapped[bool] = mapped_column(
        default=False, server_default=sa.sql.expression.false())
    disabled: Mapped[bool] = mapped_column(
        default=False, server_default=sa.sql.expression.false())
    permissions = relationship("Permission", cascade="all, delete")


class Permission(Base):
    """A permission that grants a user access to something."""

    __tablename__ = "permissions"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64), primary_key=True)
