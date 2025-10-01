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

def setup_root_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Manage Groups", callback_data="setup_groups")],
        [InlineKeyboardButton(text="🧷 Manage Ads",    callback_data="setup_ads")],
        [InlineKeyboardButton(text="⏱ Schedule",       callback_data="setup_sched")],
        [InlineKeyboardButton(text="⬅️ Back",          callback_data="back_ads_home")],
    ])

def groups_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add GC by link (t.me/... or @user)", callback_data="groups_add_link")],
        [InlineKeyboardButton(text="📃 List", callback_data="groups_list")],
        [InlineKeyboardButton(text="🗑 Delete GC by link", callback_data="groups_del_link")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="setup_home")],
    ])

def ads_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add (paste message link)", callback_data="ads_add")],
        [InlineKeyboardButton(text="📃 List", callback_data="ads_list")],
        [InlineKeyboardButton(text="⚖️ Set weight (ad_id weight)", callback_data="ads_weight")],
        [InlineKeyboardButton(text="🗑 Delete (send ad_id)", callback_data="ads_del")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="setup_home")],
    ])

def sched_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="20m", callback_data="sched_20"),
         InlineKeyboardButton(text="40m", callback_data="sched_40"),
         InlineKeyboardButton(text="60m", callback_data="sched_60")],
        [InlineKeyboardButton(text="🕰 Window (HH:MM-HH:MM)", callback_data="sched_win")],
        [InlineKeyboardButton(text="ℹ️ Cycle: 3h ON / 1h OFF (auto)", callback_data="sched_info")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="setup_home")],
    ])
    
