import os
import sys
import time
import json
import sqlite3
import logging
import datetime
import secrets
import requests
import telebot
from telebot import types

# ==============================================================================
#                       1. CONFIGURATION & CONSTANTS
# ==============================================================================

BOT_TOKEN = "8931553128:AAEizyl4u23sxZltvXuQhpH42kezELreY5I"
BOT_USERNAME = "@x96n_bot"

# سيرفر Railway
SERVER_BASE_URL = "https://sajin13-production.up.railway.app"
SERVER_CONNECT_URL = "https://sajin13-production.up.railway.app/connect"
SERVER_ADMIN_URL = "https://sajin13-production.up.railway.app/admin/generate"
ADMIN_TOKEN = "SAJIN_SECRET_DEV_KEY_2026"

# معرف الآدمن
ADMIN_IDS = [8206337665] 

SYSTEM_NAME = "SAJIN"
RIGHTS_HEADER = "👑 *SAJIN* 👑"
RIGHTS_FOOTER = "© 2026 SAJIN TOP."

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("SAJIN_CORE")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ==============================================================================
#                       2. DATABASE LOCAL SYSTEM (BOT SIDE)
# ==============================================================================

DB_FILE = "bot_panel.db"

def init_bot_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # جدول المفاتيح الصادرة من البوت
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_code TEXT UNIQUE,
            days INTEGER,
            created_by INTEGER,
            created_at TEXT,
            game_type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_bot_db()

def register_user(user):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date) VALUES (?, ?, ?, ?)",
        (user.id, user.username, user.first_name, now)
    )
    conn.commit()
    conn.close()

def save_key_to_db(key_code, days, creator_id, game_type="ALL"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute(
        "INSERT INTO generated_keys (key_code, days, created_by, created_at, game_type) VALUES (?, ?, ?, ?, ?)",
        (key_code, days, creator_id, now, game_type)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM generated_keys")
    total_keys = cursor.fetchone()[0]
    conn.close()
    return total_users, total_keys

# ==============================================================================
#                       3. ADVANCED KEYBOARD UI
# ==============================================================================

def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_keys = types.InlineKeyboardButton("⚡️ قسم إنشاء المفاتيح", callback_data="menu_keys")
    btn_status = types.InlineKeyboardButton("📊 حالة السيرفر", callback_data="menu_status")
    btn_guide = types.InlineKeyboardButton("💻 طريقة إضافة الكود للسورس", callback_data="menu_guide")
    btn_games = types.InlineKeyboardButton("🎮 الألعاب واللودرات المدعومة", callback_data="menu_games")
    btn_stats = types.InlineKeyboardButton("📈 إحصائيات البوت", callback_data="menu_stats")
    btn_rights = types.InlineKeyboardButton("👑 الحقوق والتطوير", callback_data="menu_rights")
    
    markup.add(btn_keys, btn_status)
    markup.add(btn_guide, btn_games)
    markup.add(btn_stats, btn_rights)
    
    if user_id in ADMIN_IDS:
        btn_admin = types.InlineKeyboardButton("🔐 لوحة التحكم العليا (Admin)", callback_data="menu_admin")
        markup.add(btn_admin)
        
    return markup

def key_generation_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_1d = types.InlineKeyboardButton("🟡 مفتاح تجريبي (1D)", callback_data="gen_1")
    btn_7d = types.InlineKeyboardButton("🟢 مفتاح أسبوعي (7D)", callback_data="gen_7")
    btn_30d = types.InlineKeyboardButton("🟣 مفتاح شهري (30D)", callback_data="gen_30")
    btn_365d = types.InlineKeyboardButton("🔴 مفتاح سنوي (365D)", callback_data="gen_365")
    btn_custom = types.InlineKeyboardButton("⚙️ تخصيص مدة باليوم", callback_data="gen_custom")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="menu_back")
    
    markup.add(btn_1d, btn_7d)
    markup.add(btn_30d, btn_365d)
    markup.add(btn_custom)
    markup.add(btn_back)
    return markup

def games_menu_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_pubg = types.InlineKeyboardButton("🔥 PUBG Mobile", callback_data="game_pubg")
    btn_loader = types.InlineKeyboardButton("🛡 PUBG Loader / External", callback_data="game_loader")
    btn_8ball = types.InlineKeyboardButton("🎱 8 Ball Pool", callback_data="game_8ball")
    btn_ff = types.InlineKeyboardButton("💎 Free Fire", callback_data="game_ff")
    btn_all = types.InlineKeyboardButton("🌐 جميع الألعاب والأدوات", callback_data="game_all")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="menu_back")
    
    markup.add(btn_pubg, btn_loader)
    markup.add(btn_8ball, btn_ff)
    markup.add(btn_all)
    markup.add(btn_back)
    return markup

def guide_languages_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_cpp = types.InlineKeyboardButton("💻 C++ / ImGui Source", callback_data="guide_cpp")
    btn_python = types.InlineKeyboardButton("🐍 Python Loader", callback_data="guide_python")
    btn_curl = types.InlineKeyboardButton("🌐 cURL / REST API", callback_data="guide_curl")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="menu_back")
    
    markup.add(btn_cpp, btn_python)
    markup.add(btn_curl)
    markup.add(btn_back)
    return markup

def admin_panel_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_broadcast = types.InlineKeyboardButton("📢 إذاعة للمستخدمين", callback_data="admin_broadcast")
    btn_list_keys = types.InlineKeyboardButton("📋 كشف آخر المفاتيح", callback_data="admin_keys")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="menu_back")
    
    markup.add(btn_broadcast, btn_list_keys)
    markup.add(btn_back)
    return markup

def back_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu_back")
    markup.add(btn_back)
    return markup

# ==============================================================================
#                       4. COMMANDS & MESSAGE HANDLERS
# ==============================================================================

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    register_user(message.from_user)
    user = message.from_user
    welcome_text = (
        f"🔥 *مرحباً بك في {SYSTEM_NAME}* 🔥\n"
        f"----------------------------------------\n"
        f"👤 *المستخدم:* `{user.first_name}`\n"
        f"🆔 *الآيدي:* `{user.id}`\n"
        f"🤖 *البوت الرسمي:* {BOT_USERNAME}\n"
        f"🌐 *السيرفر المباشر:* `ONLINE 🟢`\n"
        f"----------------------------------------\n"
        f"🚀 *النظام الأقوى والأحدث لإدارة التراخيص والمفاتيح لجميع الألعاب واللودرات.*\n"
        f"اختر من القائمة الشفافة أدناه للتحكم الكامل:"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_menu_keyboard(user.id)
    )

# ==============================================================================
#                       5. CALLBACK QUERY PROCESSOR
# ==============================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # ─── 1. القائمة الرئيسية ───
    if call.data == "menu_back":
        text = (
            f"🔥 *القائمة الرئيسية - {SYSTEM_NAME}* 🔥\n"
            f"----------------------------------------\n"
            f"{RIGHTS_HEADER}\n"
            f"⚡️ *جاهز للربط مع السورس كود وإدارة المفاتيح.*"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=main_menu_keyboard(user_id))

    # ─── 2. قسم توليد المفاتيح ───
    elif call.data == "menu_keys":
        text = (
            f"⚡️ *قسم إنشاء وتوليد المفاتيح والتراخيص* ⚡️\n"
            f"----------------------------------------\n"
            f"🎯 *اختر نوع الاشتراكات المطلوبة:*\n"
            f"سيتم ربط المفتاح تلقائياً بقاعدة بيانات السيرفر المركزية على Railway."
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=key_generation_keyboard())

    # ─── 3. حالة السيرفر والاتصال ───
    elif call.data == "menu_status":
        bot.answer_callback_query(call.id, "⏳ جاري فحص استجابة السيرفر...")
        try:
            start_time = time.time()
            res = requests.get(SERVER_BASE_URL, timeout=5)
            latency = round((time.time() - start_time) * 1000, 2)
            
            if res.status_code == 200:
                server_status = "🟢 ON - السيرفر يعمل بكفاءة قصوى"
            else:
                server_status = "🔴 WARNING - استجابة غير متوقعة"
        except Exception:
            server_status = "❌ OFF - متعذر الاتصال بالسيرفر"
            latency = 0

        status_text = (
            f"📊 *تفاصيل وحالة سيرفر الترخيص* 📊\n"
            f"----------------------------------------\n"
            f"🌐 *رابط السيرفر:* `{SERVER_BASE_URL}`\n"
            f"🔌 *رابط الربط:* `{SERVER_CONNECT_URL}`\n"
            f"📡 *حالة الاتصال:* {server_status}\n"
            f"⚡️ *زمن الاستجابة (Ping):* `{latency} ms`\n"
            f"🔒 *نظام التشفير:* `AES-256 + HWID LOCK`\n"
            f"🎮 *الألعاب المدعومة:* `PUBG, 8Ball, FF, Loader`\n"
            f"----------------------------------------\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(status_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 4. قسم الألعاب المدعومة ───
    elif call.data == "menu_games":
        text = (
            f"🎮 *الألعاب والمنصات المدعومة رسمياً* 🎮\n"
            f"----------------------------------------\n"
            f"السيرفر مجهز للتعامل مع كافة أنواع اللودرات ومحاكيات الحماية:\n\n"
            f"🔹 *PUBG Mobile* (Global, KR, BGMI, VN, TW)\n"
            f"🔹 *PUBG External Loaders* (Bypass & Drivers)\n"
            f"🔹 *8 Ball Pool* (Predictor & Auto Play Mods)\n"
            f"🔹 *Free Fire* (Injector & APK Mods)\n"
            f"🔹 *جميع التطبيقات والألعاب الأخرى* عبر C++ / ImGui.\n"
            f"----------------------------------------\n"
            f"اضغط على اسم اللعبة لمشاهدة تفاصيل الربط."
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=games_menu_keyboard())

    elif call.data.startswith("game_"):
        game_name = call.data.replace("game_", "").upper()
        info_text = (
            f"🎯 *تكامل السيرفر مع {game_name}*\n"
            f"----------------------------------------\n"
            f"✅ دعم تقييد المفتاح بـ *HWID الجهاز* لمنع المشاركة.\n"
            f"✅ تحقق لحظي عبر تشفير JSON/POST.\n"
            f"✅ رابط الربط في السورس كود:\n`{SERVER_CONNECT_URL}`"
        )
        bot.edit_message_text(info_text, chat_id, message_id, reply_markup=games_menu_keyboard())

    # ─── 5. طريقة كتابة الكود وإضافته للسورس ───
    elif call.data == "menu_guide":
        text = (
            f"💻 *دليل كيفية إضافة الكود ورابط السيرفر في السورس* 💻\n"
            f"----------------------------------------\n"
            f"اختر لغة البرمجة أو السورس كود الخاص بك لعرض الكود المباشر والتعليمات:"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_cpp":
        cpp_code = (
            f"💻 *طريقة ربط C++ / ImGui مع السيرفر*\n"
            f"----------------------------------------\n"
            f"ضع رابط السيرفر التالي في متغير الاتصال المباشر بالسورس كود:\n\n"
            f"`https://sajin13-production.up.railway.app/connect`\n\n"
            f"*كود الاتصال بلغة C++:*\n"
            f"```cpp\n"
            f"#include <iostream>\n"
            f"#include <cpr/cpr.h>\n\n"
            f"std::string API_URL = \"[https://sajin13-production.up.railway.app/connect](https://sajin13-production.up.railway.app/connect)\";\n\n"
            f"bool VerifyLicense(std::string key, std::string hwid) {{\n"
            f"    auto response = cpr::Post(\n"
            f"        cpr::Url{{API_URL}},\n"
            f'        cpr::Header{{"Content-Type", "application/json"}},\n'
            f'        cpr::Body{{"{{\\"key\\": \\"" + key + "\\", \\"hwid\\": \\"" + hwid + "\\"}}"}}\n'
            f"    );\n"
            f"    return (response.status_code == 200);\n"
            f"}}\n"
            f"```\n"
            f"----------------------------------------\n"
            f"📌 *ملاحظة:* يرسل الكود الطلب بصيغة POST ويطابق الـ HWID تلقائياً."
        )
        bot.edit_message_text(cpp_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_python":
        py_code = (
            f"🐍 *طريقة ربط Python Loader مع السيرفر*\n"
            f"----------------------------------------\n"
            f"```python\n"
            f"import requests\n\n"
            f'SERVER_URL = "[https://sajin13-production.up.railway.app/connect](https://sajin13-production.up.railway.app/connect)"\n\n'
            f"def check_key(user_key, user_hwid):\n"
            f"    payload = {{\n"
            f'        "key": user_key,\n'
            f'        "hwid": user_hwid\n'
            f"    }}\n"
            f"    try:\n"
            f"        res = requests.post(SERVER_URL, json=payload, timeout=5)\n"
            f"        data = res.json()\n"
            f'        if res.status_code == 200 and data.get("status") == "SUCCESS":\n'
            f'            print("✅ Access Granted!")\n'
            f"            return True\n"
            f"        else:\n"
            f'            print(f"❌ Error: {{data.get(\'message\')}}")\n'
            f"            return False\n"
            f"    except Exception as e:\n"
            f'        print(f"⚠️ Connection Failed: {{e}}")\n'
            f"        return False\n"
            f"```"
        )
        bot.edit_message_text(py_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_curl":
        curl_code = (
            f"🌐 *اختبار السيرفر عبر أمر cURL*\n"
            f"----------------------------------------\n"
            f"يمكنك تجربة الاتصال مباشرة عبر الترمينال:\n\n"
            f"```bash\n"
            f"curl -X POST [https://sajin13-production.up.railway.app/connect](https://sajin13-production.up.railway.app/connect) \\\n"
            f'     -H "Content-Type: application/json" \\\n'
            f'     -d \'{{"key": "TEST-KEY", "hwid": "DEVICE-HWID-123"}}\'\n'
            f"```"
        )
        bot.edit_message_text(curl_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    # ─── 6. إحصائيات البوت ───
    elif call.data == "menu_stats":
        total_users, total_keys = get_stats()
        stats_text = (
            f"📈 *إحصائيات النظام والبوت* 📈\n"
            f"----------------------------------------\n"
            f"👥 *عدد مستخدمي البوت:* `{total_users}`\n"
            f"🔑 *إجمالي المفاتيح المنشأة:* `{total_keys}`\n"
            f"⚙️ *السيرفر المرتبط:* `Railway Cloud`\n"
            f"🔒 *قاعدة البيانات:* `SQLite3 Local + Cloud`\n"
            f"----------------------------------------\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(stats_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 7. الحقوق والتطوير ───
    elif call.data == "menu_rights":
        rights_text = (
            f"👑 *حقوق النظام والتطوير* 👑\n"
            f"----------------------------------------\n"
            f"🔥 *POWERED BY SAJIN SYSTEM*\n"
            f"🤖 *البوت الرسمي:* {BOT_USERNAME}\n"
            f"⚡️ *السيرفر:* Railway High-Performance Cloud\n"
            f"🛡 *الحماية:* HWID Binding & Timestamp Verification\n"
            f"----------------------------------------\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(rights_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 8. لوحة التحكم الإدارية (Admin Panel) ───
    elif call.data == "menu_admin":
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⚠️ غير مسموح لك!", show_alert=True)
            return
        admin_text = (
            f"🔐 *لوحة التحكم العليا - الأدمن* 🔐\n"
            f"----------------------------------------\n"
            f"مرحباً بك في قسم إدارة السيرفر والإذاعة للمستخدمين:"
        )
        bot.edit_message_text(admin_text, chat_id, message_id, reply_markup=admin_panel_keyboard())

    elif call.data == "admin_keys":
        if user_id not in ADMIN_IDS:
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT key_code, days, created_at FROM generated_keys ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()

        keys_list = "📋 *آخر المفاتيح التي تم إنشاؤها:*\n----------------------------------------\n"
        for r in rows:
            keys_list += f"🔑 `{r[0]}` | ⏱ {r[1]}D | 📅 {r[2].split('T')[0]}\n"
        
        bot.edit_message_text(keys_list, chat_id, message_id, reply_markup=admin_panel_keyboard())

    # ─── 9. توليد المفاتيح ───
    elif call.data.startswith("gen_"):
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⚠️ عذراً! صلاحية إنشاء المفاتيح محصورة بالأدمن فقط.", show_alert=True)
            return

        action = call.data.replace("gen_", "")
        
        if action == "custom":
            msg = bot.send_message(chat_id, "⚙️ *أرسل عدد الأيام المطلوبة للمفتاح (مثال: 15):*")
            bot.register_next_step_handler(msg, process_custom_days)
            return

        days = int(action)
        generate_license_key(chat_id, days, user_id)

# ==============================================================================
#                       6. KEY GENERATION CORE LOGIC
# ==============================================================================

def process_custom_days(message):
    try:
        days = int(message.text.strip())
        if days <= 0:
            bot.send_message(message.chat.id, "❌ *الرجاء إدخال رقم صحيح أكبر من 0.*")
            return
        generate_license_key(message.chat.id, days, message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ *إدخال غير صحيح. أرسل أرقاماً فقط.*")

def generate_license_key(chat_id, days, creator_id):
    bot.send_message(chat_id, "⏳ *جاري الاتصال بالسيرفر وتوليد المفتاح...*")
    
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    payload = {"days": days}

    try:
        response = requests.post(SERVER_ADMIN_URL, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201 and data.get("status") == "SUCCESS":
            key_code = data.get("key")
            expires_at = data.get("expires_at", "").split("T")[0]

            save_key_to_db(key_code, days, creator_id)

            result_text = (
                f"🎉 *تم إنشاء كود الاشتراك بنجاح!* 🎉\n"
                f"----------------------------------------\n"
                f"🔑 *المفتاح:* `{key_code}`\n"
                f"⏱ *المدة:* `{days} يوم`\n"
                f"📅 *تاريخ الانتهاء:* `{expires_at}`\n"
                f"🔒 *الحالة:* `جاهز للربط بـ HWID`\n"
                f"----------------------------------------\n"
                f"🔗 *رابط السيرفر للربط باللودر:*\n"
                f"`{SERVER_CONNECT_URL}`\n\n"
                f"💡 _اضغط على المفتاح أعلاه لنسخه مباشرة._"
            )
            bot.send_message(chat_id, result_text, reply_markup=back_keyboard())
        else:
            bot.send_message(chat_id, "❌ *فشل السيرفر في توليد المفتاح.*", reply_markup=back_keyboard())
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ *خطأ أثناء الاتصال بالسيرفر:* `{str(e)}`", reply_markup=back_keyboard())

# ==============================================================================
#                       7. SYSTEM BOOTSTRAP
# ==============================================================================

if __name__ == '__main__':
    logger.info("Starting SAJIN Licensing Bot Engine...")
    print(f"🟢 {SYSTEM_NAME} IS NOW ONLINE AND FULLY FUNCTIONAL...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
