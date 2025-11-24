import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния разговора
QUESTION, ANSWER = range(2)

# Вопросы и ответы
questions = [
    {
        "question": "1. Какой минерал символизирует богатства Урала в Историческом сквере?",
        "options": ["Изумруд", "Малахит", "Родонит", "Аметист"],
        "correct": 2,
        "photo": "https://ibb.co/TMHMP5q1"
    },
    {
        "question": "2. Как называлась первая улица Екатеринбурга?",
        "options": ["Центральная", "Главная", "Заводская", "Перспективная"],
        "correct": 3,
        "photo": "https://ibb.co/Y7HP5j34"
    },
    {
        "question": "3. Есть ли в Екатеринбурге стела «Европа — Азия»?",
        "options": ["Да", "Нет, граница проходит за пределами города", "Была, но её демонтировали в 1990 е годы", "Стела есть, но она называется «Урал — Сибирь»"],
        "correct": 0,
        "photo": "https://ibb.co/nsj9VGDM"
    },
    {
        "question": "4. Была ли в Екатеринбурге монетная фабрика?",
        "options": ["Да", "Нет"],
        "correct": 0,
        "photo": "https://ibb.co/F4k9VGh2"
    },
    {
        "question": "5. Какое водохранилище обеспечивает город водой?",
        "options": ["Верх Исетское", "Волчихинское", "Нижне Исетское", "Партизанское"],
        "correct": 1,
        "photo": "https://ibb.co/208yBw5T"
    },
    {
        "question": "6. Какое здание называют «Американской гостиницей»?",
        "options": ["Гостиница «Центральная»", "Здание Главпочтамта", "Особняк Рабиновича", "Дом Севастьянова"],
        "correct": 0,
        "photo": "https://ibb.co/WvYLCtd8"
    },
    {
        "question": "7. Что символизируют стелы ВИЗа?",
        "options": ["Границу между Европой и Азией", "Единство рабочих и инженеров", "Процесс прокатки металла", "Волны"],
        "correct": 2,
        "photo": "https://ibb.co/pBPXHXMg"
    },
    {
        "question": "8. С начала 1950 х годов железнодорожная станция Свердловск Сортировочный на Свердловской магистрали превращается в один из мощнейших узлов страны. Какой эпитет за ней закрепился?",
        "options": ["«Фабрика маршрутов»", "«Сердце Транссиба»", "«Ворота Урала»", "«Железный узел»"],
        "correct": 0,
        "photo": "https://ibb.co/b5h8d0SK"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинаем квиз"""
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0
    
    await update.message.reply_text(
        "🎯 Добро пожаловать в викторину!\n"
        "Ответь на 8 вопросов и проверь свои знания.\n"
        "Начинаем!"
    )
    
    await ask_question(update, context)
    return QUESTION

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Задаем вопрос с вариантами ответов"""
    current = context.user_data['current_question']
    question_data = questions[current]
    
    # Создаем клавиатуру с вариантами
    keyboard = [question_data["options"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    # Если есть фото - отправляем с фото
    if "photo" in question_data and question_data["photo"]:
        await update.message.reply_photo(
            photo=question_data["photo"],
            caption=question_data["question"],
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            question_data["question"],
            reply_markup=reply_markup
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем ответ"""
    user_answer = update.message.text
    current = context.user_data['current_question']
    question_data = questions[current]
    
    # Проверяем ответ
    if user_answer == question_data["options"][question_data["correct"]]:
        context.user_data['score'] += 1
        await update.message.reply_text("✅ Правильно!")
    else:
        correct_answer = question_data["options"][question_data["correct"]]
        await update.message.reply_text(f"❌ Неправильно. Правильный ответ: {correct_answer}")
    
    # Следующий вопрос или завершение
    context.user_data['current_question'] += 1
    
    if context.user_data['current_question'] < len(questions):
        await ask_question(update, context)
        return QUESTION
    else:
        return await finish_quiz(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершаем квиз и показываем результаты"""
    score = context.user_data['score']
    total = len(questions)
    percentage = (score / total) * 100
    
    # Определяем оценку
    if percentage >= 90:
        grade = "Отлично! 🎉🏆"
    elif percentage >= 70:
        grade = "Хорошо! 👍⭐"
    elif percentage >= 50:
        grade = "Удовлетворительно 👌✅"
    else:
        grade = "Плохо 😔📚"
    
    await update.message.reply_text(
        f"🏁 Квиз завершен!\n\n"
        f"📊 Твой результат: {score} из {total}\n"
        f"📈 Процент правильных: {percentage:.1f}%\n"
        f"🎯 Оценка: {grade}",
        reply_markup=ReplyKeyboardRemove()
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяем квиз"""
    await update.message.reply_text(
        "Квиз отменен. Напиши /start чтобы начать заново",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Запускаем бота"""
    # ЗАМЕНИ НА СВОЙ ТОКЕН!
    application = Application.builder().token("8026036715:A&Ed8bbKpxV5j6vkWRahpGEUsDaWwtb2E_c").build()
    
    # Обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", cancel))
    
    print("🤖 Бот с викториной запущен! Напиши /start в Telegram")
    application.run_polling()

if __name__ == '__main__':
    main()
