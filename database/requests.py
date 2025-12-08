from database.models import async_session
from database.models import User, Group, HomeName, ElectricityID
from sqlalchemy import select, update, delete

async def set_home_name(tg_id, home_name):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(HomeName.home_name == home_name and HomeName.tg_id == tg_id))
        
        if not user:
            session.add(HomeName(tg_id=tg_id, home_name=home_name))
            await session.commit()


async def set_electricity_id(home_name, electricity_id):
    async with async_session() as session:
        user = await session.scalar(select(ElectricityID).where(ElectricityID.electricity_id == electricity_id and ElectricityID.home_name == home_name))
        
        if not user:
            session.add(ElectricityID(home_name=home_name, electricity_id=electricity_id))
            await session.commit()

async def get_electricity_id(home_name):
    async with async_session() as session:
        result = await session.execute(select(ElectricityID.electricity_id).where(ElectricityID.home_name == home_name))
        user_ids = result.scalars().first()
        return user_ids
    
async def get_home_name(tg_id):
    async with async_session() as session:
        result = await session.execute(select(HomeName.home_name).where(HomeName.tg_id == tg_id))
        user_ids = result.scalars()
        return user_ids
    
async def get_all_home_names():
    async with async_session() as session:
        result = await session.execute(select(HomeName.home_name))
        home_names = result.scalars().all()  # Returns a list of home_name values
        return home_names

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_all_user_ids():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        user_ids = result.scalars().all()  # Returns a list of tg_id values
        return user_ids


async def set_group(group_id):
    async with async_session() as session:
        user = await session.scalar(select(Group).where(Group.tg_id == group_id))

        if not user:
            session.add(Group(tg_id=group_id))
            await session.commit()


            
async def get_all_groups_ids():
    async with async_session() as session:
        result = await session.execute(select(Group.tg_id))
        user_ids = result.scalars().all()  # Returns a list of tg_id values
        return user_ids