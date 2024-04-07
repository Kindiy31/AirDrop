from bot import tg_bot


async def main():
    tasks = [tg_bot.main(),]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # запускаємо функцію main()
    import asyncio
    asyncio.run(main())
