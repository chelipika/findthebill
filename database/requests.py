from database.models import async_session
from database.models import User, Group, HomeName
from sqlalchemy import select, update, delete

async def set_home_name(tg_id, home_name):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(HomeName.home_name == home_name and HomeName.tg_id == tg_id))
        
        if not user:
            session.add(HomeName(tg_id=tg_id, home_name=home_name))
            await session.commit()

async def set_electricity_id(target_id, electricity_id):
    async with async_session() as session:
        stmt = select(HomeName).where(HomeName.id == target_id)
        result = await session.execute(stmt)
        home = result.scalar_one_or_none()

        if home:
            # 2. Modify the object (SQLAlchemy tracks this change automatically)
            home.elec_id = electricity_id
            
            # 3. Commit changes to save to DB
            await session.commit()
            return True
            
        return False

async def get_electricity_id(target_id):
    async with async_session() as session:
        return None
    
async def get_user_homes(tg_id: int):
    async with async_session() as session:
        stmt = select(HomeName).where(HomeName.tg_id == tg_id)
        result = await session.execute(stmt)
        homes = result.scalars().all() 
        return homes
    
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

async def set_homeList(tgId, homeName, elec_id, natural_gas_id, cold_water_id, garbage_id):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(HomeName.tg_id == tgId))
        if not user:
            session.add(HomeName(tg_id=tgId,home_name=homeName, elec_id=elec_id, natural_gas_id=natural_gas_id, cold_water_id=cold_water_id, garbage_id=garbage_id))
            await session.commit()
    
async def set_elec_id(elec_id, targetId):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(User.id == targetId))
        user.elec_id = elec_id
        await session.commit()

async def set_natural_gas_id(natural_gas_id, targetId):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(User.id == targetId))
        user.natural_gas_id = natural_gas_id
        await session.commit()

async def set_cold_water_id(cold_water_id, targetId):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(User.id == targetId))
        user.cold_water_id = cold_water_id
        await session.commit()

async def set_elec_id(garbage_id, targetId):
    async with async_session() as session:
        user = await session.scalar(select(HomeName).where(User.id == targetId))
        user.garbage_id = garbage_id
        await session.commit()

async def set_user_auth_token(userAuthToken, tgId):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tgId))
        user.auth_token = userAuthToken
        await session.commit()

async def get_user_auth_token(tgId):
    async with async_session() as session:
        stmt = select(User.auth_token).where(User.tg_id == tgId)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
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