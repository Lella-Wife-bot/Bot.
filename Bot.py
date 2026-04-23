import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN = "8713026682:AAFKVlRCSKbuS61lMrf_zRIR9aBry6Zm0Q8"
ADMIN_ID = 6494784660

# --- XIZMATLAR ---
SERVICES = {
    "kiprik": "👁 Kiprik ekish",
    "depil_v": "♨️ Depilatsiya (vosk)",
    "depil_l": "🪄 Depilatsiya (lazer)",
    "yuz_tozalash": "💆‍♀️ Yuz tozalash va makiyaj",
    "yuz_kosh": "🧕 Yuz va qosh terish, bo'yash",
    "kelin": "👰 Kelin makiyaji va pricheska",
    "soch_buyash": "👱‍♀️ Soch kuydirish va bo'yash",
    "soch_kesish": "💇‍♀️ Soch qirqish"
}

# Ish vaqti: 08:00 dan 19:00 gacha
TIMES = ["08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
user_data = {}

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: types.Message):
        kb = InlineKeyboardBuilder()
        for key, name in SERVICES.items():
            kb.row(types.InlineKeyboardButton(text=name, callback_data=f"s_{key}"))

        # Siz ko'rsatgan manzillar
        kb.row(types.InlineKeyboardButton(text="🖼 Galereya", callback_data="gallery"))
        kb.row(types.InlineKeyboardButton(text="👨‍⚕️ Mutaxassis bilan maslahat", url="https://t.me/Parikmaxerskaya_G"))
        kb.row(types.InlineKeyboardButton(text="✍️ Adminga murojaat", url="https://t.me/Lella_Wife"))

        await message.answer(
            "Assalomu alaykum! **Lella Wife** botiga xush kelibsiz.\n"
            "Xizmatni tanlang:",
            reply_markup=kb.as_markup()
        )

    @dp.callback_query(F.data == "gallery")
    async def gallery(call: types.CallbackQuery):
        await call.message.answer("Ishlarimiz galereyasi yaqin orada yangilanadi.")
        await call.answer()

    @dp.callback_query(F.data.startswith("s_"))
    async def select_service(call: types.CallbackQuery):
        key = call.data.split("_")[1]
        user_data[call.from_user.id] = {'service': SERVICES[key]}
        kb = InlineKeyboardBuilder()
        for d in ["Bugun", "Ertaga", "Indinga"]:
            kb.add(types.InlineKeyboardButton(text=d, callback_data=f"d_{d}"))
        await call.message.edit_text(f"Xizmat: {SERVICES[key]}\nKunni tanlang:", reply_markup=kb.as_markup())
        await call.answer()

    @dp.callback_query(F.data.startswith("d_"))
    async def select_day(call: types.CallbackQuery):
        user_id = call.from_user.id
        if user_id in user_data:
            user_data[user_id]['day'] = call.data.split("_")[1]
            kb = InlineKeyboardBuilder()
            for t in TIMES:
                kb.add(types.InlineKeyboardButton(text=t, callback_data=f"t_{t}"))
            kb.adjust(3)
            await call.message.edit_text("Vaqtni tanlang:", reply_markup=kb.as_markup())
        await call.answer()

    @dp.callback_query(F.data.startswith("t_"))
    async def select_time(call: types.CallbackQuery):
        user_id = call.from_user.id
        if user_id in user_data:
            user_data[user_id]['time'] = call.data.split("_")[1]
            kb = ReplyKeyboardBuilder()
            kb.add(types.KeyboardButton(text="📱 Raqamni yuborish", request_contact=True))
            await call.message.delete()
            await bot.send_message(user_id, "Telefon raqamingizni yuboring:", reply_markup=kb.as_markup(resize_keyboard=True))
        await call.answer()

    @dp.message(F.contact)
    async def finalize(message: types.Message):
        uid = message.from_user.id
        if uid in user_data:
            data = user_data[uid]
            await message.answer("✅ Rahmat! So'rovingiz qabul qilindi.", reply_markup=types.ReplyKeyboardRemove())

            # Adminga xabar yuborish
            admin_msg = (
                f"🆕 YANGI BRON!\n\n"
                f"👤 Mijoz: {message.from_user.full_name}\n"
                f"📞 Tel: {message.contact.phone_number}\n"
                f"💅 Xizmat: {data['service']}\n"
                f"⏰ Vaqt: {data['day']} soat {data['time']}"
            )
            await bot.send_message(ADMIN_ID, admin_msg)
            del user_data[uid]

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
