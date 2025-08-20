import os
import subprocess
import zipfile
from aiogram import Bot, Dispatcher, executor, types

# Tera token
API_TOKEN = "8107067133:AAGBN2rFEx15F_wt5tnwGK0IJCz4U5BLTQM"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Folder to store hosted bots
HOST_DIR = "hosted_bots"
os.makedirs(HOST_DIR, exist_ok=True)

# Dictionary to store running processes
running_processes = {}

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("👋 Send me a `.py` or `.zip` file and I will host it 24/7 for you!")

@dp.message_handler(content_types=["document"])
async def handle_file(message: types.Message):
    file = message.document
    file_name = file.file_name

    if not (file_name.endswith(".py") or file_name.endswith(".zip")):
        await message.reply("❌ Only `.py` or `.zip` files are supported!")
        return

    file_path = os.path.join(HOST_DIR, file_name)

    # Download file
    await file.download(file_path)
    await message.reply("📥 File received. Setting up your bot...")

    bot_folder = os.path.join(HOST_DIR, file_name.split(".")[0])
    os.makedirs(bot_folder, exist_ok=True)

    if file_name.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(bot_folder)
        main_file = os.path.join(bot_folder, "main.py")
    else:
        main_file = os.path.join(bot_folder, file_name)
        os.rename(file_path, main_file)

    # Install requirements if exist
    req_file = os.path.join(bot_folder, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(["pip", "install", "-r", req_file])

    # Kill old process if running
    if message.from_user.id in running_processes:
        running_processes[message.from_user.id].kill()

    # Start bot in background
    process = subprocess.Popen(["python", main_file], cwd=bot_folder)
    running_processes[message.from_user.id] = process

    await message.reply("✅ Your bot is now hosted and running 24/7!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)