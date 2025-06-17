import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BOT_TOKEN = "6556931752:AAET-aaZwdBg_tgQa4AJexUXZJr5xMgIQx4"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DOCTORS = {
    "therapist": "Терапевт",
    "dentist": "Стоматолог",
    "cardiologist": "Кардиолог",
    "neurologist": "Невролог",
    "ophthalmologist": "Офтальмолог"
}
AVAILABLE_TIMES = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
class AppointmentState(StatesGroup):
    waiting_for_fio = State()
    waiting_for_doctor = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_confirmation = State()
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Добро пожаловать в систему записи на прием.\n"
        "/appointment"
    )
    await state.clear()
@dp.message(Command("appointment"))
async def cmd_appointment(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше ФИО:")
    await state.set_state(AppointmentState.waiting_for_fio)
@dp.message(AppointmentState.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    if len(message.text.split()) < 2:
        await message.answer("Пожалуйста, введите полное ФИО")
        return
    await state.update_data(fio=message.text)
    # Создаем клавиатуру для выбора врача
    builder = InlineKeyboardBuilder()
    for doctor_id, doctor_name in DOCTORS.items():
        builder.add(types.InlineKeyboardButton(
            text=doctor_name,
            callback_data=f"doctor_{doctor_id}"
        ))
    builder.adjust(2)
    await message.answer("Выберите специалиста:", reply_markup=builder.as_markup())
    await state.set_state(AppointmentState.waiting_for_doctor)
@dp.callback_query(F.data.startswith("doctor_"), AppointmentState.waiting_for_doctor)
async def process_doctor(callback: types.CallbackQuery, state: FSMContext):
    doctor_id = callback.data.split("_")[1]
    await state.update_data(doctor=DOCTORS[doctor_id], doctor_id=doctor_id)
    dates_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=(datetime.now() + timedelta(days=i)).strftime("%d.%m.%Y"))]
            for i in range(1, 8)
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer("Выберите дату приема:", reply_markup=dates_kb)
    await state.set_state(AppointmentState.waiting_for_date)
    await callback.answer()
@dp.message(AppointmentState.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
        if date.date() < datetime.now().date():
            await message.answer("Пожалуйста, выберите дату в будущем")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")
        return
    await state.update_data(date=message.text)
    times_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=time)] for time in AVAILABLE_TIMES],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите время приема:", reply_markup=times_kb)
    await state.set_state(AppointmentState.waiting_for_time)
@dp.message(AppointmentState.waiting_for_time)
async def process_time(message: types.Message, state: FSMContext):
    if message.text not in AVAILABLE_TIMES:
        await message.answer("Пожалуйста, выберите время из предложенных вариантов")
        return
    await state.update_data(time=message.text)
    data = await state.get_data()
    confirmation_text = (
        "Пожалуйста, проверьте данные записи:\n\n"
        f"ФИО: {data['fio']}\n"
        f"Врач: {data['doctor']}\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['time']}\n\n"
        "Все верно?"
    )
    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(confirmation_text, reply_markup=confirm_kb)
    await state.set_state(AppointmentState.waiting_for_confirmation)
@dp.message(AppointmentState.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        await message.answer(
            "Запись успешно оформлена\n\n"
            f"ФИО: {data['fio']}\n"
            f"Врач: {data['doctor']}\n"
            f"Дата: {data['date']}\n"
            f"Время: {data['time']}",
            reply_markup=ReplyKeyboardRemove()
        )

    else:
        await message.answer("Запись отменена", reply_markup=ReplyKeyboardRemove())
    await state.clear()
async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())