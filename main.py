from bot import tg_bot
from models import *
from fastapi import FastAPI
import asyncio
import uvicorn

app = FastAPI()
db = tg_bot.db


@app.get("/api/v1/balance/add")
async def read_root(request: BalanceAddRequest):
    response = await db.modify_balance(id_user=request.user_id, amount=request.amount, operation="+")
    if response:
        handler = tg_bot.HandlerUser(id_user=request.user_id)
        await handler.connect()
        await handler.add_balance(amount=request.amount)
    return response


async def run_fast_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    tasks = [asyncio.create_task(tg_bot.main()), asyncio.create_task(run_fast_api())]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
