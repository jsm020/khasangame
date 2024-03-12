from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import asyncpg

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgresSQL ulanish malumotlari
DATABASE_URL = "postgres://telegram_bot_db_kehw_user:Sm9B8gp85QZr7EKCcUZuKY0hRWFxkfkL@dpg-cn9ik3ocmk4c73a09au0-a.oregon-postgres.render.com/telegram_bot_db_kehw"
# Asinxron funktsiya
async def connect_to_db():
    return await asyncpg.connect(DATABASE_URL)

# Asinxron funktsiya
async def close_connection_to_db(connection):
    await connection.close()

# # Lifespan event handler to create the users table
# @app.on_event("startup")
# async def create_users_table():
#     connection = await connect_to_db()
#     try:
#         create_table_query = """
#         CREATE TABLE users.users (
#             id SERIAL PRIMARY KEY,
#             telegram_id INT NOT NULL,
#             score INT NOT NULL
#         )

#         """
#         await connection.execute(create_table_query)
#     finally:
#         await close_connection_to_db(connection)

# Post qo'shish
@app.post("/users/")
async def create_user(telegram_id: int, score: int):
    connection = await connect_to_db()
    try:
        query = "INSERT INTO users.users (telegram_id, score) VALUES ($1, $2) RETURNING id"
        user_id = await connection.fetchval(query, telegram_id, score)
        return {"id": user_id, "telegram_id": telegram_id, "score": score}
    finally:
        await close_connection_to_db(connection)

# Barcha foydalanuvchilarni o'qish
@app.get("/users/")
async def read_users():
    connection = await connect_to_db()
    try:
        query = "SELECT id, telegram_id, score FROM users.users"
        rows = await connection.fetch(query)
        return [{"id": row[0], "telegram_id": row[1], "score": row[2]} for row in rows]
    finally:
        await close_connection_to_db(connection)

# Foydalanuvchini yangilash
@app.put("/users/{user_id}/")
async def update_user(user_id: int, telegram_id: int, score: int):
    connection = await connect_to_db()
    try:
        query = "UPDATE users.users SET telegram_id = $1, score = $2 WHERE id = $3"
        await connection.execute(query, telegram_id, score, user_id)
        return {"id": user_id, "telegram_id": telegram_id, "score": score}
    finally:
        await close_connection_to_db(connection)

# Foydalanuvchini o'chirish
@app.delete("/users/{user_id}/")
async def delete_user(user_id: int):
    connection = await connect_to_db()
    try:
        query = "DELETE FROM users.users WHERE id = $1"
        await connection.execute(query, user_id)
        return {"message": "User deleted successfully"}
    finally:
        await close_connection_to_db(connection)
