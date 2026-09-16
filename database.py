import asyncpg



class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS films (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    genre TEXT,
                    year TEXT,
                    cost bigint,
                    description TEXT,
                    url TEXT
                    )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    phone TEXT,
                    balance BIGINT NOT NULL DEFAULT 0
                )
            """)

    async def add_film(self, title, genre, year, cost):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO films (title, genre, year, cost) VALUES ($1, $2, $3, $4)",
                title, genre, year, cost
            )

    async def find_film(self, genre: str):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT title,year,cost FROM films WHERE genre = $1",
                genre
            )
        return [f"{row['title']} | {row['year']} | {row['cost']}₽" for row in rows]

    async def select_film(self, title: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT title,year,cost,genre,description,url FROM films WHERE LOWER(title) = LOWER($1)",
                title
            )
        return row

    async def get_cost(self, title: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT cost from films where title = $1",
                title
            )
        return row

    async def get_profile(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, phone, balance  FROM contacts WHERE user_id = $1",
                user_id
            )
        return row

    async def add_contact(self, user_id: int, phone: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO contacts (user_id, phone) VALUES ($1, $2)",
                user_id, phone
            )

    async def get_phone(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT phone FROM contacts WHERE user_id = $1",
                user_id
            )
        return str(row) if row else None

    async def edit_phone(self, user_id: int, new_phone):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE contacts set phone = $2  WHERE user_id = $1",
                user_id, new_phone
            )
            
    async def is_registered(self, user_id: int) -> bool:
        """Проверяет, зарегистрирован ли пользователь"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM contacts WHERE user_id = $1",
                user_id
            )
        return row is not None
    
    async def get_balance(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT balance FROM contacts WHERE user_id = $1",
                user_id
            )
        return row if row else None
    
    async def change_balance(self, user_id: int, new_balance):
        async with self.pool.acquire() as conn:
            await conn.execute(
                    "UPDATE contacts set balance = $2  WHERE user_id = $1",
                    user_id, new_balance
                )