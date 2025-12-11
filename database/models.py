from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Define the engine
engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")

# Define async session maker
async_session = async_sessionmaker(engine)

# Define base and models
class Base(DeclarativeBase):
    pass
class HomeName(Base):
    __tablename__ = "home_names"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    home_name = mapped_column(String)
    natural_gas_id = mapped_column(String)
    elec_id = mapped_column(String)
    cold_water_id = mapped_column(String)
    garbage_id = mapped_column(String)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    auth_token = mapped_column(String)

class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)