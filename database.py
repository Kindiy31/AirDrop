from sqlalchemy import create_engine, select, inspect, insert, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import *
import config

DATABASE_URL = f"mysql+aiomysql://{config.db.get('name')}:{config.db.get('password')}@{config.db.get('host')}/{config.db.get('db_name')}"


def generate_time_now():
    t_time = str(datetime.now())
    t_time = t_time.split(r'.')[0]
    return t_time


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


class Database:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=True, future=True)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def connect(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            return conn

    @staticmethod
    def create_all_tables(bind):
        Base.metadata.create_all(bind)

    async def execute(self, query, params=None):
        async with self.async_session() as session:
            async with session.begin():
                if params:
                    result = await session.execute(query, params)
                else:
                    result = await session.execute(query)
                data = result.all()
                return [row._mapping for row in data]

    async def execute_many(self, query, params_list):
        async with self.async_session() as session:
            async with session.begin():
                results = []
                for params in params_list:
                    result = await session.execute(query, params)
                    data = result.all()
                    results.append([row._mapping for row in data])
                return results

    async def insert(self, table, data):
        stmt = insert(table).values(data)
        async with self.engine.connect() as connection:
            result = await connection.execute(stmt)
            await connection.commit()
            return result.inserted_primary_key[0]

    async def add(self, model):
        async with self.engine.connect() as connection:
            async with self.async_session() as session:
                async with session.begin():
                    session.add(model)
            await connection.commit()

    async def commit(self):
        async with self.engine.connect() as connection:
            await connection.commit()

    async def update(self, table, data, where=None):
        stmt = update(table)
        if where:
            stmt = stmt.where(*where)
        stmt = stmt.values(data)
        async with self.engine.connect() as connection:
            result = await connection.execute(stmt)
            await connection.commit()
            return result.rowcount

    async def delete(self, table, where):
        stmt = delete(table).where(*where)
        async with self.engine.connect() as connection:
            result = await connection.execute(stmt)
            await connection.commit()
            return result.rowcount

    async def close(self):
        await self.engine.dispose()

    async def get_data(self, table, where=None, values=None, fetchall=True) -> list[Base] or Base or None:
        if values:
            query = select(*values).select_from(table)
        else:
            query = select(table)
        if where:
            query = query.where(*where)

        async with (self.async_session() as session):
            result = await session.execute(query)
            if fetchall:
                data = result.scalars()
                if data:
                    data = data.all()
                return data
            else:
                data = result.scalar()
                return data

    async def take_users(self, id_user: str or int = None) -> list[User] or User or None:
        users = await self.take_for_table(id_model=id_user, model=User)
        return users

    async def modify_balance(self, id_user: str or int, amount: int or float, operation: str) -> User or None:
        user = await self.take_users(id_user=id_user)
        if not user:
            return None
        else:
            user.balance = round(float(eval(f"{user.balance} {operation} {amount}")), 2)
            await self.update(
                table=User,
                data={User.balance: user.balance},
                where=[User.id == id_user]
            )
            return user

    async def take_items(self, id_item: int = None) -> list[Item] or Item or None:
        items = await self.take_for_table(id_model=id_item, model=Item)
        return items

    async def take_transactions(self, id_transaction: int = None) -> list[Transaction] or Transaction or None:
        transactions = await self.take_for_table(id_model=id_transaction, model=Transaction)
        return transactions


    async def take_purchases(self, id_purchase: int = None, id_user: int or str = None) -> list[Purchase] or Purchase or None:
        if id_user:
            purchases = await self.get_data(table=Purchase, where=[Purchase.user_id == id_user])
            return purchases
        purchases = await self.take_for_table(id_model=id_purchase, model=Purchase)
        return purchases

    async def register(self, message) -> bool:
        id_user = message.from_user.id
        user = await self.take_users(id_user=id_user)
        if not user:
            first_name = message.from_user.first_name
            username = message.from_user.username
            user = User(
                first_name=first_name,
                username=username,
                id=id_user
            )
            await self.add(user)
            return True
        else:
            return False

    async def add_item(self, name, description, price, image_url) -> Item:
        item = Item(
            name=name,
            description=description,
            price=price,
            image_url=image_url
        )
        await self.add(item)
        return item

    async def buy_item(self, id_user, id_item) -> Purchase:
        purchase = Purchase(
            user_id=id_user,
            item_id=id_item,
        )
        await self.add(purchase)
        return purchase

    async def take_for_table(self, id_model: int or str, model: Base) -> list[Base] or Base or None:
        if id_model:
            data = await self.get_data(table=model, fetchall=False, where=[model.id == int(id_model)])
        else:
            data = await self.get_data(table=model)
        return data

    async def set_language(self, language_code, id_user):
        await self.update(User, {User.language: language_code}, where=[User.id == id_user])

    async def set_email(self, email, id_user):
        await self.update(User, {User.email: email}, where=[User.id == id_user])

    async def create_transaction(self, transaction_type, user_id, item_id, amount, address, transaction_hash, status=None):
        transaction = Transaction(
            transaction_type=transaction_type,
            transaction_hash=transaction_hash,
            user_id=user_id,
            item_id=item_id,
            amount=amount,
            address=address
        )
        if transaction.transaction_type == 1:
            operation = '-'
            await self.modify_balance(id_user=user_id, amount=transaction.amount, operation=operation)
        if status:
            transaction.status = status
        await self.add(model=transaction)
        return transaction

    async def take_admins(self):
        admins = await self.get_data(table=User, where=[User.is_admin == 1])
        return admins

    async def modify_transaction(self, transaction, modify_type) -> Transaction:
        user_id = transaction.user_id
        if modify_type == "confirm":
            status = 2
            if transaction.transaction_type == 0:
                operation = '+'
                await self.modify_balance(id_user=user_id, amount=transaction.amount, operation=operation)
        elif modify_type == "cancel":
            status = 3
            if transaction.transaction_type == 1:
                operation = '+'
                await self.modify_balance(id_user=user_id, amount=transaction.amount, operation=operation)
        else:
            status = 1
        transaction.status = status
        await self.update(
            table=Transaction,
            data={Transaction.status: status},
            where=[Transaction.id == transaction.id]
        )
        return transaction
