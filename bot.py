import asyncio
import logging
from loader import BOT_TOKEN
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from test import generate_result

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class YOLOModel:
    model_yolo = None


async def create_start_keyboard():
    buttons = [
        [InlineKeyboardButton(text='Детекция на фото', callback_data="test_photo"),
         InlineKeyboardButton(text='Детекция на видео', callback_data="test_video")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = await create_start_keyboard()
    await message.answer(text=f"Привет, {message.from_user.username}!\n"
                              f"Чтобы воспользоваться ботом, тебе нужно передать мне фото/видео\n"
                              f"В ответном сообщении ты получишь детектированную и классифицированную одежду!\n"
                              f"Старайся отправлять такие фото/видео, в которых будет минимум других людей возле "
                              f"тебя, результат в таком случае будет наилучшим!",
                         reply_markup=keyboard, parse_mode="markdown")


router = Router()


class TestPhotoStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_video = State()


@router.callback_query(F.data == "test_photo")
async def handle_test_photo_callback(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Теперь отправьте мне фото.")
    await state.set_state(TestPhotoStates.waiting_for_photo)


@router.message(TestPhotoStates.waiting_for_photo, F.photo)
async def send_user_photo_result(msg: Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    image_path = f'images/{file_id}.jpg'

    await bot.download_file(file_path, destination=image_path)

    new_image_path = generate_result(image_path)
    photo = FSInputFile(path=new_image_path, filename='generated_result.jpg')
    keyboard = await create_start_keyboard()
    await msg.answer_photo(photo, caption='Вот результат', reply_markup=keyboard)

    await state.clear()


@router.callback_query(F.data == "test_video")
async def handle_test_video(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Теперь отправьте мне видео.")
    await state.set_state(TestPhotoStates.waiting_for_video)


@router.message(TestPhotoStates.waiting_for_video, F.video)
async def send_user_result(msg: Message, state: FSMContext):
    file_id = msg.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    video_path = f'videos/{file_id}.mp4'

    await bot.download_file(file_path, destination=video_path)

    new_video_path = generate_result(video_path)
    video = FSInputFile(path=new_video_path, filename='generated_result.mp4')
    keyboard = await create_start_keyboard()
    await msg.answer_video(video, caption='Вот результат', reply_markup=keyboard)

    await state.clear()


async def main():
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
