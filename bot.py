import os
import sys
import time
import json
import sqlite3
import logging
import datetime
import html
import requests
import telebot
from telebot import types

# ==============================================================================
#                       1. CONFIGURATION & CONSTANTS
# ==============================================================================

BOT_TOKEN = "8271205861:AAGTOYtJQCvhS50Mgvx9Uum6L1r9xsdrfl4"
BOT_USERNAME = "@servers_1_bot"

SERVER_BASE_URL = "https://sajin13-production.up.railway.app"
SERVER_CONNECT_URL = "https://sajin13-production.up.railway.app/connect"
SERVER_ADMIN_URL = "https://sajin13-production.up.railway.app/admin/generate"
ADMIN_TOKEN = "SAJIN_SECRET_DEV_KEY_2026"

ADMIN_IDS = [8206337665] 

SYSTEM_NAME = "SAJIN"
RIGHTS_HEADER = "👑 <b>SAJIN</b> 👑"
RIGHTS_FOOTER = "© 2026 SAJIN TOP."

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("SAJIN_CORE")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==============================================================================
#                       2. DATABASE LOCAL SYSTEM (BOT SIDE)
# ==============================================================================

DB_FILE = "bot_panel.db"

def init_bot_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
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
    # استخدام الطريقة الحديثة بدلاً من utcnow() لتفادي التنبيهات
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
    safe_name = html.escape(user.first_name if user.first_name else "User")
    
    welcome_text = (
        f"🔥 <b>مرحباً بك في {SYSTEM_NAME}</b> 🔥\n\n"
        f"👤 <b>المستخدم:</b> <code>{safe_name}</code>\n"
        f"🆔 <b>الآيدي:</b> <code>{user.id}</code>\n"
        f"🤖 <b>البوت الرسمي:</b> {BOT_USERNAME}\n"
        f"🌐 <b>السيرفر المباشر:</b> <code>ONLINE 🟢</code>\n\n"
        f"🚀 <b>النظام الأقوى والأحدث لإدارة التراخيص والمفاتيح لجميع الألعاب واللودرات.</b>\n"
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
            f"🔥 <b>القائمة الرئيسية - {SYSTEM_NAME}</b> 🔥\n\n"
            f"{RIGHTS_HEADER}\n"
            f"⚡️ <b>جاهز للربط مع السورس كود وإدارة المفاتيح.</b>"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=main_menu_keyboard(user_id))

    # ─── 2. قسم توليد المفاتيح ───
    elif call.data == "menu_keys":
        text = (
            f"⚡️ <b>قسم إنشاء وتوليد المفاتيح والتراخيص</b> ⚡️\n\n"
            f"🎯 <b>اختر نوع الاشتراكات المطلوبة:</b>\n"
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
            f"📊 <b>تفاصيل وحالة سيرفر الترخيص</b> 📊\n\n"
            f"🌐 <b>رابط السيرفر:</b> <code>{SERVER_BASE_URL}</code>\n"
            f"🔌 <b>رابط الربط:</b> <code>{SERVER_CONNECT_URL}</code>\n"
            f"📡 <b>حالة الاتصال:</b> {server_status}\n"
            f"⚡️ <b>زمن الاستجابة (Ping):</b> <code>{latency} ms</code>\n"
            f"🔒 <b>نظام التشفير:</b> <code>AES-256 + HWID LOCK</code>\n"
            f"🎮 <b>الألعاب المدعومة:</b> <code>PUBG, 8Ball, FF, Loader</code>\n\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(status_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 4. قسم الألعاب المدعومة ───
    elif call.data == "menu_games":
        text = (
            f"🎮 <b>الألعاب والمنصات المدعومة رسمياً</b> 🎮\n\n"
            f"السيرفر مجهز للتعامل مع كافة أنواع اللودرات ومحاكيات الحماية:\n\n"
            f"🔹 <b>PUBG Mobile</b> (Global, KR, BGMI, VN, TW)\n"
            f"🔹 <b>PUBG External Loaders</b> (Bypass &amp; Drivers)\n"
            f"🔹 <b>8 Ball Pool</b> (Predictor &amp; Auto Play Mods)\n"
            f"🔹 <b>Free Fire</b> (Injector &amp; APK Mods)\n"
            f"🔹 <b>جميع التطبيقات والألعاب الأخرى</b> عبر C++ / ImGui.\n\n"
            f"اضغط على اسم اللعبة لمشاهدة تفاصيل الربط."
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=games_menu_keyboard())

    elif call.data.startswith("game_"):
        game_name = call.data.replace("game_", "").upper()
        info_text = (
            f"🎯 <b>تكامل السيرفر مع {game_name}</b>\n\n"
            f"✅ دعم تقييد المفتاح بـ <b>HWID الجهاز</b> لمنع المشاركة.\n"
            f"✅ تحقق لحظي عبر تشفير JSON/POST.\n"
            f"✅ رابط الربط في السورس كود:\n<code>{SERVER_CONNECT_URL}</code>"
        )
        bot.edit_message_text(info_text, chat_id, message_id, reply_markup=games_menu_keyboard())

    # ─── 5. طريقة كتابة الكود وإضافته للسورس ───
    elif call.data == "menu_guide":
        text = (
            f"💻 <b>دليل كيفية إضافة الكود ورابط السيرفر في السورس</b> 💻\n\n"
            f"اختر لغة البرمجة أو السورس كود الخاص بك لعرض الكود المباشر والتعليمات:"
        )
        bot.edit_message_text(text, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_cpp":
        cpp_code = (
            f"💻 <b>طريقة ربط C++ / ImGui مع السيرفر</b>\n\n"
            f"ضع رابط السيرفر التالي في متغير الاتصال المباشر بالسورس كود:\n\n"
            f"<code>https://sajin13-production.up.railway.app/connect</code>\n\n"
            f"<b>كود الاتصال بلغة C++:</b>\n"
            f"<pre><code class=\"language-cpp\">"
            rf'#include <iostream>' "\n"
            rf'#include <cpr/cpr.h>' "\n\n"
            rf'std::string API_URL = "https://sajin13-production.up.railway.app/connect";' "\n\n"
            rf'bool VerifyLicense(std::string key, std::string hwid) {{' "\n"
            rf'    auto response = cpr::Post(' "\n"
            rf'        cpr::Url{{API_URL}},' "\n"
            rf'        cpr::Header{{"Content-Type", "application/json"}},' "\n"
            rf'        cpr::Body{{"key": "' + r'" + key + "' + r'", "hwid": "' + r'" + hwid + "' + r'"}}' "\n"
            rf'    );' "\n"
            rf'    return (response.status_code == 200);' "\n"
            rf'}}' "\n"
            f"</code></pre>\n\n"
            f"📌 <b>ملاحظة:</b> يرسل الكود الطلب بصيغة POST ويطابق الـ HWID تلقائياً."
        )
        bot.edit_message_text(cpp_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_python":
        py_code = (
            f"🐍 <b>طريقة ربط Python Loader مع السيرفر</b>\n\n"
            f"<pre><code class=\"language-python\">"
            rf'import requests' "\n\n"
            rf'SERVER_URL = "https://sajin13-production.up.railway.app/connect"' "\n\n"
            rf'def check_key(user_key, user_hwid):' "\n"
            rf'    payload = {' "\n"
            rf'        "key": user_key,' "\n"
            rf'        "hwid": user_hwid' "\n"
            rf'    }' "\n"
            rf'    try:' "\n"
            rf'        res = requests.post(SERVER_URL, json=payload, timeout=5)' "\n"
            rf'        data = res.json()' "\n"
            rf'        if res.status_code == 200 and data.get("status") == "SUCCESS":' "\n"
            rf'            print("✅ Access Granted!")' "\n"
            rf'            return True' "\n"
            rf'        else:' "\n"
            rf'            print(f"❌ Error: {{data.get(\'message\')}}")' "\n"
            rf'            return False' "\n"
            rf'    except Exception as e:' "\n"
            rf'        print(f"⚠️ Connection Failed: {{e}}")' "\n"
            rf'        return False' "\n"
            f"</code></pre>"
        )
        bot.edit_message_text(py_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    elif call.data == "guide_curl":
        curl_code = (
            f"🌐 <b>اختبار السيرفر عبر أمر cURL</b>\n\n"
            f"يمكنك تجربة الاتصال مباشرة عبر الترمينال:\n\n"
            f"<pre><code class=\"language-bash\">"
            rf'curl -X POST https://sajin13-production.up.railway.app/connect \' "\n"
            rf'     -H "Content-Type: application/json" \' "\n"
            rf'     -d \'{"key": "TEST-KEY", "hwid": "DEVICE-HWID-123"}\'' "\n"
            f"</code></pre>"
        )
        bot.edit_message_text(curl_code, chat_id, message_id, reply_markup=guide_languages_keyboard())

    # ─── 6. إحصائيات البوت ───
    elif call.data == "menu_stats":
        total_users, total_keys = get_stats()
        stats_text = (
            f"📈 <b>إحصائيات النظام والبوت</b> 📈\n\n"
            f"👥 <b>عدد مستخدمي البوت:</b> <code>{total_users}</code>\n"
            f"🔑 <b>إجمالي المفاتيح المنشأة:</b> <code>{total_keys}</code>\n"
            f"⚙️ <b>السيرفر المرتبط:</b> <code>Railway Cloud</code>\n"
            f"🔒 <b>قاعدة البيانات:</b> <code>SQLite3 Local + Cloud</code>\n\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(stats_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 7. الحقوق والتطوير ───
    elif call.data == "menu_rights":
        rights_text = (
            f"👑 <b>حقوق النظام والتطوير</b> 👑\n\n"
            f"🔥 <b>POWERED BY SAJIN SYSTEM</b>\n"
            f"🤖 <b>البوت الرسمي:</b> {BOT_USERNAME}\n"
            f"⚡️ <b>السيرفر:</b> Railway High-Performance Cloud\n"
            f"🛡 <b>الحماية:</b> HWID Binding &amp; Timestamp Verification\n\n"
            f"{RIGHTS_FOOTER}"
        )
        bot.edit_message_text(rights_text, chat_id, message_id, reply_markup=back_keyboard())

    # ─── 8. لوحة التحكم الإدارية (Admin Panel) ───
    elif call.data == "menu_admin":
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⚠️ غير مسموح لك!", show_alert=True)
            return
        admin_text = (
            f"🔐 <b>لوحة التحكم العليا - الأدمن</b> 🔐\n\n"
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

        keys_list = "📋 <b>آخر المفاتيح التي تم إنشاؤها:</b>\n----------------------------------------\n"
        for r in rows:
            keys_list += f"🔑 <code>{r[0]}</code> | ⏱ {r[1]}D | 📅 {r[2].split('T')[0]}\n"
        
        bot.edit_message_text(keys_list, chat_id, message_id, reply_markup=admin_panel_keyboard())

    # ─── 9. توليد المفاتيح ───
    elif call.data.startswith("gen_"):
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⚠️ عذراً! صلاحية إنشاء المفاتيح محصورة بالأدمن فقط.", show_alert=True)
            return

        action = call.data.replace("gen_", "")
        
        if action == "custom":
            msg = bot.send_message(chat_id, "⚙️ <b>أرسل عدد الأيام المطلوبة للمفتاح (مثال: 15):</b>")
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
            bot.send_message(message.chat.id, "❌ <b>الرجاء إدخال رقم صحيح أكبر من 0.</b>")
            return
        generate_license_key(message.chat.id, days, message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ <b>إدخال غير صحيح. أرسل أرقاماً فقط.</b>")

def generate_license_key(chat_id, days, creator_id):
    bot.send_message(chat_id, "⏳ <b>جاري الاتصال بالسيرفر وتوليد المفتاح...</b>")
    
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
                f"🎉 <b>تم إنشاء كود الاشتراك بنجاح!</b> 🎉\n\n"
                f"🔑 <b>المفتاح:</b> <code>{key_code}</code>\n"
                f"⏱ <b>المدة:</b> <code>{days} يوم</code>\n"
                f"📅 <b>تاريخ الانتهاء:</b> <code>{expires_at}</code>\n"
                f"🔒 <b>الحالة:</b> <code>جاهز للربط بـ HWID</code>\n\n"
                f"🔗 <b>رابط السيرفر للربط باللودر:</b>\n"
                f"<code>{SERVER_CONNECT_URL}</code>\n\n"
                f"💡 <i>اضغط على المفتاح أعلاه لنسخه مباشرة.</i>"
            )
            bot.send_message(chat_id, result_text, reply_markup=back_keyboard())
        else:
            bot.send_message(chat_id, "❌ <b>فشل السيرفر في توليد المفتاح.</b>", reply_markup=back_keyboard())
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ <b>خطأ أثناء الاتصال بالسيرفر:</b> <code>{html.escape(str(e))}</code>", reply_markup=back_keyboard())

# ==============================================================================
#                       7. SYSTEM BOOTSTRAP
# ==============================================================================

if __name__ == '__main__':
    logger.info("Starting SAJIN Licensing Bot Engine...")
    print(f"🟢 {SYSTEM_NAME} IS NOW ONLINE AND FULLY FUNCTIONAL...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
