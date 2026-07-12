# -*- coding: utf-8 -*-
"""
بوم متجر | نسخة احترافية بإدارة كاملة من داخل البوت.

المميزات:
- تعديل أسماء الأزرار الأساسية
- تغيير ألوان الأزرار
- إخفاء وإظهار الأزرار
- تغيير ترتيب الأزرار
- تعديل نصوص الأقسام
- إدارة الخدمات
- حفظ الإعدادات في JSON
- أوامر خاصة للأدمن فقط

التثبيت:
pip install -U pyTelegramBotAPI
"""

import json
import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "8615795845:AAE-Uv_4-YaL3A9WjNFQ-VhJsaMVS3XsjJs").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "798055716"))
DATA_FILE = "boom_store_pro_data.json"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
admin_state = {}


def default_data():
    return {
        "store_name": "💥 بوم متجر | أدوات بايثون",
        "welcome_text": "• أدوات وملفات بايثون\n• خدمات رقمية\n• سرعة في التنفيذ",
        "buttons": [
            {
                "key": "services",
                "text": "🛍 الخدمات",
                "style": "success",
                "visible": True,
                "order": 1
            },
            {
                "key": "contact",
                "text": "📞 التواصل",
                "style": "primary",
                "visible": True,
                "order": 2
            },
            {
                "key": "about",
                "text": "ℹ️ حول المتجر",
                "style": "primary",
                "visible": True,
                "order": 3
            },
            {
                "key": "refresh",
                "text": "🔄 تحديث",
                "style": "success",
                "visible": True,
                "order": 4
            }
        ],
        "contact_text": "سيتم إضافة وسيلة التواصل قريبًا.",
        "about_text": "بوم متجر متخصص في أدوات بايثون والخدمات الرقمية.",
        "services": [],
        "admins": [ADMIN_ID],
        "users": [],
        "blocked_users": []
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        base = default_data()

        for key, value in base.items():
            if key not in data:
                data[key] = value

        existing_keys = {item.get("key") for item in data.get("buttons", [])}

        for button_item in base["buttons"]:
            if button_item["key"] not in existing_keys:
                data["buttons"].append(button_item)

        return data

    except Exception:
        return default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)



def is_admin(user_id):
    return user_id in load_data().get("admins", [ADMIN_ID])


def is_owner(user_id):
    return user_id == ADMIN_ID


def register_user(user_id):
    data = load_data()
    users = data.setdefault("users", [])
    if user_id not in users:
        users.append(user_id)
        save_data(data)


def make_button(text, callback_data, style=None):
    try:
        return types.InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            style=style
        )
    except TypeError:
        return types.InlineKeyboardButton(
            text=text,
            callback_data=callback_data
        )


def edit_or_send(call, text, keyboard=None):
    try:
        bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    except Exception:
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboard
        )


def get_button_config(key):
    data = load_data()
    for item in data["buttons"]:
        if item["key"] == key:
            return item
    return None


def sorted_visible_buttons():
    data = load_data()
    items = [item for item in data["buttons"] if item.get("visible", True)]
    return sorted(items, key=lambda x: x.get("order", 999))


def home_text(name):
    data = load_data()
    return (
        f"<b>{data['store_name']}</b>\n\n"
        f"مرحبًا <b>{name}</b> 👋\n\n"
        f"{data['welcome_text']}\n\n"
        "اختر القسم المطلوب:"
    )


def home_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for item in sorted_visible_buttons():
        callback_map = {
            "services": "user_services",
            "contact": "user_contact",
            "about": "user_about",
            "refresh": "user_home"
        }

        buttons.append(
            make_button(
                item["text"],
                callback_map[item["key"]],
                item.get("style")
            )
        )

    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i + 2])

    return kb


def admin_main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.row(
        make_button("🏪 إعدادات المتجر", "admin_store_settings", "primary"),
        make_button("🔘 إدارة الأزرار", "admin_buttons", "success")
    )

    kb.row(
        make_button("🛍 إدارة الخدمات", "admin_services", "success"),
        make_button("👥 إدارة الأدمنات", "admin_manage_admins", "danger")
    )

    kb.row(
        make_button("📢 إرسال جماعي", "admin_broadcast", "primary"),
        make_button("📊 الإحصائيات", "admin_stats", "primary")
    )

    kb.row(
        make_button("👁 معاينة المتجر", "user_home", "success"),
        make_button("📦 تصدير الإعدادات", "admin_export", "primary")
    )

    kb.row(
        make_button("❌ إغلاق", "admin_close", "danger")
    )

    return kb


def admin_store_settings_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.row(
        make_button("🏪 اسم المتجر", "edit_store_name", "primary"),
        make_button("👋 رسالة الترحيب", "edit_welcome_text", "primary")
    )

    kb.row(
        make_button("📞 نص التواصل", "edit_contact_text", "success"),
        make_button("ℹ️ نص حول المتجر", "edit_about_text", "success")
    )

    kb.row(
        make_button("↩️ رجوع", "admin_panel", "danger")
    )

    return kb


def admin_buttons_keyboard():
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)

    for item in sorted(data["buttons"], key=lambda x: x.get("order", 999)):
        state = "✅ ظاهر" if item.get("visible", True) else "🚫 مخفي"
        kb.add(
            make_button(
                f"{item['text']} | {state}",
                f"manage_button:{item['key']}",
                item.get("style")
            )
        )

    kb.add(make_button("↩️ رجوع", "admin_panel", "danger"))
    return kb


def single_button_manage_keyboard(key):
    item = get_button_config(key)
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.row(
        make_button("✏️ تغيير الاسم", f"btn_rename:{key}", "primary"),
        make_button("🎨 تغيير اللون", f"btn_color:{key}", "success")
    )

    visible_text = "🚫 إخفاء الزر" if item.get("visible", True) else "✅ إظهار الزر"

    kb.row(
        make_button(visible_text, f"btn_toggle:{key}", "danger"),
        make_button("🔢 تغيير الترتيب", f"btn_order:{key}", "primary")
    )

    kb.row(
        make_button("↩️ رجوع للأزرار", "admin_buttons", "danger")
    )

    return kb


def color_keyboard(key):
    kb = types.InlineKeyboardMarkup(row_width=3)

    kb.row(
        make_button("🔵 أزرق", f"set_color:{key}:primary", "primary"),
        make_button("🟢 أخضر", f"set_color:{key}:success", "success"),
        make_button("🔴 أحمر", f"set_color:{key}:danger", "danger")
    )

    kb.row(make_button("↩️ رجوع", f"manage_button:{key}", "danger"))
    return kb


def admin_services_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.row(
        make_button("➕ إضافة خدمة", "service_add", "success"),
        make_button("✏️ تعديل خدمة", "service_edit", "primary")
    )

    kb.row(
        make_button("🗑 حذف خدمة", "service_delete", "danger"),
        make_button("📋 عرض الخدمات", "service_list", "primary")
    )

    kb.row(make_button("↩️ رجوع", "admin_panel", "danger"))
    return kb


def service_select_keyboard(action):
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)

    for index, service in enumerate(data["services"]):
        kb.add(
            make_button(
                service.get("name", f"خدمة {index + 1}"),
                f"{action}:{index}",
                "primary"
            )
        )

    kb.add(make_button("↩️ رجوع", "admin_services", "danger"))
    return kb


def user_services_keyboard():
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for index, service in enumerate(data["services"]):
        buttons.append(
            make_button(
                f"🛒 {service.get('name', 'خدمة')}",
                f"user_service:{index}",
                "success"
            )
        )

    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i + 2])

    kb.row(make_button("🏠 الرئيسية", "user_home", "primary"))
    return kb



def admins_keyboard():
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(make_button("➕ إضافة أدمن", "admin_add_admin", "success"))
    for admin_id in data.get("admins", [ADMIN_ID]):
        title = "👑 المالك" if admin_id == ADMIN_ID else "👤 أدمن"
        kb.add(make_button(f"{title}: {admin_id}", f"admin_view:{admin_id}", "primary"))
    kb.add(make_button("↩️ رجوع", "admin_panel", "danger"))
    return kb


def admin_details_keyboard(admin_id):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if admin_id != ADMIN_ID:
        kb.add(make_button("🗑 حذف الأدمن", f"admin_remove:{admin_id}", "danger"))
    kb.add(make_button("↩️ رجوع", "admin_manage_admins", "primary"))
    return kb


@bot.message_handler(commands=["start"])
def start_command(message):
    register_user(message.from_user.id)
    if message.from_user.id in load_data().get("blocked_users", []):
        bot.send_message(message.chat.id, "🚫 تم حظرك من استخدام البوت.")
        return
    bot.send_message(
        message.chat.id,
        home_text(message.from_user.first_name or "عزيزي"),
        reply_markup=home_keyboard()
    )


@bot.message_handler(commands=["admin"])
def admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ هذا الأمر خاص بالإدارة.")
        return

    bot.send_message(
        message.chat.id,
        "<b>👑 لوحة الإدارة الاحترافية</b>\n\n"
        "يمكنك التحكم في كل شيء من هنا:",
        reply_markup=admin_main_keyboard()
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    action = call.data

    # واجهة المستخدم
    if action == "user_home":
        edit_or_send(
            call,
            home_text(call.from_user.first_name or "عزيزي"),
            home_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action == "user_services":
        services = load_data()["services"]
        text = (
            "<b>🛍 خدمات المتجر</b>\n\n"
            + ("اختر الخدمة المطلوبة:" if services else "لا توجد خدمات مضافة حاليًا.")
        )
        edit_or_send(call, text, user_services_keyboard())
        bot.answer_callback_query(call.id)
        return

    if action.startswith("user_service:"):
        index = int(action.split(":")[1])
        services = load_data()["services"]

        if not 0 <= index < len(services):
            bot.answer_callback_query(call.id, "الخدمة غير موجودة.", show_alert=True)
            return

        service = services[index]

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            make_button("📩 طلب الخدمة", f"user_order:{index}", "success"),
            make_button("↩️ رجوع", "user_services", "primary")
        )

        edit_or_send(
            call,
            f"<b>🛍 {service.get('name', 'خدمة')}</b>\n\n"
            f"{service.get('description') or 'لا يوجد وصف.'}\n\n"
            f"💰 السعر: <b>{service.get('price') or 'غير محدد'}</b>",
            kb
        )

        bot.answer_callback_query(call.id)
        return

    if action.startswith("user_order:"):
        index = int(action.split(":")[1])
        services = load_data()["services"]

        if not 0 <= index < len(services):
            bot.answer_callback_query(call.id, "الخدمة غير موجودة.", show_alert=True)
            return

        username = (
            f"@{call.from_user.username}"
            if call.from_user.username
            else "لا يوجد"
        )

        for admin_id in load_data().get("admins", [ADMIN_ID]):
            try:
                bot.send_message(admin_id,
            f"<b>🆕 طلب جديد</b>\n\n"
            f"🛍 الخدمة: <b>{services[index].get('name', 'خدمة')}</b>\n"
            f"👤 العميل: {call.from_user.first_name}\n"
            f"🔗 المستخدم: {username}\n"
            f"🆔 ID: <code>{call.from_user.id}</code>"
                )
            except Exception:
                pass

        bot.answer_callback_query(
            call.id,
            "✅ تم إرسال الطلب للإدارة.",
            show_alert=True
        )
        return

    if action == "user_contact":
        data = load_data()
        kb = types.InlineKeyboardMarkup()
        kb.add(make_button("🏠 الرئيسية", "user_home", "primary"))
        edit_or_send(
            call,
            f"<b>📞 التواصل</b>\n\n{data['contact_text']}",
            kb
        )
        bot.answer_callback_query(call.id)
        return

    if action == "user_about":
        data = load_data()
        kb = types.InlineKeyboardMarkup()
        kb.add(make_button("🏠 الرئيسية", "user_home", "primary"))
        edit_or_send(
            call,
            f"<b>ℹ️ حول المتجر</b>\n\n{data['about_text']}",
            kb
        )
        bot.answer_callback_query(call.id)
        return

    # حماية الإدارة
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ غير مسموح لك.", show_alert=True)
        return

    if action == "admin_panel":
        edit_or_send(
            call,
            "<b>👑 لوحة الإدارة الاحترافية</b>\n\n"
            "يمكنك التحكم في كل شيء من هنا:",
            admin_main_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action == "admin_store_settings":
        edit_or_send(
            call,
            "<b>🏪 إعدادات المتجر</b>\n\nاختر ما تريد تعديله:",
            admin_store_settings_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action == "admin_buttons":
        edit_or_send(
            call,
            "<b>🔘 إدارة الأزرار الأساسية</b>\n\n"
            "اختر الزر الذي تريد التحكم به:",
            admin_buttons_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("manage_button:"):
        key = action.split(":")[1]
        item = get_button_config(key)

        if not item:
            bot.answer_callback_query(call.id, "الزر غير موجود.", show_alert=True)
            return

        visible_text = "ظاهر" if item.get("visible", True) else "مخفي"

        edit_or_send(
            call,
            f"<b>🔘 إدارة الزر</b>\n\n"
            f"الاسم: <b>{item['text']}</b>\n"
            f"الحالة: <b>{visible_text}</b>\n"
            f"الترتيب: <b>{item.get('order')}</b>\n"
            f"اللون: <b>{item.get('style')}</b>",
            single_button_manage_keyboard(key)
        )

        bot.answer_callback_query(call.id)
        return

    if action.startswith("btn_rename:"):
        key = action.split(":")[1]
        admin_state[call.from_user.id] = {
            "step": "rename_button",
            "key": key
        }
        bot.send_message(call.message.chat.id, "أرسل الاسم الجديد للزر:")
        bot.answer_callback_query(call.id)
        return

    if action.startswith("btn_color:"):
        key = action.split(":")[1]
        edit_or_send(
            call,
            "<b>🎨 اختر لون الزر:</b>",
            color_keyboard(key)
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("set_color:"):
        _, key, style = action.split(":")
        data = load_data()

        for item in data["buttons"]:
            if item["key"] == key:
                item["style"] = style
                break

        save_data(data)

        edit_or_send(
            call,
            "✅ تم تغيير لون الزر.",
            single_button_manage_keyboard(key)
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("btn_toggle:"):
        key = action.split(":")[1]
        data = load_data()

        for item in data["buttons"]:
            if item["key"] == key:
                item["visible"] = not item.get("visible", True)
                new_state = item["visible"]
                break
        else:
            new_state = False

        save_data(data)

        result = "✅ تم إظهار الزر." if new_state else "✅ تم إخفاء الزر."

        edit_or_send(
            call,
            result,
            single_button_manage_keyboard(key)
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("btn_order:"):
        key = action.split(":")[1]
        admin_state[call.from_user.id] = {
            "step": "button_order",
            "key": key
        }
        bot.send_message(
            call.message.chat.id,
            "أرسل رقم ترتيب الزر، مثال: 1 أو 2 أو 3 أو 4"
        )
        bot.answer_callback_query(call.id)
        return

    if action == "edit_store_name":
        admin_state[call.from_user.id] = {"step": "store_name"}
        bot.send_message(call.message.chat.id, "أرسل اسم المتجر الجديد:")
        bot.answer_callback_query(call.id)
        return

    if action == "edit_welcome_text":
        admin_state[call.from_user.id] = {"step": "welcome_text"}
        bot.send_message(call.message.chat.id, "أرسل رسالة الترحيب الجديدة:")
        bot.answer_callback_query(call.id)
        return

    if action == "edit_contact_text":
        admin_state[call.from_user.id] = {"step": "contact_text"}
        bot.send_message(call.message.chat.id, "أرسل نص أو رابط التواصل الجديد:")
        bot.answer_callback_query(call.id)
        return

    if action == "edit_about_text":
        admin_state[call.from_user.id] = {"step": "about_text"}
        bot.send_message(call.message.chat.id, "أرسل نص حول المتجر الجديد:")
        bot.answer_callback_query(call.id)
        return

    if action == "admin_services":
        edit_or_send(
            call,
            "<b>🛍 إدارة الخدمات</b>\n\nاختر العملية المطلوبة:",
            admin_services_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action == "service_add":
        admin_state[call.from_user.id] = {"step": "service_add_name"}
        bot.send_message(
            call.message.chat.id,
            "أرسل اسم الخدمة:\n\nللإلغاء أرسل /cancel"
        )
        bot.answer_callback_query(call.id)
        return

    if action == "service_edit":
        if not load_data()["services"]:
            bot.answer_callback_query(call.id, "لا توجد خدمات للتعديل.", show_alert=True)
            return

        edit_or_send(
            call,
            "<b>✏️ اختر الخدمة للتعديل:</b>",
            service_select_keyboard("edit_service")
        )
        bot.answer_callback_query(call.id)
        return

    if action == "service_delete":
        if not load_data()["services"]:
            bot.answer_callback_query(call.id, "لا توجد خدمات للحذف.", show_alert=True)
            return

        edit_or_send(
            call,
            "<b>🗑 اختر الخدمة للحذف:</b>",
            service_select_keyboard("delete_service")
        )
        bot.answer_callback_query(call.id)
        return

    if action == "service_list":
        services = load_data()["services"]

        if not services:
            text = "<b>📋 الخدمات</b>\n\nلا توجد خدمات."
        else:
            lines = ["<b>📋 الخدمات الحالية</b>\n"]

            for i, service in enumerate(services, 1):
                lines.append(
                    f"<b>{i}- {service.get('name', 'خدمة')}</b>\n"
                    f"📝 {service.get('description') or 'بلا وصف'}\n"
                    f"💰 {service.get('price') or 'بلا سعر'}\n"
                )

            text = "\n".join(lines)

        edit_or_send(call, text, admin_services_keyboard())
        bot.answer_callback_query(call.id)
        return

    if action.startswith("edit_service:"):
        index = int(action.split(":")[1])
        services = load_data()["services"]

        if not 0 <= index < len(services):
            bot.answer_callback_query(call.id, "الخدمة غير موجودة.", show_alert=True)
            return

        admin_state[call.from_user.id] = {
            "step": "service_edit_name",
            "index": index,
            "service": services[index].copy()
        }

        bot.send_message(
            call.message.chat.id,
            f"أرسل الاسم الجديد:\n"
            f"الاسم الحالي: <b>{services[index].get('name', '')}</b>"
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("delete_service:"):
        index = int(action.split(":")[1])
        data = load_data()

        if 0 <= index < len(data["services"]):
            deleted = data["services"].pop(index)
            save_data(data)

            edit_or_send(
                call,
                f"✅ تم حذف الخدمة:\n<b>{deleted.get('name', 'الخدمة')}</b>",
                admin_services_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, "الخدمة غير موجودة.", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        return

    if action == "admin_export":
        data = load_data()
        export_file = "boom_store_export.json"

        with open(export_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        with open(export_file, "rb") as file:
            bot.send_document(
                call.message.chat.id,
                file,
                caption="📦 نسخة احتياطية من إعدادات المتجر"
            )

        bot.answer_callback_query(call.id)
        return


    if action == "admin_manage_admins":
        if not is_owner(call.from_user.id):
            bot.answer_callback_query(call.id, "إدارة الأدمنات للمالك فقط.", show_alert=True)
            return
        edit_or_send(call, "<b>👥 إدارة الأدمنات</b>", admins_keyboard())
        bot.answer_callback_query(call.id)
        return

    if action == "admin_add_admin":
        if not is_owner(call.from_user.id):
            return
        admin_state[call.from_user.id] = {"step": "add_admin"}
        bot.send_message(call.message.chat.id, "أرسل ID الأدمن الجديد:")
        bot.answer_callback_query(call.id)
        return

    if action.startswith("admin_view:"):
        target = int(action.split(":")[1])
        edit_or_send(
            call,
            f"<b>👤 بيانات الأدمن</b>\n\nID: <code>{target}</code>",
            admin_details_keyboard(target)
        )
        bot.answer_callback_query(call.id)
        return

    if action.startswith("admin_remove:"):
        if not is_owner(call.from_user.id):
            return
        target = int(action.split(":")[1])
        data = load_data()
        if target != ADMIN_ID and target in data.get("admins", []):
            data["admins"].remove(target)
            save_data(data)
        edit_or_send(call, "✅ تم حذف الأدمن.", admins_keyboard())
        bot.answer_callback_query(call.id)
        return

    if action == "admin_broadcast":
        admin_state[call.from_user.id] = {"step": "broadcast"}
        bot.send_message(call.message.chat.id, "أرسل الرسالة الجماعية:")
        bot.answer_callback_query(call.id)
        return

    if action == "admin_stats":
        data = load_data()
        edit_or_send(
            call,
            f"<b>📊 الإحصائيات</b>\n\n"
            f"👥 المستخدمون: <b>{len(data.get('users', []))}</b>\n"
            f"👑 الأدمنات: <b>{len(data.get('admins', []))}</b>\n"
            f"🛍 الخدمات: <b>{len(data.get('services', []))}</b>",
            admin_main_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    if action == "admin_close":
        edit_or_send(call, "✅ تم إغلاق لوحة الإدارة.")
        bot.answer_callback_query(call.id)


@bot.message_handler(
    func=lambda message: (
        message.from_user.id == ADMIN_ID
        and message.from_user.id in admin_state
    )
)
def admin_steps(message):
    state = admin_state[call.from_user.id]
    text = (message.text or "").strip()

    if text == "/cancel":
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "✅ تم إلغاء العملية.",
            reply_markup=admin_main_keyboard()
        )
        return

    if not text:
        bot.send_message(message.chat.id, "أرسل نصًا صحيحًا.")
        return

    data = load_data()
    step = state["step"]

    if step == "add_admin":
        try:
            new_admin = int(text)
        except ValueError:
            bot.send_message(message.chat.id, "أرسل ID رقميًا صحيحًا.")
            return
        admins = data.setdefault("admins", [ADMIN_ID])
        if new_admin not in admins:
            admins.append(new_admin)
            save_data(data)
        admin_state.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "✅ تم إضافة الأدمن.", reply_markup=admins_keyboard())
        return

    if step == "broadcast":
        sent = 0
        failed = 0
        for target in data.get("users", []):
            try:
                bot.send_message(target, text)
                sent += 1
            except Exception:
                failed += 1
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            f"✅ انتهى الإرسال.\nنجح: {sent}\nفشل: {failed}",
            reply_markup=admin_main_keyboard()
        )
        return

    if step == "store_name":
        data["store_name"] = text
        save_data(data)
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "✅ تم تعديل اسم المتجر.",
            reply_markup=admin_store_settings_keyboard()
        )
        return

    if step == "welcome_text":
        data["welcome_text"] = text
        save_data(data)
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "✅ تم تعديل رسالة الترحيب.",
            reply_markup=admin_store_settings_keyboard()
        )
        return

    if step == "contact_text":
        data["contact_text"] = text
        save_data(data)
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "✅ تم تعديل نص التواصل.",
            reply_markup=admin_store_settings_keyboard()
        )
        return

    if step == "about_text":
        data["about_text"] = text
        save_data(data)
        admin_state.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "✅ تم تعديل نص حول المتجر.",
            reply_markup=admin_store_settings_keyboard()
        )
        return

    if step == "rename_button":
        key = state["key"]

        for item in data["buttons"]:
            if item["key"] == key:
                item["text"] = text
                break

        save_data(data)
        admin_state.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "✅ تم تغيير اسم الزر.",
            reply_markup=single_button_manage_keyboard(key)
        )
        return

    if step == "button_order":
        try:
            order = int(text)
        except ValueError:
            bot.send_message(message.chat.id, "أرسل رقمًا صحيحًا فقط.")
            return

        key = state["key"]

        for item in data["buttons"]:
            if item["key"] == key:
                item["order"] = order
                break

        save_data(data)
        admin_state.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "✅ تم تغيير ترتيب الزر.",
            reply_markup=single_button_manage_keyboard(key)
        )
        return

    if step == "service_add_name":
        state["name"] = text
        state["step"] = "service_add_description"

        bot.send_message(
            message.chat.id,
            "أرسل وصف الخدمة.\nأرسل نقطة . إذا لا تريد وصفًا."
        )
        return

    if step == "service_add_description":
        state["description"] = "" if text == "." else text
        state["step"] = "service_add_price"

        bot.send_message(
            message.chat.id,
            "أرسل سعر الخدمة.\nأرسل نقطة . إذا لا تريد سعرًا."
        )
        return

    if step == "service_add_price":
        data["services"].append({
            "name": state["name"],
            "description": state["description"],
            "price": "" if text == "." else text
        })

        save_data(data)
        admin_state.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "✅ تم إضافة الخدمة.",
            reply_markup=admin_services_keyboard()
        )
        return

    if step == "service_edit_name":
        state["service"]["name"] = text
        state["step"] = "service_edit_description"

        bot.send_message(
            message.chat.id,
            "أرسل الوصف الجديد.\nأرسل نقطة . لحذف الوصف."
        )
        return

    if step == "service_edit_description":
        state["service"]["description"] = "" if text == "." else text
        state["step"] = "service_edit_price"

        bot.send_message(
            message.chat.id,
            "أرسل السعر الجديد.\nأرسل نقطة . لحذف السعر."
        )
        return

    if step == "service_edit_price":
        state["service"]["price"] = "" if text == "." else text
        index = state["index"]

        if 0 <= index < len(data["services"]):
            data["services"][index] = state["service"]
            save_data(data)
            result = "✅ تم تعديل الخدمة."
        else:
            result = "❌ تعذر تعديل الخدمة."

        admin_state.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            result,
            reply_markup=admin_services_keyboard()
        )


@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(message.chat.id, "أرسل /start لفتح المتجر.")



class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Python Bot is running".encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server is running on port {port}")
    server.serve_forever()


def setup_commands():
    bot.set_my_commands([
        types.BotCommand("start", "فتح المتجر")
    ])

    for admin_id in load_data().get("admins", [ADMIN_ID]):
        try:
            bot.set_my_commands(
                [
                    types.BotCommand("start", "فتح المتجر"),
                    types.BotCommand("admin", "لوحة الإدارة")
                ],
                scope=types.BotCommandScopeChat(admin_id)
            )
        except Exception as error:
            print("Could not set admin commands:", error)


if __name__ == "__main__":
    print("Boom Store Pro Bot is running...")
    bot.remove_webhook()
    setup_commands()
    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
