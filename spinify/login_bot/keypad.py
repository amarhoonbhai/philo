from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def otp_keyboard(prefix="otp:"):
    rows = []
    nums = ["1","2","3","4","5","6","7","8","9","0"]
    for i in range(0,9,3):
        rows.append([InlineKeyboardButton(text=n, callback_data=f"{prefix}{n}") for n in nums[i:i+3]])
    rows.append([InlineKeyboardButton(text="0", callback_data=f"{prefix}0")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data=f"{prefix}back"),
        InlineKeyboardButton(text="🧹 Clear", callback_data=f"{prefix}clear"),
        InlineKeyboardButton(text="✔️ Submit", callback_data=f"{prefix}submit"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
  
