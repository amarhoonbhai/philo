from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Account"), KeyboardButton(text="📣 Ads Manager")],
            [KeyboardButton(text="✏️ Customize Name"), KeyboardButton(text="🛟 Support")],
            [KeyboardButton(text="⭐ Subscriptions")],
            [KeyboardButton(text="📨 Total Messages Sent"), KeyboardButton(text="📊 Ads Message Total Sent")]
        ],
        resize_keyboard=True
    )

def inline_login(url, guide_url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Open Login Bot", url=url)],
        [InlineKeyboardButton(text="❓ How to", url=guide_url)]
    ])
  
