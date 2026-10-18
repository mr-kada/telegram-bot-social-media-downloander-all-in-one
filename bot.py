import requests
from telethon import TelegramClient, events, Button, errors, functions, types
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ReplyKeyboardHide
from telethon.tl.functions.messages import ExportChatInviteRequest

from datetime import datetime, timedelta
import string, random, os, json, sqlite3, re, asyncio, math, lzma, shutil


from myfatoorah_payApi import check_invoice_status_myfatoorah, create_invoice_myfatoorah
from scripts.Instagram_API import download_instagram_post_imageV2
from scripts.Jaco_API import download_jaco_video
from scripts.Likee_API import LikeeDownload
from scripts.Multi_API import multi_download_video
from scripts.Pinterest_API import download_pinterest_video
from scripts.Snapchat_info import scrape_snapchat_profile
from scripts.Tiktok_API import download_tiktok_video
from scripts.Tiktok_Acount import get_tiktok_account_info, process_json
from scripts.Tiktok_img_API import download_tiktok_image
from scripts.Tiktok_info import fetch_tiktok_data
from scripts.Tiktok_infoV2 import get_tiktok_infoV2
from scripts.Twitter_API import TwitterDownload
from scripts.Twitter_info import extract_tweet_data
from scripts.Twitter_infoV2 import GetTwitterInfoV2
from scripts.Youtube_API import get_video_length_and_size, youtube_download_up_to_720p
from scripts.Facebook_API import facebook_download_best_quality_video
from database_function import create_table_if_not_existsV2

from database_function import bot_users_columns, bot_settings_columns, ad_buttons_columns, vip_subscription_columns, limited_offer_columns, subscription_history_columns, download_history_columns, join_channels_columns
from scripts.snapchat_API import SnapchatDownload, download_media, get_json, get_snapchat_info
from scripts.save_files import download_file


# READ CONFIGS
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)



# BOT CONFIGS
api_id = 1724716
api_hash = '00b2d8f59c12c1b9a4bc63b70b461b2f'
bot_token = config["TEST_BOT_TOKEN"] # config["BOT_TOKEN"]


bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
bot.start()


# CONNECT TO DATABASE
database = sqlite3.connect('database.db')
cursor = database.cursor()


# CONFIGS
bot_configs = json.load(open('bot_configs.json', encoding='utf-8'))


# VARs
OWNER_ID = 691459768 #7616544351

# Define items per page
page_data = {}
PAGE_SIZE = 5
ITEMS_PER_PAGE = 2

download_list = []
# channels_list = ['https://t.me/xckrypton']


###########################
async def DeleteEvent(event):
    try:
        await event.delete()
    except:pass


async def generate_random_id(length=6):
    characters = string.ascii_uppercase + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id


async def DeleteFile(path):
    try:
        os.remove(path)
    except:pass


async def SaveJsonData(data):
    global bot_configs

    with open('bot_configs.json', mode='w', encoding='utf-8') as JsonFile:
        json.dump(data, JsonFile, ensure_ascii=False, indent=4)

    bot_configs = data


async def set_bot_commands():
    commands = [
        types.BotCommand(command="start", description="Start the bot"),
        types.BotCommand(command="developer", description="Get Bot Developer information")
    ]

    await bot(functions.bots.SetBotCommandsRequest(
        commands=commands,
        scope=types.BotCommandScopeDefault(),
        lang_code='en'
    ))


async def hide_keyboard(event):
    hide = await bot.send_message(
        entity=event.chat_id,
        message='__⏳ Processing__',
        buttons=ReplyKeyboardHide(selective=True))
    try:
        await hide.delete()
    except:pass


async def open_and_print_json(file_path):
    try:
        with lzma.open(file_path, mode='rt', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        return None


#############################
# ADMIN PANEL
@bot.on(events.CallbackQuery(data='admin_panel'))
async def BotAdminPanel(event):

    await DeleteEvent(event)
    notify_login_text = "إشعار الدخول ✅" if bot_configs["is_notify_login_enabled"] else "إشعار الدخول ❌"
    
    buttons = [
        [Button.inline(notify_login_text, b'toggle_notify_login')],
        [Button.inline('💳 خطط الاشتراكات', 'vip_show'), Button.inline('🎁 عروض و خصومات', 'discounts_show')],
        [Button.inline('📌 الاشتراك الاجباري', 'first_join'), Button.inline('📉 عمليات التحميل', 'daily_limits_show')],
        [Button.inline('🛠️ انشاء أزرار للاشهار', 'ad_buttons')],
        [Button.inline('📢 اذاعة لجميع المستخدمين', 'broadcast')],
        [Button.inline('💰 اضافة/حذف رصيد', 'editUser_price'), Button.inline('🔎 بحث عن عميل', 'getUser_byID')],
        [Button.inline('🎁 تعديل جائزة رابط الدعوة', 'editLink_price')],
        [Button.inline("⚙️ إعدادات البوت", b'settings_section'), Button.inline("👤 قسم الأدمنية", b'admin_section')],
        [Button.inline('📊 احصائيات متقدمة', 'all_statistics')],
        [Button.inline('🏷 أكثر الخدمات طلبا', 'most_services_needed')],
        [Button.inline('🕵️‍♂️ اخر عمليات التحميل', 'last_download'), Button.inline('🏆 أكثر من قام بالتحميل', 'most_download')],
        [Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]
    ]

    await event.respond(f'''__
👋 مرحبًا بك في لوحة المشرف!
                        
🎯 اختر الأمر الذي ترغب في تنفيذه من القائمة أدناه.
__''', buttons=buttons)
    


@bot.on(events.NewMessage(pattern='/start'))
async def BotStart(event):

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    try:
        await hide_keyboard(event)
    except:pass

    try:
        await set_bot_commands()
    except Exception as error:print (error)

    try:
        await create_table_if_not_existsV2(cursor, database, 'bot_users', bot_users_columns)
        await create_table_if_not_existsV2(cursor, database, 'bot_settings', bot_settings_columns)
        await create_table_if_not_existsV2(cursor, database, 'ad_buttons', ad_buttons_columns)
        await create_table_if_not_existsV2(cursor, database, 'vip_subscription', vip_subscription_columns)
        await create_table_if_not_existsV2(cursor, database, 'limited_offer', limited_offer_columns)
        await create_table_if_not_existsV2(cursor, database, 'subscription_history', subscription_history_columns)
        await create_table_if_not_existsV2(cursor, database, 'download_history', download_history_columns)
        await create_table_if_not_existsV2(cursor, database, 'join_channels', join_channels_columns)
    
    except Exception as error:print ('Database error:', error)


    bot_data_db = cursor.execute(f"SELECT * FROM bot_settings WHERE setting_id = 1").fetchone()
    if bot_data_db == None:
        cursor.execute("""
            INSERT INTO bot_settings (setting_id, download_limit, link_reward)
            VALUES (?, ?, ?)
        """, (1, 10, '0.01'))
        database.commit()


    try:
        event.data
        can_pass = False
    except:can_pass = True


    user_entity = await bot.get_entity(event.chat_id)
    if not event.is_group and not event.is_channel and can_pass == True:
        # CHECK IF USER ALREADY IN DATABASE / REFFERALED
        user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
        user_data = cursor.fetchone()
        refferal_from = str(event.message.message).replace('/start', '').strip()
        if user_data == None:
            refferal_from_data = None
            if str(refferal_from).isdigit():
                refferal_from_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {int(refferal_from)}')
                refferal_from_data = cursor.fetchone()

            refferal_from_id = None
            if refferal_from_data != None:
                refferal_from_id = refferal_from_data[0]

                # Add balance to link owner then notify him
                bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
                bot_settings_data = cursor.fetchone()
                new_balance = float(refferal_from_data[1]) + float(bot_settings_data[2])

                cursor.execute(
                    "UPDATE bot_users SET balance = ? WHERE user_id = ?",
                    (new_balance, refferal_from_id)
                )

                database.commit()

                try:
                    await bot.send_message(int(refferal_from_id), message=f'''__
🎉 تهانينا!

لقد انضم شخص جديد عبر رابط دعوتك، وحصلت على: {bot_settings_data[2]}$
__''')
                except:pass


            try:
                get_user_data = await bot.get_entity(event.chat_id)
                first_name = get_user_data.first_name
                last_name = get_user_data.last_name
            except:
                first_name = None
                last_name = None

            # NEW USER
            cursor.execute(
                """
                INSERT INTO bot_users 
                (user_id, balance, is_vip, refferal_from, added_date, today_downloads, last_download_date, banned, firstname, lastname) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event.chat_id, 0.0, None, refferal_from_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, None, None, first_name, last_name)
            )
            database.commit()


            # LOGIN - NOTIFY OWNER
            if bot_configs["is_notify_login_enabled"]:
                try:
                    user_entity = await bot.get_entity(event.chat_id)
                    await bot.send_message(OWNER_ID, f'''__
🚨 تم دخول شخص جديد للبوت الخاص بك :
                                    
الاسم: {user_entity.first_name}
المعرف: @{user_entity.username}
ID: `{user_entity.id}`
__''')
                except:pass


    user_data_ = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
    user_data_ = cursor.fetchone()

    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()

    if user_data_[7] == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return
    
    if user_data_[8] == None:
        try:
            get_user_data = await bot.get_entity(event.chat_id)
            first_name = get_user_data.first_name
            last_name = get_user_data.last_name
        except:
            first_name = None
            last_name = None

        cursor.execute(
            "UPDATE bot_users SET firstname = ?, lastname = ? WHERE user_id = ?",
            (first_name, last_name, event.chat_id)
        )
        database.commit()
    
    if not user_data_[2]:
        limit = f'{user_data_[5]}/{bot_settings_data[1]}'
    else:
        limit = f'غير محدود'

    buttons = [
        [Button.inline(f'الرصيد : {round(float(user_data_[1]), 2)}$ | محاولات التحميل : {limit}', 'short_info')],
        [
            Button.inline("🎬 تحميل من يوتيوب", b'download_youtube'),
            Button.inline("📘 تحميل من فيسبوك", b'download_facebook')
        ],
        [
            Button.inline("📸 تحميل من انستغرام", b'download_instagram'),
            Button.inline("🎥 تحميل من تيك توك", b'download_tiktok')
        ],
        [
            Button.inline("📌 تحميل من بنترست", b'download_pinterest'),
            Button.inline("👻 تحميل من سناب شات", b'download_snapchat')
        ],
        [   
            Button.inline("🎞️ تحميل من لايكي", b'download_likee'),
            Button.inline("🖥️ تحميل من Jaco", b'download_jaco')
        ],
        [
            Button.inline("🐦 تحميل من تويتر", b'twitter_section')
        ],
        [
            Button.inline("👨🏻‍💻 كشف حساب تيك توك", b'tiktok_account')
        ],
        [
            Button.inline('📣 رابط الدعوة', 'refferal_link')
        ],
        [
            Button.inline('👤 حسابي', 'show_profile'),
            Button.inline('📩 تواصل مع الدعم', 'contact_support')
        ],
        [
            Button.inline('⭐ اشتراك VIP', 'buy_vip')
        ]
    ]

    ad_buttons_data = cursor.execute('SELECT * FROM ad_buttons')
    ad_buttons_data = cursor.fetchall()

    if len(ad_buttons_data) != 0:
        for item in ad_buttons_data:
            buttons.append([Button.url(item[1], item[2])])

    admins_list = bot_configs.get('admins')
    if event.chat_id == OWNER_ID or event.chat_id == 978571497 or event.chat_id in admins_list:
        buttons.append([Button.inline('🛠️ لوحة المشرف', 'admin_panel')])


    channels_list = cursor.execute('SELECT * FROM join_channels')
    channels_list = cursor.fetchall()
    if not event.is_group and not event.is_channel:
        # CHECK IF USER JOINED ALL CHANNELS
        user_joined_all = True
        for channel in channels_list:
            try:
                check_user = await bot(GetParticipantRequest(channel=int(channel[0]), participant=event.chat_id))
            except errors.UserNotParticipantError:
                user_joined_all = False
                break
            except Exception as error:pass


        if user_joined_all == True:
            await event.respond(f'''__
✨ مرحبًا بك {user_entity.first_name}! 😊

📥 مع هذا البوت، يمكنك تحميل الفيديوهات والصور من منصات متعددة بكل سهولة!

⚡ ما عليك سوى إرسال الرابط هنا، وسنقوم بجلب المحتوى لك بسرعة! 🚀


💾 استمتع بالتحميل السريع والمباشر! 🔥
__''', buttons=buttons)
            
        else:
            channels_buttons = []
            for channel in channels_list:
                channels_buttons.append([Button.url(f'{channel[1]}', channel[2])])
            
            bot_data = await bot.get_me()
            channels_buttons.append([Button.url('✅ تحقق', f'https://t.me/{bot_data.username}?start=start')])
            await event.respond('__اشترك في قناتنا أولا ثم اضغط تحقق__', buttons=channels_buttons)



# BACK TO MENU
@bot.on(events.CallbackQuery(data='back_to_menu'))
async def BackToMenu(event):

    await DeleteEvent(event)
    await BotStart(event)



# BACK TO ADMIN PANEL 
@bot.on(events.CallbackQuery(data='back_to_adminpanel'))
async def BackToAdminPanel(event):
    await DeleteEvent(event), await BotAdminPanel(event)



# BACK TO SUB
@bot.on(events.CallbackQuery(data='back_to_sub'))
async def BackToSub(event):
    await DeleteEvent(event), await VIP_SHOW(event)



# BACK TO OFFER
@bot.on(events.CallbackQuery(data='back_to_offer'))
async def BackToOffer(event):
    await DeleteEvent(event), await discounts_show(event)


# BACK TO STATISTICS
@bot.on(events.CallbackQuery(data='back_to_statistics'))
async def BackToStatistics(event):
    await DeleteEvent(event), await AllStatistics(event)


# BACK TO STATISTICS
@bot.on(events.CallbackQuery(data='back_to_join_channels'))
async def BackToJoinChannel(event):
    await DeleteEvent(event), await FirstJoin(event)


# BACK TO Admin Section
@bot.on(events.CallbackQuery(data='back_to_admin_section'))
async def BackToAdminSection(event):
    await DeleteEvent(event), await AdminSection(event)




# Enabled/Disabled Notify Login
@bot.on(events.CallbackQuery(data='toggle_notify_login'))
async def ToggleNotifyLogin(event):
    global bot_configs

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_notify_login_enabled", False)
    bot_configs["is_notify_login_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs)

    # Send a response message to the user
    status_message = "تم تفعيل إشعار الدخول!" if is_enabled else "تم تعطيل إشعار الدخول!"
    await event.answer(status_message), await BotAdminPanel(event)



# REFFERAL LINK
@bot.on(events.CallbackQuery(data='refferal_link'))
async def RefferalLink(event):

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    await DeleteEvent(event)

    user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
    user_data = cursor.fetchone()

    if user_data[7] == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return

    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()

    bot_data, reward_link_owner = await bot.get_me(), bot_settings_data[2]

    buttons = [[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]]
    await event.respond(f'''__
🎉 رابط دعوتك الخاص بانتظارك! شاركه الآن واحصل على مكافآت رائعة:

💰 عند مشاركة رابط الدعوة الخاص بك، ستحصل على: {reward_link_owner}$

https://t.me/{bot_data.username}?start={event.chat_id}
__''', buttons=buttons)




# CONTACT SUPPORT
@bot.on(events.CallbackQuery(data='contact_support'))
async def ContactSupport(event):

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    await DeleteEvent(event)

    user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
    user_data = cursor.fetchone()

    if user_data[7] == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            buttons = [[Button.text('الغاء التذكرة', resize=True)]]
            await conv.send_message('__أرسل رسالة التي تريد ارسالها للدعم:__', buttons=buttons)
            the_message = await conv.get_response()

        if the_message.message == 'الغاء التذكرة':
            await event.respond('__تم الغاء التذكرة__')
        else:
            reply_buttons = [[Button.inline('ارسال رد', f'ownerReply_{event.chat_id}')]]
            try:
                await bot.forward_messages(entity=OWNER_ID, messages=the_message)
                await bot.send_message(entity=OWNER_ID, message='للرد على هذه الرسالة اضغط هنا:', buttons=reply_buttons)
            except:pass
            await event.respond('__تم ارسال الرسالة, سوف تتلقى رد في أقرب وقت__')
        
        await hide_keyboard(event)
    except Exception as error:print(error)
    await BotStart(event)



# REPLY ON MESSAGE
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'ownerReply_')))
async def OwnerReply(event):

    user_id = int(str(event.data.decode()).replace('ownerReply_', '').strip())
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            buttons = [[Button.text('الغاء الرد', resize=True)]]
            await conv.send_message('__أرسل رسالة التي تريد ارسالها:__', buttons=buttons)
            the_message = await conv.get_response()

        if the_message.message == 'الغاء الرد':
            await event.respond('__تم الغاء الرد__')
        else:
            try:
                await bot.send_message(entity=user_id, message=the_message)
            except:pass

            buttons = [[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]]
            await event.respond('__تم ارسال الرسالة, بنجاح__', buttons=buttons)
        
        await hide_keyboard(event)
    except:pass



# SHOW PROFILE
@bot.on(events.CallbackQuery(data='show_profile'))
async def ShowProfile(event):

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    await DeleteEvent(event)

    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()

    user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {event.chat_id}")
    user_data = cursor.fetchone()

    if user_data[7] == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return

    balance, joined_date = user_data[1], user_data[4]

    if not user_data[2]:
        limit = f'{user_data[5]}/{bot_settings_data[1]}'
        subscription_active = 'مجانية'
        subscription_date = 'غير مشترك'
        subscription_expires = 'غير مشترك'
    else:
        limit = f'غير محدود'
        subscription_active = 'مدفوعة'
        subscription_date = user_data[2]

        expire_time = datetime.strptime(str(user_data[2]), "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()

        time_remaining = expire_time - current_time
        days = time_remaining.days

        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        subscription_expires = f'{days} يوم، {hours} ساعة، {minutes} دقيقة'

    bot_data = await bot.get_me()
    buttons = [
        [Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]
    ]

    await event.respond(f'''__
✨ **تفاصيل حسابك**

🆔 آيدي: `{event.chat_id}`
💰 رصيدك: {round(float(balance), 2)}$

⭐ العضوية: {subscription_active}
📆 تاريخ انتهاء العضوية: {subscription_date}
⏳ المدة المتبقية لانتهاء العضوية: {subscription_expires}

📅 تاريخ انضمامك للبوت: {joined_date}
🔍 محاولات التحميل اليومية المتبقية: {limit}
__''', buttons=buttons)




# VIP show
@bot.on(events.CallbackQuery(data='vip_show')) 
async def VIP_SHOW(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    vip_subscription = cursor.execute('SELECT * FROM vip_subscription')
    vip_subscription = cursor.fetchall()

    vip_subscription_active = cursor.execute("SELECT * FROM vip_subscription WHERE status = 'active'")
    vip_subscription_active = cursor.fetchall()

    vip_subscription_unactive = cursor.execute("SELECT * FROM vip_subscription WHERE status = 'unactive'")
    vip_subscription_unactive = cursor.fetchall()

    vip_bot_users = cursor.execute("SELECT * FROM bot_users WHERE is_vip IS NOT NULL")
    vip_bot_users = cursor.fetchall()

    await DeleteEvent(event)

    buttons = [
        [Button.inline('📋 عرض جميع الخطط', 'show_all_vip_sub')],
        [Button.inline(f'✅ الخطط النشيطة ({len(vip_subscription_active)})', 'activeVIP'), Button.inline(f'❌ الخطط غير النشيطة ({len(vip_subscription_unactive)})', 'unactiveVIP')],
        [Button.inline('➕ اضافة خطة جديدة', 'add_vip_sub')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]


    await event.respond(f'''__
🔧 **إدارة خطط الاشتراك**  

📊 **إحصائيات عامة**  
📋 إجمالي الخطط: {len(vip_subscription)}
✅ الخطط النشطة: {len(vip_subscription_active)}
❌ الخطط غير النشطة: {len(vip_subscription_unactive)}
👥 إجمالي المشتركين النشطين: {len(vip_bot_users)}


🔽 **اختر ما تريد عرضه:**
__''', buttons=buttons)



# Show all VIP subscriptions with Pagination
@bot.on(events.CallbackQuery(data='activeVIP'))
async def activeVIP(event):

    cursor.execute("SELECT * FROM vip_subscription WHERE status = 'active'")
    vip_subscription = cursor.fetchall()

    # Get the first subscription based on the id or show the first if none selected
    if len(vip_subscription) == 0:
        await event.answer('لا توجد خطط لعرضها', alert=True)
    else:
        first_sub = vip_subscription[0]
        item = first_sub
        await display_vip_subscription(event, item[0], is_status=True, status_type='active')



# Show all VIP subscriptions with Pagination
@bot.on(events.CallbackQuery(data='unactiveVIP'))
async def unactiveVIP(event):

    cursor.execute("SELECT * FROM vip_subscription WHERE status = 'unactive'")
    vip_subscription = cursor.fetchall()

    # Get the first subscription based on the id or show the first if none selected
    if len(vip_subscription) == 0:
        await event.answer('لا توجد خطط لعرضها', alert=True)
    else:
        first_sub = vip_subscription[0]
        item = first_sub
        await display_vip_subscription(event, item[0], is_status=True, status_type='unactive')



# Show all VIP subscriptions with Pagination
@bot.on(events.CallbackQuery(data='show_all_vip_sub'))
async def show_all_vip_sub(event):

    cursor.execute('SELECT * FROM vip_subscription')
    vip_subscription = cursor.fetchall()

    # Get the first subscription based on the id or show the first if none selected
    if len(vip_subscription) == 0:
        await event.answer('لا توجد خطط لعرضها', alert=True)
    else:
        first_sub = vip_subscription[0]
        item = first_sub
        await display_vip_subscription(event, item[0])



# Function to display a specific VIP subscription
async def display_vip_subscription(event, sub_id, is_status=False, status_type=''):

    await DeleteEvent(event)
    cursor = database.cursor()

    # Query to get the specific subscription by id
    if is_status == False:
        cursor.execute('SELECT * FROM vip_subscription WHERE id = ?', (sub_id,))
        item = cursor.fetchone()
    else:
        cursor.execute('SELECT * FROM vip_subscription WHERE id = ? AND status = ?', (sub_id, status_type,))
        item = cursor.fetchone()

    if item:
        if item[3] == 'active':
            status = 'نشيطة ✅'
        else:
            status = 'غير نشيطة ❌'

        item_display = f"""
📅 حالة الخطة : {status}
💰 سعر الاشتراك: {item[1]}$
⏳ المدة الاشتراك بالشهر: {item[2]}
"""

        # Prepare the buttons for Next and Previous navigation
        buttons = [[
            Button.inline('🛠 تعديل السعر', f'VipEditPrice_{item[0]}'), 
            Button.inline('📅 تعديل الشهور', f'VipEditMonth_{item[0]}')
        ]]

        if item[3] == 'active':
            buttons.append([Button.inline('❌ ايقاف تنشيط الخطة', f'VipActive_{item[0]}')])
        else:
            buttons.append([Button.inline('✅ اعادة تنشيط الخطة', f'VipUnActive_{item[0]}')])

        nextback_buttons = []

        # Get Previous Item (if exists)
        if is_status == False:
            cursor.execute('SELECT id FROM vip_subscription WHERE id < ? ORDER BY id DESC LIMIT 1', (item[0],))
            prev_item = cursor.fetchone()

            if prev_item:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevSub_{prev_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevSub_none'))

        else:
            cursor.execute('SELECT id FROM vip_subscription WHERE status = ? AND id < ? ORDER BY id DESC LIMIT 1', (status_type, item[0]))
            prev_item = cursor.fetchone()

            if prev_item:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevSub{status_type}_{prev_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevSub{status_type}_none'))

        # Get Next Item (if exists)
        if is_status == False:
            cursor.execute('SELECT id FROM vip_subscription WHERE id > ? ORDER BY id ASC LIMIT 1', (item[0],))
            next_item = cursor.fetchone()

            if next_item:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextSub_{next_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextSub_none'))
        else:
            cursor.execute('SELECT id FROM vip_subscription WHERE status = ? AND id > ? ORDER BY id ASC LIMIT 1', (status_type, item[0]))
            next_item = cursor.fetchone()

            if next_item:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextSub{status_type}_{next_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextSub{status_type}_none'))


        buttons.append(nextback_buttons)

        # Back to main menu button
        buttons.append([Button.inline('🔙 رجوع', data='back_to_sub')])

        # Send the current item with navigation buttons
        await event.respond(f"__📋 الخطة\n{item_display}\n\n🔽 اختر ما تريد:__", buttons=buttons)
    else:
        await event.respond("لا توجد خطة اشتراك بهذا الرقم.")



# Handle "Next" button press to show the next subscription
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextSub_')))
async def next_item(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id)
    except:await event.answer('لا مزيد من الخطط', alert=True)



# Handle "Previous" button press to show the previous subscription
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevSub_')))
async def prev_item(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id)
    except:await event.answer('لا مزيد من الخطط', alert=True)



@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextSubactive_')))
async def next_item2(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id, is_status=True, status_type='active')
    except Exception as e:
        await event.answer('لا مزيد من الخطط', alert=True)


@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevSubactive_')))
async def prev_item2(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id, is_status=True, status_type='active')
    except Exception as e:
        await event.answer('لا مزيد من الخطط', alert=True)



@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextSubunactive_')))
async def next_item3(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id, is_status=True, status_type='unactive')
    except Exception as e:
        await event.answer('لا مزيد من الخطط', alert=True)


@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevSubunactive_')))
async def prev_item3(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_vip_subscription(event, sub_id, is_status=True, status_type='unactive')
    except Exception as e:
        await event.answer('لا مزيد من الخطط', alert=True)



# VipActive_
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'VipActive_')))
async def VipActive_(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        cursor.execute(f"UPDATE vip_subscription SET status = 'unactive' WHERE id = {sub_id}")
        database.commit()
        await display_vip_subscription(event, sub_id)
    except:await event.answer('لا توجد هذه الخطة', alert=True)



# VipUnActive_
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'VipUnActive_')))
async def VipUnActive_(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        cursor.execute(f"UPDATE vip_subscription SET status = 'active' WHERE id = {sub_id}")
        database.commit()
        await display_vip_subscription(event, sub_id)
    except:await event.answer('لا توجد هذه الخطة', alert=True)




# Add Vip Sub
@bot.on(events.CallbackQuery(data='add_vip_sub'))
async def add_vip_sub(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل عدد أشهر الخطة:__')
            months = (await conv.get_response()).message

            await conv.send_message('__أرسل السعر الخطة:__')
            price = (await conv.get_response()).message

        if str(months).isdigit():
            try:
                price = float(price)
            except:
                await event.respond('__السعر يجب أن يكون رقما!__')
                return
            
            # ADD VIP SUB
            insert_sql = f"INSERT INTO vip_subscription (price, months, status) VALUES ({float(price)}, {int(months)}, 'active');"
            cursor.execute(insert_sql)
            database.commit()

        else:
            await event.respond('الأشهر يجب أن يكون رقما!__')

    except:pass
    await VIP_SHOW(event)


# Vip Edit Price
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'VipEditPrice_')))
async def VipEditPrice(event):

    await DeleteEvent(event)
    sub_id = int(event.data.decode().split('_')[1])
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل السعر الجديد:__')
            new_price = (await conv.get_response()).message

        try:
            new_price = float(new_price)
            cursor.execute(f"UPDATE vip_subscription SET price = {new_price} WHERE id = {sub_id}")
            database.commit()

            await display_vip_subscription(event, sub_id)
        except:
            await event.respond('__السعر يجب أن يكون رقما!__')

    except:pass



# Vip Edit Month
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'VipEditMonth_')))
async def VipEditMonth(event):

    await DeleteEvent(event)
    sub_id = int(event.data.decode().split('_')[1])
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل المدة الجديد بالشهور:__')
            new_month = (await conv.get_response()).message

        if str(new_month).isdigit():
            cursor.execute(f"UPDATE vip_subscription SET months = {new_month} WHERE id = {sub_id}")
            database.commit()

            await display_vip_subscription(event, sub_id)
        else:
            await event.respond('الشهور يجب أن يكون رقما!__')

    except:pass




# Discounts Show
@bot.on(events.CallbackQuery(data='discounts_show')) 
async def discounts_show(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)

    limited_offer = cursor.execute('SELECT * FROM limited_offer')
    limited_offer = cursor.fetchall()

    limited_offer_active = cursor.execute("SELECT * FROM limited_offer WHERE status = 'active'")
    limited_offer_active = cursor.fetchall()

    limited_offer_users = 0
    for offer in limited_offer:
        limited_offer_users += int(offer[8])


    last_offer = ''
    if len(limited_offer_active) != 0:
        offer_data = limited_offer_active[-1]

        target_date = datetime.strptime(str(offer_data[6]), "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()

        # Calculate the time difference
        time_difference = target_date - current_time

        if time_difference.total_seconds() > 0:
            remaining_days = time_difference.days
            remaining_seconds = time_difference.seconds
            remaining_hours = remaining_seconds // 3600
            remaining_minutes = (remaining_seconds % 3600) // 60
            remains = f'{remaining_days} يوم, {remaining_hours} ساعة, {remaining_minutes} ثانية'
        else:
            remains = 'العرض انتهى'
            cursor.execute(f"UPDATE limited_offer SET status = 'unactive' WHERE id = {offer_data[0]}")
            database.commit()

        last_offer = f'''🏷️ اسم العرض: {offer_data[1]}
🔢 كود العرض: {offer_data[2]}
💸 قيمة الخصم: {offer_data[3]}%

⏳ المدة: {offer_data[4]} يوم
📅 ينتهي بعد: {remains}'''
    
    else:
        last_offer = 'لا يوجد أي عروض'


    limited_offer_unactive = cursor.execute("SELECT * FROM limited_offer WHERE status = 'unactive'")
    limited_offer_unactive = cursor.fetchall()


    buttons = [
        [Button.inline('📊 إحصائيات العروض', 'offers_statistics')],
        [
            Button.inline(f'✅ الخطط النشيطة ({len(limited_offer_active)})', 'activeOffers'), 
            Button.inline(f'❌ الخطط غير النشيطة ({len(limited_offer_unactive)})', 'unactiveOffers')
        ],
        [Button.inline('➕ اضافة عرض', 'add_limited_offer')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    await event.respond(f'''__
🔧 **إدارة العروض و الخصومات**  

📊 **إحصائيات عامة**  
📋 إجمالي العروض: {len(limited_offer)}
✅ العروض النشيطة: {len(limited_offer_active)}
❌ العروض المنتهية : {len(limited_offer_unactive)}
👥 إجمالي الاستخدامات: {limited_offer_users}


🔥 **احدث العروض النشيطة**
--------------------------------
{last_offer}
--------------------------------
__''', buttons=buttons)




@bot.on(events.CallbackQuery(data='offers_statistics'))
async def offers_statistics(event):
    # Start with the first page
    await show_offers_page(event, current_page=0)



@bot.on(events.CallbackQuery(data=re.compile(r'OffersUsagePage_(\d+)')))
async def paginate_offers(event):
    # Extract the current page from callback data
    current_page = int(event.data_match.group(1))
    await show_offers_page(event, current_page)



async def show_offers_page(event, current_page):

    # Calculate offset for pagination
    offset = current_page * ITEMS_PER_PAGE

    # Fetch offers from the database
    cursor.execute(
        "SELECT * FROM limited_offer LIMIT ? OFFSET ?", (ITEMS_PER_PAGE, offset)
    )
    limited_offers = cursor.fetchall()

    if len(limited_offers) == 0:
        await event.answer('لا توجد عروض لعرضها', alert=True)
        return


    await DeleteEvent(event)

    # Create the message with offers
    offer_msg = '**📊 إحصائيات العروض**\n\n'
    for offer in limited_offers:
        offer_name, usage_count = offer[1], offer[8]
        offer_msg += f'''__🏷️ اسم العرض: {offer_name}
👥 عدد المستخدمين : {usage_count}__

'''

    # Fetch total number of offers for pagination controls
    cursor.execute("SELECT COUNT(*) FROM limited_offer")
    total_offers = cursor.fetchone()[0]

    # Calculate total pages
    total_pages = (total_offers + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    offer_msg += f'\n📄 الصفحة: {current_page + 1}/{total_pages}'

    # Ensure "back" and "next" buttons are always visible
    buttons = [
        [
            Button.inline('« السابق', f'OffersUsagePage_{max(0, current_page - 1)}'),
            Button.inline('التالي »', f'OffersUsagePage_{min(total_pages - 1, current_page + 1)}'),
        ],
        [Button.inline('🔙 Back', 'back_to_offer')]
    ]

    # Add buttons to the message
    await event.respond(offer_msg, buttons=buttons)




# Show all VIP subscriptions with Pagination
@bot.on(events.CallbackQuery(data='activeOffers'))
async def activeOffers(event):

    cursor.execute("SELECT * FROM limited_offer WHERE status = 'active'")
    limited_offers = cursor.fetchall()

    # Get the first subscription based on the id or show the first if none selected
    if len(limited_offers) == 0:
        await event.answer('لا توجد عروض لعرضها', alert=True)
    else:
        first_sub = limited_offers[0]
        item = first_sub
        await display_limited_offers(event, item[0], is_status=True, status_type='active')



# Show all VIP subscriptions with Pagination
@bot.on(events.CallbackQuery(data='unactiveOffers'))
async def unactiveOffers(event):

    cursor.execute("SELECT * FROM limited_offer WHERE status = 'unactive'")
    limited_offers = cursor.fetchall()

    # Get the first subscription based on the id or show the first if none selected
    if len(limited_offers) == 0:
        await event.answer('لا توجد عروض لعرضها', alert=True)
    else:
        first_sub = limited_offers[0]
        item = first_sub
        await display_limited_offers(event, item[0], is_status=True, status_type='unactive')



# Function to display a specific VIP subscription
async def display_limited_offers(event, sub_id, is_status=False, status_type=''):

    await DeleteEvent(event)
    cursor = database.cursor()

    # Query to get the specific subscription by id
    if is_status == False:
        cursor.execute('SELECT * FROM limited_offer WHERE id = ?', (sub_id,))
        item = cursor.fetchone()
    else:
        cursor.execute('SELECT * FROM limited_offer WHERE id = ? AND status = ?', (sub_id, status_type,))
        item = cursor.fetchone()

    if item:
        if item[7] == 'active':
            status = 'نشيطة ✅'
        else:
            status = 'غير نشيطة ❌'
        
        target_date = datetime.strptime(str(item[6]), "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()

        # Calculate the time difference
        time_difference = target_date - current_time
        if time_difference.total_seconds() > 0:
            remaining_days = time_difference.days
            remaining_seconds = time_difference.seconds
            remaining_hours = remaining_seconds // 3600
            remaining_minutes = (remaining_seconds % 3600) // 60
            remains = f'{remaining_days} يوم, {remaining_hours} ساعة, {remaining_minutes} ثانية'
        else:
            remains = 'العرض انتهى'
            cursor.execute(f"UPDATE limited_offer SET status = 'unactive' WHERE id = {item[0]}")
            database.commit()

        if item[7] == 'unactive':
            remains = 'العرض انتهى'


        item_display = f'''🏷️ اسم العرض: {item[1]}
🔢 كود العرض: {item[2]}
💸 قيمة الخصم: {item[3]}%

⏳ المدة: {item[4]} يوم
📅 ينتهي بعد: {remains}

👥 عدد المستخدمين : {item[8]}
'''
        

        # Prepare the buttons for Next and Previous navigation
        buttons = [
            # [Button.inline('🛠 تعديل السعر', f'VipEditPrice_{item[0]}'), Button.inline('📅 تعديل الشهور', f'VipEditMonth_{item[0]}')]
        ]

        if item[7] == 'active':
            buttons.append([Button.inline('❌ انهاء العرض', f'StopOffer_{item[0]}')])
        else:
            buttons.append([Button.inline('❌ العرض منتهي', '')])

        nextback_buttons = []

        # Get Previous Item (if exists)
        if is_status == False:
            cursor.execute('SELECT id FROM limited_offer WHERE id < ? ORDER BY id DESC LIMIT 1', (item[0],))
            prev_item = cursor.fetchone()

            if prev_item:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevOffer_{prev_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevOffer_none'))

        else:
            cursor.execute('SELECT id FROM limited_offer WHERE status = ? AND id < ? ORDER BY id DESC LIMIT 1', (status_type, item[0]))
            prev_item = cursor.fetchone()

            if prev_item:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevOffer{status_type}_{prev_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('« السابق', data=f'prevOffer{status_type}_none'))

        # Get Next Item (if exists)
        if is_status == False:
            cursor.execute('SELECT id FROM limited_offer WHERE id > ? ORDER BY id ASC LIMIT 1', (item[0],))
            next_item = cursor.fetchone()

            if next_item:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextOffer_{next_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextOffer_none'))
        else:
            cursor.execute('SELECT id FROM limited_offer WHERE status = ? AND id > ? ORDER BY id ASC LIMIT 1', (status_type, item[0]))
            next_item = cursor.fetchone()

            if next_item:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextOffer{status_type}_{next_item[0]}'))
            else:
                nextback_buttons.append(Button.inline('التالي »', data=f'nextOffer{status_type}_none'))


        buttons.append(nextback_buttons)

        # Back to main menu button
        buttons.append([Button.inline('🔙 رجوع', data='back_to_offer')])

        # Send the current item with navigation buttons
        await event.respond(f"__📋 العرض\n\n{item_display}\n\n🔽 اختر ما تريد:__", buttons=buttons)
    else:
        await event.respond("العرض غير موجود")



# Stop Offer
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'StopOffer_')))
async def StopOffer(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        cursor.execute(f"UPDATE limited_offer SET status = 'unactive' WHERE id = {sub_id}")
        database.commit()
        await display_limited_offers(event, sub_id)
    except:await event.answer('لا يوجد هذا العرض', alert=True)



# Handle "Next" button press to show the next subscription
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextOffer_')))
async def next_item_offer(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id)
    except:await event.answer('لا مزيد من العروض', alert=True)



# Handle "Previous" button press to show the previous subscription
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevOffer_')))
async def prev_item_offer(event):

    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id)
    except:await event.answer('لا مزيد من العروض', alert=True)



@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextOfferactive_')))
async def next_item2_offer(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id, is_status=True, status_type='active')
    except Exception as e:
        await event.answer('لا مزيد من العروض', alert=True)


@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevOfferactive_')))
async def prev_item2_offer(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id, is_status=True, status_type='active')
    except Exception as e:
        await event.answer('لا مزيد من العروض', alert=True)



@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'nextOfferunactive_')))
async def next_item3_offer(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id, is_status=True, status_type='unactive')
    except Exception as e:
        await event.answer('لا مزيد من العروض', alert=True)


@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'prevOfferunactive_')))
async def prev_item3_offer(event):
    try:
        sub_id = int(event.data.decode().split('_')[1])
        await display_limited_offers(event, sub_id, is_status=True, status_type='unactive')
    except Exception as e:
        await event.answer('لا مزيد من العروض', alert=True)




# Add Limited Offer
@bot.on(events.CallbackQuery(data='add_limited_offer'))
async def add_limited_offer(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل اسم العرض:__')
            offer_name = (await conv.get_response()).message

            await conv.send_message('__أرسل كود العرض:__')
            offer_code = (await conv.get_response()).message

            await conv.send_message('__أرسل قيمة العرض:__')
            offer_reduce = (await conv.get_response()).message

            await conv.send_message('__أرسل مدة العرض بالأيام:__')
            offer_days = (await conv.get_response()).message

        if str(offer_days).isdigit():
            try:
                reduce = float(offer_reduce)
            except:
                await event.respond('__قيمة العرض يجب أن يكون رقما!__')
                return
            
            current_datetime = datetime.now()
            future_datetime = current_datetime + timedelta(days=int(offer_days))
            future_datetime = future_datetime.replace(microsecond=0)
            
            # ADD OFFER
            insert_query = """
                INSERT INTO limited_offer (
                    offer_name, offer_code, reduce, valid_days, created_at, end_at, status, usage_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            values = (
                offer_name,
                offer_code,
                reduce,
                int(offer_days),
                current_datetime.replace(microsecond=0),
                future_datetime,
                'active',
                0,
            )
            
            cursor.execute(insert_query, values)
            database.commit()

        else:
            await event.respond('__الأيام يجب أن يكون رقما!__')

    except:pass
    await discounts_show(event)





# BUY VIP
@bot.on(events.CallbackQuery(data='buy_vip'))
async def BuyVIP(event):
    
    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
            
    await DeleteEvent(event)

    user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
    user_data = cursor.fetchone()

    if user_data[7] == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return

    vip_subscription = cursor.execute("SELECT * FROM vip_subscription WHERE status = 'active'")
    vip_subscription  = cursor.fetchall()

    buttons = []

    for sub in vip_subscription:
        buttons.append([Button.inline(f'اشتراك مدفوع لـ {sub[2]} أشهر ({sub[1]}$)', f'PreCreateInvoice_{sub[2]}_{sub[1]}')])

    buttons.append([Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')])

    await event.respond(f'''__
✨ اشترك في العضوية المدفوعة للحصول على جميع مميزات البوت، مثل التحميل غير المحدود والمزيد!
__''', buttons=buttons)




# PRE-BUY VIP
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'PreCreateInvoice_')))
async def PreCreateInvoice(event):

    await DeleteEvent(event)
    months, price_in_dollar = str(event.data.decode()).replace('PreCreateInvoice_', '').split('_')

    user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {event.chat_id}")
    user_data = cursor.fetchone()

    buttons = [
        [Button.inline(f'🎁 استخدم خصم', f'Discount_{months}_{price_in_dollar}')],
        [Button.inline(f'💳 دفع بواسطة رصيدي', f'PayInstant_{months}_{price_in_dollar}')],
        [Button.inline(f'🧾 دفع بواسطة فاتورة', f'CreateInvoice_{months}_{price_in_dollar}')],
        [Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]
    ]

    gen_msg = await event.reply(f'''__
💳 اختر طريقة الدفع، يمكنك الدفع بواسطة رصيدك في البوت أو عن طريق فاتورة:  

💵 **رصيدك الحالي**: {user_data[1]}$  
💰 **سعر الاشتراك**: {price_in_dollar}$  
📆 **مدة الاشتراك بالشهر**: {months}
__''', buttons=buttons)



# DISCOUNT
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'Discount_')))
async def RedeemDiscount(event):

    await DeleteEvent(event)
    months, price_in_dollar = str(event.data.decode()).replace('Discount_', '').split('_')

    update_msg, coupon_used = '', False
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل كود الخصم:__')
            code = (await conv.get_response()).message

        offer_data = cursor.execute(f"SELECT * FROM limited_offer WHERE offer_code = '{code}'")
        offer_data = cursor.fetchone()

        if offer_data == None:
            update_msg = '‼ كود الخصم الذي أرسلته غير موجود!'
        else:
            if offer_data[7] == 'unactive':
                update_msg = '‼ كود الخصم الذي أرسلت لم يعد صالحا'
            else:
                target_date = datetime.strptime(str(offer_data[6]), "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()

                # Calculate the time difference
                time_difference = target_date - current_time
                if time_difference.total_seconds() > 0:
                    price_in_dollar = float(price_in_dollar) * (1 - float(offer_data[3]) / 100)
                    update_msg = f'✅ تم تطبيق الخصم بنجاح, الخصم {offer_data[3]}%'
                    coupon_used = True

                    cursor.execute(f"UPDATE limited_offer SET usage_count = {int(offer_data[8]) + 1} WHERE id = {offer_data[0]}")
                    database.commit()
                else:
                    update_msg = '‼ كود الخصم الذي أرسلت لم يعد صالحا'
                    cursor.execute(f"UPDATE limited_offer SET status = 'unactive' WHERE id = {offer_data[0]}")
                    database.commit()

    except Exception as error:pass

    user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {event.chat_id}")
    user_data = cursor.fetchone()

    buttons = []

    if coupon_used == False:
        buttons.append([Button.inline(f'🎁 استخدم خصم', f'Discount_{months}_{price_in_dollar}')])
    
    buttons.append([Button.inline(f'💳 دفع بواسطة رصيدي', f'PayInstant_{months}_{price_in_dollar}')])
    buttons.append([Button.inline(f'🧾 دفع بواسطة فاتورة', f'CreateInvoice_{months}_{price_in_dollar}')])
    buttons.append([Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')])


    gen_msg = await event.reply(f'''__
💳 اختر طريقة الدفع، يمكنك الدفع بواسطة رصيدك في البوت أو عن طريق فاتورة:  

💵 **رصيدك الحالي**: {user_data[1]}$  
💰 **سعر الاشتراك**: {price_in_dollar}$  
📆 **مدة الاشتراك بالشهر**: {months}

{update_msg}
__''', buttons=buttons)




@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'PayInstant_')))
async def CreateInvoice(event):

    await DeleteEvent(event)
    gen_msg = await event.reply('__جاري التحقق...__')

    months, price_in_dollar = str(event.data.decode()).replace('PayInstant_', '').split('_')

    user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {event.chat_id}")
    user_data = cursor.fetchone()

    user_balance = float(user_data[1])
    if user_balance >= float(price_in_dollar):
        # take user balance
        new_balance = user_balance - float(price_in_dollar)

        is_vip = user_data[2]
        if is_vip is None:
            new_vip_time = datetime.now() + timedelta(days=int(months) * 30)
        else:
            current_vip_time = datetime.strptime(str(is_vip), "%Y-%m-%d %H:%M:%S")
            new_vip_time = current_vip_time + timedelta(days=int(months) * 30)

        # Format the datetime back to string / # Update the database
        new_vip_time_str = new_vip_time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE bot_users SET is_vip = ?, balance = ? WHERE user_id = ?",
            (new_vip_time_str, new_balance, event.chat_id,)
        )
        database.commit()

        notice_user = await event.reply(
            message=f'''__
🎉 شكرًا لك على دفعتك!

لقد تم دفع فاتورتك بنجاح، تم ترقية حسابك. نقدر سرعة استجابتك!
__''', buttons=[[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]])
        
        # Add To History
        user_id = event.chat_id
        invoice_id = 'تم الدفع بواسطة رصيد البوت'
        invoice_link = 'تم الدفع بواسطة رصيد البوت'
        paid_subscription_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subscription_ends = new_vip_time_str
        subscription_months = months
        subscription_price = price_in_dollar

        insert_query = """
            INSERT INTO subscription_history (
                user_id,
                invoice_id,
                invoice_link,
                paid_subscription_at,
                subscription_ends,
                subscription_months,
                subscription_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_query, (user_id, invoice_id, invoice_link, paid_subscription_at, subscription_ends, subscription_months, subscription_price))
        database.commit()

        
        try:
            notice_admin = await bot.send_message(
                entity=OWNER_ID,
                message=f'''__
تم دفع الفاتورة بنجاح ✅

👤 **ايدي المستخدم**: {event.chat_id}  
💳 **رقم الفاتورة**: تم الدفع بواسطة رصيد البوت  

📅 **العضوية بالشهر**: {months}  
💵 **السعر**: {price_in_dollar}$  
__''')
        except:pass


    else:
        await event.respond('__رصيدك غير كافي, يرجى الدفع بواسطة فاتورة__', 
            buttons=[[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]])

    await DeleteEvent(gen_msg)

    

@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'CreateInvoice_')))
async def CreateInvoice(event):

    await DeleteEvent(event)
    gen_msg = await event.reply('__جاري توليد فاتورتك. الرجاء الانتظار قليلاً...__')

    months, price_in_dollar = str(event.data.decode()).replace('CreateInvoice_', '').split('_')
    amount_inSAR = float(price_in_dollar) * 3.76 # FROM USD TO SAR

    invoice = await create_invoice_myfatoorah(amount_inSAR, event.chat_id)
    await event.reply(f'''__
✅ فاتورتك جاهزة!

رقم الفاتورة: {invoice[0]}
رابط الفاتورة: [اضغط لدفع فاتورتك]({invoice[1]})

عند إكمال دفع ( ${price_in_dollar} ), سيتم ترقية عضوية حسابك فورًا. يرجى الدفع خلال ساعة، شكرًا لك!
__''', buttons=[
            [Button.url('دفع فاتورتي', invoice[1])],
            [Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]])
    

    await DeleteEvent(gen_msg)
    try:
        notice_admin = await bot.send_message(
            entity=OWNER_ID,
            message=f'''__
مستخدم أنشأ فاتورة 🧾

👤 **ايدي المستخدم**: {event.chat_id}  
💳 **رقم الفاتورة**: {invoice[0]}  
🔗 **رابط الدفع**: {invoice[1]}

📅 **العضوية بالشهر**: {months}  
💵 **السعر**: ${price_in_dollar}  
__''')
    except Exception as error:pass

    counter = 0
    while True:
        check_paid = await check_invoice_status_myfatoorah(invoice[0])
        if check_paid[0] == False:
            await asyncio.sleep(120)
            counter += 120
        else:
            user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {event.chat_id}")
            user_data = cursor.fetchone()
            is_vip = user_data[2]
            if is_vip is None:
                new_vip_time = datetime.now() + timedelta(days=int(months) * 30)
            else:
                current_vip_time = datetime.strptime(str(is_vip), "%Y-%m-%d %H:%M:%S")
                new_vip_time = current_vip_time + timedelta(days=int(months) * 30)

            # Format the datetime back to string / # Update the database
            new_vip_time_str = new_vip_time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE bot_users SET is_vip = ? WHERE user_id = ?",
                (new_vip_time_str, event.chat_id,)
            )
            database.commit()

            notice_user = await event.reply(
                message=f'''__
🎉 شكرًا لك على دفعتك!

لقد تم دفع فاتورتك بنجاح، تم ترقية حسابك. نقدر سرعة استجابتك!
__''', buttons=[[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]])
            

            # Add To History
            user_id = event.chat_id
            invoice_id = invoice[0]
            invoice_link = invoice[1]
            paid_subscription_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subscription_ends = new_vip_time_str
            subscription_months = months
            subscription_price = price_in_dollar

            insert_query = """
                INSERT INTO subscription_history (
                    user_id,
                    invoice_id,
                    invoice_link,
                    paid_subscription_at,
                    subscription_ends,
                    subscription_months,
                    subscription_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(insert_query, (user_id, invoice_id, invoice_link, paid_subscription_at, subscription_ends, subscription_months, subscription_price))
            database.commit()

            
            try:
                notice_admin = await bot.send_message(
                    entity=OWNER_ID,
                    message=f'''__
تم دفع الفاتورة بنجاح ✅

👤 **ايدي المستخدم**: {event.chat_id}  
💳 **رقم الفاتورة**: {invoice[0]}

📅 **العضوية بالشهر**: {months}  
💵 **السعر**: {price_in_dollar}$  

__''')
            except:pass

            break
        
        if counter >= 3600:
            await event.reply(f'''__
⏰ مرت ساعة واحدة دون الدفع.

إذا كنت لا تزال ترغب في الاشتراك, يرجى إنشاء فاتورة جديدة لمتابعة معاملتك.
__''', buttons=[[Button.inline('🔙 رجوع للقائمة الرئيسية', 'back_to_menu')]])
            break



# Daily limits show
@bot.on(events.CallbackQuery(data='daily_limits_show')) 
async def DAILY_LIMITS_SHOW(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()
    await DeleteEvent(event)
    buttons = [
        [Button.inline('تعديل عدد عمليات التحميل اليومية', 'edit_DailyLimit')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    search_limit, result_limit = bot_settings_data[1], bot_settings_data[2]
    await event.respond(f'''__
🔧✨ **قم بتخصيص إعدادات التحميل في البوت بكل سهولة!**  
(للمستخدمين بدون اشتراك)

🔍 **عمليات التحميل اليومية**: {search_limit}
__''', buttons=buttons)



# Edit DailyLimit
@bot.on(events.CallbackQuery(data='edit_DailyLimit'))
async def edit_DailyLimit(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل العدد الأقصى المسموح به:__')
            new_limit = (await conv.get_response()).message

        if str(new_limit).isdigit():
            cursor.execute(f"UPDATE bot_settings SET download_limit = {new_limit} WHERE setting_id = 1")
            database.commit()
        else:
            await event.respond('__العدد يجب أن يكون رقما!__')

    except:pass
    await DAILY_LIMITS_SHOW(event)



# AD BUTTON
@bot.on(events.CallbackQuery(data='ad_buttons')) 
async def AD_Button(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    ad_buttons_data = cursor.execute('SELECT * FROM ad_buttons')
    ad_buttons_data = cursor.fetchall()
    await DeleteEvent(event)
    buttons = [
        [Button.inline('➕ اضافة زر', 'add_button'), Button.inline('➖ حذف زر', 'delete_button')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    await event.respond(f'''__
✨ يمكنك اضافة أو حذف أزرار القنوات و المجموعات من هنا بكل سهولة!

عدد أزرار القنوات/المجموعات : {len(ad_buttons_data)}
__''', buttons=buttons)
    


# Add Buttons
@bot.on(events.CallbackQuery(data='add_button'))
async def AddButton(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل اسم الزر ( اسم الذي سيظهر على الزر  ):__')
            button_text = (await conv.get_response()).message

            await conv.send_message('__أرسل الرابط الذي تريد وضعه في الزر:__')
            button_link = (await conv.get_response()).message

        if str(button_link).startswith('https://'):
            cursor.execute(f"SELECT * FROM ad_buttons WHERE link = '{button_link}'")
            item_exists = cursor.fetchone()

            # Add the item if it doesn't exist
            if not item_exists:
                cursor.execute("INSERT INTO ad_buttons (title, link) VALUES (?, ?)", (button_text, button_link))
                database.commit()

        else:
            await event.reply('__رابط الزر يجب أن يبدأ بـ https://__')

    except:pass
    await AD_Button(event)



# Delete  Buttons
@bot.on(events.CallbackQuery(data='delete_button'))
async def DeleteButton(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    ad_buttons_data = cursor.execute('SELECT * FROM ad_buttons')
    ad_buttons_data = cursor.fetchall()
    
    buttons = []
    for item in ad_buttons_data:
        buttons.append([Button.inline(f'❌ {item[1]}', f'deleteButtonAD_{item[0]}')])

    buttons.append([Button.inline('🔙 رجوع', 'back_to_adminpanel')])
    await event.respond('__اضغط على زر القناة أو الجروب لحذف ذالك الزر:__', buttons=buttons)



# Delete Button AD
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'deleteButtonAD_')))
async def DeleteButton_AD(event):
    
    # await DeleteEvent(event)
    id = int(str(event.data.decode()).replace('deleteButtonAD_', '').strip())
    ad_buttons_data = cursor.execute(f'SELECT * FROM ad_buttons WHERE id = {id}')
    ad_buttons_data = cursor.fetchone()

    if ad_buttons_data != None:
        cursor.execute(f'DELETE FROM ad_buttons WHERE id = {id}')
        database.commit()
    
    await DeleteButton(event)



# BROADCAST
@bot.on(events.CallbackQuery(data='broadcast')) 
async def BroadCast(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    if event.chat_id == OWNER_ID or event.chat_id == 978571497 or event.chat_id in admins_list:
        await event.answer('🥽 جاري تجهيز الاذاعة')

        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message('__أرسل الرسالة :__')
            the_message = await conv.get_response()
            
        notice_admin = await event.reply(f"__جاري الارسال...__")
        users = cursor.execute(f"SELECT * FROM bot_users")
        users = cursor.fetchall()
        success, fails = 0, 0
        for user in users:
            try:
                if int(user[0]) != OWNER_ID:
                    send_to__user = await bot.send_message(entity=int(user[0]), message=the_message)
                    success += 1
                else:
                    success += 1
            except:
                cursor.execute(f"UPDATE bot_users SET banned = 'YES' WHERE user_id = {int(user[0])}")
                fails += 1
        
        bot_users = cursor.execute("SELECT * FROM bot_users WHERE banned = 'YES'")
        bot_users = cursor.fetchall()

        notice_admin = await event.reply(f"""__
📊 تمت الإذاعة بنجاح تام 

👥 المستخدمون المستهدفون الذين شاهدوا الرساله: غير معروف
✅ تم الإرسال إلى: {success}
🚫 الاعضاء المحظورين: {len(bot_users)}
❌ فشل في الإرسال لهم بسبب الحظر : {fails}
📈 نسبة نجاح الاذاعة : {round((success / len(users)) * 100, 2)}%
__""")
	


# Edit User Price
@bot.on(events.CallbackQuery(data='editUser_price')) 
async def EditUserPrice(event, USER_ID=None):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    if event.chat_id == OWNER_ID or event.chat_id == 978571497:
        try:
            async with bot.conversation(event.chat_id, timeout=120) as conv:
                if USER_ID == None:
                    await conv.send_message('__أرسل ايدي الشخص الذي تريد اضافة/حذف الرصيد له:__')
                    user_id = (await conv.get_response()).message
                else:
                    user_id = int(USER_ID)
                
                await conv.send_message('__أرسل الرصيد بالدولار ( لحذف رصيد أرسل الرقم بالسالب ):__')
                price_in_dollar = (await conv.get_response()).message
                
            try:
                user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {user_id}")
                user_data = cursor.fetchone()
                if user_data != None:
                    new_balance = round((float(user_data[1]) + float(price_in_dollar)), 2)
                    cursor.execute(f"UPDATE bot_users SET balance = {new_balance} WHERE user_id = {user_id}")

                    try:
                        notice_user = await bot.send_message(entity=int(user_id), message=f'__تم ارسال لك رصيد من مشرف البوت : **{price_in_dollar}$**__')
                    except:pass

                    buttons = [[Button.inline('🔙 رجوع', 'back_to_adminpanel')]]
                    notice_admin = await event.reply("__تم التنفيذ بنجاح__", buttons=buttons)
                    database.commit()

            except Exception as error:
                notice_user = await event.reply(str(error))

        except:pass



# Edit Link Price
@bot.on(events.CallbackQuery(data='editLink_price')) 
async def EditLinkPrice(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()
    if event.chat_id == OWNER_ID or event.chat_id == 978571497 or event.chat_id in admins_list:
        await event.respond(f'''__
🎁 الجائزة الحالية:

سيحصل صاحب رابط الدعوة على **{bot_settings_data[2]}$** عند انضمام أي شخص عبر الرابط! 🌟
__''')
        
        try:
            buttons = [[Button.text('الغاء و الرجوع', resize=True)]]
            async with bot.conversation(event.chat_id, timeout=120) as conv:
                await conv.send_message('__أرسل الرصيد الذي تريد صاحب رابط الدعوة الحصول عليه بالدولار:__', buttons=buttons)
                price_in_dollar = (await conv.get_response()).message
                
            if price_in_dollar == 'الغاء و الرجوع':
                await hide_keyboard(event)
                await BotAdminPanel(event)
            else:
                try:
                    price_in_dollar = float(price_in_dollar)
                    cursor.execute(f"UPDATE bot_settings SET link_reward = '{price_in_dollar}' WHERE setting_id = 1")
                    database.commit()

                    await EditLinkPrice(event)
                except:
                    back_buttons= [[Button.inline('🔙 رجوع', 'back_to_menu')]]
                    await event.reply('__الجائزة يجب أن تكون رقما!__', buttons=back_buttons)

        except:pass



# Last Search
@bot.on(events.CallbackQuery(data='last_download')) 
async def last_downloaded(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    cursor.execute("""
        SELECT * 
        FROM download_history
        ORDER BY download_date DESC
        LIMIT 10;
    """)
    results = cursor.fetchall()

    message = f'**اخر عمليات التحميل:**\n\n'
    # Process the results
    for row in results:
        user_id = row[1]

        try:
            user_data = await bot.get_entity(int(user_id))

            if user_data.username:
                user_text = f"👤 زيارة المستخدم: @{user_data.username}"
            else:
                user_text = f"👤 زيارة المستخدم: {user_id}"
                # user_text = f"👤 زيارة المستخدم: [{user_id}](tg://user?id={user_id})\n"
            
        except:
            user_text = f"👤 زيارة المستخدم: {user_id}"
            
        message += f'''__
✨ الايدي: {row[1]}  
🔎 رابط التحميل: {row[3]}  
🕒 تاريخ البحث: {row[4]}  
{user_text}
__'''


    buttons = [[Button.inline('🔙 رجوع', 'back_to_adminpanel')]]
    await event.respond(message, buttons=buttons)



# Most Search
@bot.on(events.CallbackQuery(data='most_download')) 
async def most_download(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    cursor.execute("""
        SELECT download_by, COUNT(*) AS download_count
        FROM download_history
        GROUP BY download_by
        ORDER BY download_count DESC
        LIMIT 10;
    """)
    results = cursor.fetchall()

    message = f'**أكثر الأشخاص قاموا بالتحميل:**\n\n'
    for row in results:
        user_id, search_count = row
        message += f'''__
✨ الايدي: {user_id}  
🔍 عدد عمليات التحميل: {search_count}
👤 زيارة المستخدم: [{user_id}](tg://user?id={user_id})  
__'''


    buttons = [[Button.inline('🔙 رجوع', 'back_to_adminpanel')]]
    await event.respond(message, buttons=buttons)



# GET USRES BY OFFSET
def get_users(offset, limit):
    cursor.execute("SELECT * FROM bot_users LIMIT ? OFFSET ?", (limit, offset))
    return cursor.fetchall()



# Previous Users
@bot.on(events.CallbackQuery(data='previous_users')) 
async def PreviousUsers(event):
    user_id = event.chat_id

    # Initialize user's page if not set
    if user_id not in page_data:
        page_data[user_id] = 0

    # Adjust offset based on button
    if page_data[user_id] > 0:
        page_data[user_id] -= PAGE_SIZE

    await AllStatistics(event)



# Next Users
@bot.on(events.CallbackQuery(data='next_users')) 
async def NextUsers(event):
    user_id = event.chat_id

    # Initialize user's page if not set
    if user_id not in page_data:
        page_data[user_id] = 0

    # Adjust offset based on button
    page_data[user_id] += PAGE_SIZE

    # Fetch the users
    offset = page_data[user_id]
    users = get_users(offset, PAGE_SIZE)

    if not users:
        # If no more users, reset the page
        page_data[user_id] -= PAGE_SIZE
        await event.answer("لا يوجد المزيد")
        return
    
    await AllStatistics(event)



# STATISTICS
@bot.on(events.CallbackQuery(data='all_statistics')) 
async def AllStatistics(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)

    user_data = cursor.execute(f"SELECT * FROM bot_users")
    user_data = cursor.fetchall()

    user_data_banned = cursor.execute(f"SELECT * FROM bot_users WHERE banned = 'YES'")
    user_data_banned = cursor.fetchall()

    user_data_not_banned = cursor.execute(f"SELECT * FROM bot_users WHERE banned IS NULL")
    user_data_not_banned = cursor.fetchall()


    today = datetime.now()
    today_formatted = today.strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM bot_users WHERE DATE(added_date) = ?", (today_formatted,))
    date_users_today = cursor.fetchall()

    cursor.execute("SELECT * FROM bot_users WHERE DATE(last_download_date) = ?", (today_formatted,))
    date_users_today_search_today = cursor.fetchall()

    cursor.execute("SELECT * FROM subscription_history WHERE DATE(paid_subscription_at) = ?", (today_formatted,))
    paid_subscription_today = cursor.fetchall()


    today_users_subscription = 0
    for sub in paid_subscription_today:
        today_users_subscription += float(sub[7])

    today_msg = len(date_users_today_search_today)
    for msg in date_users_today_search_today:
        today_msg += int(msg[5])


    yesterday = today - timedelta(days=1)
    yesterday_formatted = yesterday.strftime("%Y-%m-%d")
    
    cursor.execute("SELECT * FROM bot_users WHERE DATE(added_date) = ?", (yesterday_formatted,))
    date_users_yesterday = cursor.fetchall()

    cursor.execute("SELECT * FROM bot_users WHERE DATE(last_download_date) = ?", (yesterday_formatted,))
    date_users_today_search_yesterday = cursor.fetchall()

    cursor.execute("SELECT * FROM subscription_history WHERE DATE(paid_subscription_at) = ?", (yesterday_formatted,))
    paid_subscription_yesterday = cursor.fetchall()

    yesterday_users_subscription = 0
    for sub in paid_subscription_yesterday:
        yesterday_users_subscription += float(sub[7])

    yesterday_msg = len(date_users_today_search_yesterday)
    for msg in date_users_today_search_yesterday:
        yesterday_msg += int(msg[5])


    # Get current month
    current_month = today.strftime("%Y-%m")

    # Get users who joined in the current month
    # cursor.execute("SELECT * FROM bot_users WHERE DATE_FORMAT(added_date, '%Y-%m') = ?", (current_month,))
    cursor.execute("SELECT * FROM bot_users WHERE strftime('%Y-%m', added_date) = ?", (current_month,))
    date_users_current_month = cursor.fetchall()

    # Get previous month
    previous_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    # Get users who joined in the previous month
    # cursor.execute("SELECT * FROM bot_users WHERE DATE_FORMAT(added_date, '%Y-%m') = ?", (previous_month,))
    cursor.execute("SELECT * FROM bot_users WHERE strftime('%Y-%m', added_date) = ?", (previous_month,))
    date_users_previous_month = cursor.fetchall()
 

    if event.chat_id not in page_data:
        page_data[event.chat_id] = 0

    users = get_users(page_data[event.chat_id], PAGE_SIZE)

    cursor.execute("SELECT COUNT(*) FROM bot_users")
    total_users = cursor.fetchone()[0]
    total_pages = math.ceil(total_users / PAGE_SIZE)
    current_page = (page_data[event.chat_id] // PAGE_SIZE) + 1


    buttons = [[Button.inline('🔎 بحث عن مستخدم', 'getUser_byID')]]

    for user in users:
        try:
            get_user_data = await bot.get_entity(int(user[0]))
            if get_user_data.username == None:
                username = ''
            else:
                username = f'( @{get_user_data.username} )'

            if user[8] == None:
                first_name = get_user_data.first_name
                last_name = get_user_data.last_name

                cursor.execute(
                    "UPDATE bot_users SET firstname = ?, lastname = ? WHERE user_id = ?",
                    (first_name, last_name, int(user[0]))
                )
                database.commit()

                if last_name == None:
                    firstlast_name = f'{first_name}'
                else:
                    firstlast_name = f'{first_name} {last_name}'

            else:
                if user[9] == None:
                    firstlast_name = f'{user[8]}'
                else:
                    firstlast_name = f'{user[8]} {user[9]}'

            buttons.append([Button.inline(f'{firstlast_name} {username}', f'getUserInfoID_{user[0]}')])
        except Exception as error:print (error)

    buttons.append([Button.inline("« الصفحة السابقة", data='previous_users'), Button.inline("الصفحة التالية »", data='next_users')])

    buttons.append([Button.inline('🔙 رجوع', 'back_to_adminpanel')])

    channels_list = cursor.execute('SELECT * FROM join_channels')
    channels_list = cursor.fetchall()

    await event.respond(f'''
📊 مرحبًا بك في قسم الإحصائيات 📊

المستخدمون:
- 👥 العدد الإجمالي للمستخدمين: {len(user_data)}
- 👤 عدد المستخدمين في الخاص: {len(user_data_not_banned)}
- 👥 عدد القنوات والمجموعات: {len(channels_list)}
- 🚫 عدد المحظورين: {len(user_data_banned)}

📅 الفعّالين:
اليوم ({today_formatted}):
- 👥 المستخدمون الجدد: {len(date_users_today)}
- 👥 المستخدمون الفعّالين: {len(date_users_today_search_today)}
- 💰 ربحية الاشتراكات: {today_users_subscription}$
- ✉️ الرسائل: {today_msg}

الأمس ({yesterday_formatted}):
- 👥 المستخدمون الجدد: {len(date_users_yesterday)}
- 👥 المستخدمون الفعّالين: {len(date_users_today_search_yesterday)}
- 💰 ربحية الاشتراكات: {yesterday_users_subscription}$
- ✉️ الرسائل: {yesterday_msg}

📅 المستخدمون الجدد:
- عدد المستخدمين الجدد خلال الشهر الحالي: {len(date_users_current_month)}
- عدد المستخدمين الجدد خلال الشهر الماضي: {len(date_users_previous_month)}

الصفحة: {current_page}/{total_pages}
''', buttons=buttons)




# Get User by ID
@bot.on(events.CallbackQuery(data='getUser_byID')) 
async def GetUserbyID(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    if event.chat_id == OWNER_ID or event.chat_id == 978571497 or event.chat_id in admins_list:
        try:
            async with bot.conversation(event.chat_id, timeout=120) as conv:
                await conv.send_message('__أرسل ايدي الشخص لعرض معلوماته:__')
                user_id = (await conv.get_response()).message
            
            if str(user_id).isdigit():
                await GetUserByID_(event, passed_user_id=user_id)
            else:
                await event.reply('__ايدي يجب أن يكون رقما!__')

        except:pass



# GET USER BY ID
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'getUserInfoID_')))
async def GetUserByID_(event, passed_user_id=None):

    await DeleteEvent(event)
    if passed_user_id == None:
        user_id = int(str(event.data.decode()).split('_')[1])
    else:
        user_id = passed_user_id

    try:
        bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
        bot_settings_data = cursor.fetchone()

        user_data = cursor.execute(f"SELECT * FROM bot_users WHERE user_id = {int(user_id)}")
        user_data = cursor.fetchone()

        search_history_data = cursor.execute(f"SELECT * FROM download_history WHERE download_by = {int(user_id)}")
        search_history_data = cursor.fetchall()
        
        balance, added_date = user_data[1], user_data[4]
        last_search_date, banned = user_data[6], user_data[7]

        if user_data[9] == None:
            firstlast_name = f'{user_data[8]}'
        else:
            firstlast_name = f'{user_data[8]} {user_data[9]}'

        if user_data[3] == None:
            refferal_from = 'لا أحد'
        else:
            refferal_from = f'[اضغط لزيارة المستخدم](tg://user?id={user_data[3]})'
        
        if not user_data[2]:
            limit = f'{user_data[5]}/{bot_settings_data[1]}'
            subscription_active = 'مجانية'
            subscription_date = 'غير مشترك'
            subscription_expires = 'غير مشترك'
        else:
            limit = f'غير محدود'
            subscription_active = 'مدفوعة'
            subscription_date = user_data[2]

            expire_time = datetime.strptime(str(user_data[2]), "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()

            time_remaining = expire_time - current_time
            days = time_remaining.days

            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            subscription_expires = f'{days} يوم، {hours} ساعة، {minutes} دقيقة'

        if banned == None:
            banned_text = '🚫 حظر'
        else:
            banned_text = '🔓 فك حظر'
        
        try:
            get_user_data = await bot.get_entity(int(user_id))
            if get_user_data.username == None:
                url = f'tg://user?id={get_user_data.id}'
            else:
                url = f'https://t.me/{get_user_data.username}'
        except:url = f'tg://user?id={int(user_id)}'

        buttons = [
            [Button.url('💬 فتح محادثة', url), Button.inline('✏️ تعديل', f'OwnerEdit_{user_id}')],
            [
                Button.inline('🔎 سجل التحميل', f'getSearchHistory_{user_id}'),
                Button.inline('💳 سجل اشتراكات', f'getSubscription_{user_id}')
            ],
            [Button.inline(banned_text, f'CheckBan_{user_id}'), Button.inline('🗑️ حذف', f'DeleteUser_{user_id}')],
            [Button.inline('💰 اضافة/حذف رصيد', f'editPrice_{user_id}')],
            [Button.inline('♻ تصفير العداد', f'resetDownloads_{user_id}')],
            [Button.inline('🔄 تحديث', f'reffresh_{user_id}')],
            [Button.inline('🔙 رجوع', 'back_to_statistics')]
        ]

        notice_user = await event.reply(f'''__
✨ **تفاصيل العميل**

🆔 رقم المستخدم: {user_id}
👨🏻‍💻 اسم الكامل : {firstlast_name}
💰 الرصيد: {balance}$

📅 تاريخ الانضمام: {added_date}
🔗 الإحالة من: {refferal_from}

🏷️ نوع العضوية: {subscription_active}
📆 تاريخ انتهاء العضوية: {subscription_date}
⏳ المدة المتبقية لانتهاء العضوية: {subscription_expires}

🔍 محاولات التحميل اليومية المتبقية: {limit}
⏱️ تاريخ آخر تحميل: {last_search_date}

🔍 اجمالي عدد عمليات التحميل: {len(search_history_data)}
__''', buttons=buttons)

    except Exception as error:
        notice_user = await event.reply(str(error))



# Edit Price
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'editPrice_')))
async def GetUserByID_EditPrice(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])

    await EditUserPrice(event, user_id)



# Reset Downloads
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'resetDownloads_')))
async def GetUserByID_ResetDownloads(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])

    cursor.execute(f"UPDATE bot_users SET today_downloads = 0 WHERE user_id = {user_id}")
    database.commit()

    buttons = [
        [Button.inline('🔙 رجوع', f'getUserInfoID_{user_id}')]
    ]

    await event.respond('__تم تصفير العداد للمستخدم__', buttons=buttons)



# Delete User
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'DeleteUser_')))
async def GetUserByID_DeleteUser(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])
    buttons = [
        [Button.inline('🗑️ تأكيد و حذف المستخدم', f'ConfirmDeleteUser_{user_id}')],
        [Button.inline('🔙 رجوع', f'getUserInfoID_{user_id}')]
    ]

    await event.respond(f'''__
هل أنت متأكد من حذف هذا المستخدم, سيتم حذف جميع معلوماته بالكامل
__''', buttons=buttons)



# Confirm Delete User
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'ConfirmDeleteUser_')))
async def GetUserByID_ConfirmDeleteUser(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])

    cursor.execute(f'DELETE FROM bot_users WHERE user_id = {int(user_id)}')
    database.commit()

    buttons = [
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    await event.respond('__تم حذف المستخدم و كامل معلوماته في البوت__', buttons=buttons)


# Reffresh
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'reffresh_')))
async def GetUserByID_reffresh(event):

    user_id = int(str(event.data.decode()).split('_')[1])
    await GetUserByID_(event, passed_user_id=user_id)



# Check Ban/Unban
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'CheckBan_')))
async def GetUserByID_CheckBan(event):

    user_id = int(str(event.data.decode()).split('_')[1])
    cursor.execute("SELECT banned FROM bot_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        await event.answer('المستخدم غير موجود')
        return

    current_status = result[0]
    if current_status is not None:
        cursor.execute("UPDATE bot_users SET banned = NULL WHERE user_id = ?", (user_id,))
        await event.answer('تم فك حظر المستخدم')
    else:
        cursor.execute("UPDATE bot_users SET banned = 'YES' WHERE user_id = ?", (user_id,))
        await event.answer('تم حظر المستخدم')
    
    database.commit()
    await GetUserByID_(event, passed_user_id=user_id)




# Get Subscription
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'getSubscription_')))
async def GetSubscription(event):
    
    user_id = int(str(event.data.decode()).replace('getSubscription_', '').strip())
    subscription_history = cursor.execute(f'SELECT * FROM subscription_history WHERE user_id = {user_id}')
    subscription_history = cursor.fetchall()

    if len(subscription_history) == 0:
        header_info = f'''# تقرير شامل على اشتراكات العميل

ايدي العميل : {user_id}
اجمالي عدد الاشتراكات : {len(subscription_history)}

--------------------------------------------
لا يوجد اشتراكات
--------------------------------------------
'''
    else:
        header_info = f'''# تقرير شامل على اشتراكات العميل

ايدي العميل : {user_id}
اجمالي عدد الاشتراكات : {len(subscription_history)}


--------------------------------------------
'''
        
        for item in subscription_history:
            header_info += f'''رقم الفاتورة : {item[2]}
رابط الفاتورة : {item[3]}

تم دفع الفاتورة بتاريخ : {item[4]}
تاريخ انتهاء الاشتراك : {item[5]}

عدد أشهر الاشتراك : {item[6]}
سعر الاشتراك : {item[7]}$
--------------------------------------------'''


    filepath = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.txt'
    with open(filepath, "w", encoding='utf-8 ') as file:
        file.write(header_info)

    last_3 = '**💳📜 سجل الاشتراكات (📥 حمل الملف لتصفح السجل بالكامل) 📄**\n\n'
    for idx, item in enumerate(subscription_history):
        if idx == 3:
            break

        last_3 += f'''__🧾 **رقم الفاتورة**: {item[2]}
🔗 **رابط الفاتورة**: {item[3]}
📅 **تم دفع الفاتورة بتاريخ**: {item[4]}
⏳ **تاريخ انتهاء الاشتراك**: {item[5]}
📆 **عدد أشهر الاشتراك**: {item[6]}
💰 **سعر الاشتراك**: {item[7]}$__

'''

    await bot.send_message(event.chat_id, file=filepath, message=last_3)

    try:
        os.remove(filepath)
    except:pass



# Get Search History
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'getSearchHistory_')))
async def GetSearchHistory(event):
    
    # await DeleteEvent(event)
    user_id = int(str(event.data.decode()).replace('getSearchHistory_', '').strip())
    search_history = cursor.execute(f'SELECT * FROM download_history WHERE download_by = {user_id}')
    search_history = cursor.fetchall()

    if len(search_history) == 0:
        header_info = f'''# تقرير شامل على عمليات التحميل

ايدي العميل : {user_id}
اجمالي عمليات التحميل : {len(search_history)}

--------------------------------------------
لا يوجد عمليات تحميل
--------------------------------------------
'''
    else:
        header_info = f'''# تقرير شامل على عمليات التحميل

ايدي العميل : {user_id}
اجمالي عمليات التحميل : {len(search_history)}

--------------------------------------------
'''
        
        for item in search_history:
            header_info += f'''
رابط التحميل : {item[3]}
نوع التحميل : {item[2]}
تاريخ التحميل : {item[4]}
--------------------------------------------'''


    filepath = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.txt'
    with open(filepath, "w", encoding='utf-8 ') as file:
        file.write(header_info)

    last_3 = '**🔍📜 سجل التحميل (📥 حمل الملف لتصفح السجل بالكامل) 📄**\n\n'
    for idx, item in enumerate(search_history):
        if idx == 3:
            break

        last_3 += f'''__🔎 **رابط التحميل**: {item[3]}
📂 **نوع التحميل**: {item[2]}
📅 **تاريخ التحميل**: {item[4]}__

'''

    await bot.send_message(event.chat_id, file=filepath, message=last_3)

    try:
        os.remove(filepath)
    except:pass



# Owner Edit User
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'OwnerEdit_')))
async def GetUserByID_OwnerEdit(event, passed_user_id=None, extra_msg=''):

    await DeleteEvent(event)
    if passed_user_id == None:
        user_id = int(str(event.data.decode()).split('_')[1])
    else:
        user_id = passed_user_id

    buttons = [
        [Button.inline('✏️ الاسم الأول', f'OwnerEditName1_{user_id}'), Button.inline('✏️ الاسم الأخير', f'OwnerEditName2_{user_id}')],
        [Button.inline('🔙 رجوع', f'getUserInfoID_{user_id}')]
    ]

    await event.respond(f'''__
يمكنك تعديل اسم الأول و الأخير للمستخدم:

{extra_msg}
__''', buttons=buttons)



# EDIT NAME 1
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'OwnerEditName1_')))
async def GetUserByID_OwnerEditName1(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل الاسم الأول لتحديثه:__')
            first_name = (await conv.get_response()).message

        cursor.execute("UPDATE bot_users SET firstname = ? WHERE user_id = ?", (first_name, user_id,))
        database.commit()

        await GetUserByID_OwnerEdit(event, passed_user_id=user_id, extra_msg='__✅ تم تعديل الاسم الأول للمستخدم بنجاح__')
    
    except:await GetUserByID_(event, passed_user_id=user_id)


# EDIT NAME 2
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'OwnerEditName2_')))
async def GetUserByID_OwnerEditName2(event):

    await DeleteEvent(event)
    user_id = int(str(event.data.decode()).split('_')[1])

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل الاسم الأخير لتحديثه:__')
            first_name = (await conv.get_response()).message

        cursor.execute("UPDATE bot_users SET lastname = ? WHERE user_id = ?", (first_name, user_id,))
        database.commit()

        await GetUserByID_OwnerEdit(event, passed_user_id=user_id, extra_msg='__✅ تم تعديل الاسم الأخير للمستخدم بنجاح__')
    
    except:await GetUserByID_(event, passed_user_id=user_id)



# Most Services Needed
@bot.on(events.CallbackQuery(data='most_services_needed')) 
async def MostServicesNeeded(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)

    cursor.execute("""
        SELECT download_type, COUNT(download_type) AS download_count
        FROM download_history
        GROUP BY download_type
        ORDER BY download_count DESC
        LIMIT 10;"""
    )
    top_10 = cursor.fetchall()

    message = f'**أكثر 10 خدمات طلبا للتحميل:**\n\n'
    for row in top_10:
        message += f'''__
🛒 الخدمة: {row[0]}
✨ الطلبات: {row[1]}
__'''
    

    buttons = []
    buttons.append([Button.inline('🔙 رجوع', 'back_to_adminpanel')])
    await event.respond(message, buttons=buttons)



# FIRST JOIN
@bot.on(events.CallbackQuery(data='first_join')) 
async def FirstJoin(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    join_channels_data = cursor.execute('SELECT * FROM join_channels')
    join_channels_data = cursor.fetchall()

    await DeleteEvent(event)
    buttons = [
        [Button.inline('➕ اضافة', 'add_channel'), Button.inline('➖ حذف', 'delete_channel')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    await event.respond(f'''__
✨ يمكنك اضافة أو حذف القنوات و المجموعات من الاشتراك الاجباري للبوت من هنا بكل سهولة!

عدد القنوات/المجموعات المضافة : {len(join_channels_data)}
__''', buttons=buttons)



# Add Channel
@bot.on(events.CallbackQuery(data='add_channel'))
async def AddChannel(event):

    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل رابط أو ايدي القناة/جروب:__')
            channel_url = (await conv.get_response()).message

        try:
            if str(channel_url).isdigit():
                channel_entity = await bot.get_entity(int(channel_url))
            else:
                channel_entity = await bot.get_entity(str(channel_url))
        except:channel_entity = None

        if channel_entity == None:
            await event.respond(f'''
لم يتم اضافة القناة/الجروب, تأكد من التالي قبل الاضافة

- أضف البوت مشرف مع صلاحيات اضافة الأعضاء/انشاء روابط الدعوة
- اذا كان الرابط لا يعمل أرسل الايدي
''', buttons=[[Button.inline('🔙 رجوع', 'back_to_join_channels')]])
            return

        try:
            invite_link = await bot(ExportChatInviteRequest(
                peer=channel_entity.id,
            ))
        except:invite_link = None

        if invite_link == None:
            await event.respond(f'''
لم يتم اضافة القناة/الجروب, تأكد من التالي قبل الاضافة

- أضف البوت مشرف مع صلاحيات اضافة الأعضاء/انشاء روابط الدعوة
''', buttons=[[Button.inline('🔙 رجوع', 'back_to_join_channels')]])
            return
        

        # ADD CHANNEL
        cursor.execute(
            """
            INSERT INTO join_channels 
            (channel_id, title, invite_link) 
            VALUES (?, ?, ?)
            """,
            (channel_entity.id, channel_entity.title, invite_link.link,)
        )
        database.commit()

    except:pass
    await FirstJoin(event)



# Delete Channel
@bot.on(events.CallbackQuery(data='delete_channel'))
async def DeleteChannel(event):

    await DeleteEvent(event)
    join_channels_data = cursor.execute('SELECT * FROM join_channels')
    join_channels_data = cursor.fetchall()

    buttons = []
    for item in join_channels_data:
        buttons.append([Button.inline(f'❌ {item[1]}', f'deleteJoinChannel_{item[0]}')])

    buttons.append([Button.inline('🔙 رجوع', 'back_to_join_channels')])
    await event.respond('__اضغط على زر القناة أو الجروب لحذفه من الاشتراك الاجباري:__', buttons=buttons)


# Delete Join Channel
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'deleteJoinChannel_')))
async def DeleteJoinChannel(event):
    
    channel_id = int(str(event.data.decode()).replace('deleteJoinChannel_', '').strip())
    join_channels_data = cursor.execute(f'SELECT * FROM join_channels WHERE channel_id = {channel_id}')
    join_channels_data = cursor.fetchone()

    if join_channels_data != None:
        cursor.execute(f'DELETE FROM join_channels WHERE channel_id = {channel_id}')
        database.commit()
    
    await DeleteChannel(event)



# Settings Section
@bot.on(events.CallbackQuery(data='settings_section'))
async def SettingsSection(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)

    maintenance_mode = bot_configs['is_bot_in_maintenance_mode']
    maintenance_text = 'معطل ❌' if maintenance_mode else 'شغال ✅'

    youtube_text = f"تحميل يوتيوب {'✅' if bot_configs['is_youtube_enabled'] else '❌'}"
    facebook_text = f"تحميل فيسبوك {'✅' if bot_configs['is_facebook_enabled'] else '❌'}"

    instagram_text = f"تحميل انتستقرام {'✅' if bot_configs['is_instagram_enabled'] else '❌'}"
    tiktok_text = f"تحميل تيكتوك {'✅' if bot_configs['is_tiktok_enabled'] else '❌'}"

    pinterest_text = f"تحميل بنترست {'✅' if bot_configs['is_pinterest_enabled'] else '❌'}"
    snapchat_text = f"تحميل سناب شات {'✅' if bot_configs['is_snapchat_enabled'] else '❌'}"

    likee_text = f"تحميل لايكي {'✅' if bot_configs['is_likee_enabled'] else '❌'}"
    jaco_text = f"تحميل جاكو {'✅' if bot_configs['is_jaco_enabled'] else '❌'}"

    twitter_text = f"تحميل تويتر {'✅' if bot_configs['is_twitter_enabled'] else '❌'}"
    tiktok_account_text = f"معلومات التيكتوك {'✅' if bot_configs['is_tiktokAccount_enabled'] else '❌'}"

    buttons = [
        [Button.inline(f'حالة البوت : {maintenance_text}', 'editBotStatus')],
        [
            Button.inline(youtube_text, 'toogle_youtube'),
            Button.inline(facebook_text, 'toogle_facebook')
        ],
        [
            Button.inline(instagram_text, 'toogle_instagram'),
            Button.inline(tiktok_text, 'toogle_tiktok')
        ],
        [
            Button.inline(pinterest_text, 'toogle_pinterest'),
            Button.inline(snapchat_text, 'toogle_snapchat')
        ],
        [
            Button.inline(likee_text, 'toogle_likee'),
            Button.inline(jaco_text, 'toogle_jaco')
        ],
        [
            Button.inline(twitter_text, 'toogle_twitter'),
            Button.inline(tiktok_account_text, 'toogle_tiktokAccount')
        ]
    ]

    buttons.append([Button.inline('🔙 رجوع', 'back_to_adminpanel')])

    await event.respond('''__
تحكم في البوت من هنا:
                        
- يمكنك ايقاف تشغيل البوت في اي وقت

                        


__''', buttons=buttons)



# Edit Bot Status
@bot.on(events.CallbackQuery(data='editBotStatus'))
async def EditBotStatus(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_bot_in_maintenance_mode", False)
    bot_configs["is_bot_in_maintenance_mode"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs)

    # Send a response message to the user
    status_message = "تم تعطيل البوت!" if is_enabled else "تم تشغيل البوت!"
    await event.answer(status_message), await SettingsSection(event)




# Toogle Youtube
@bot.on(events.CallbackQuery(data='toogle_youtube'))
async def ToogleFacebook(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_youtube_enabled", False)
    bot_configs["is_youtube_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Facebook
@bot.on(events.CallbackQuery(data='toogle_facebook'))
async def ToogleFacebook(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_facebook_enabled", False)
    bot_configs["is_facebook_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Instagram
@bot.on(events.CallbackQuery(data='toogle_instagram'))
async def ToogleInstagram(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_instagram_enabled", False)
    bot_configs["is_instagram_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Tiktok
@bot.on(events.CallbackQuery(data='toogle_tiktok'))
async def ToogleTiktok(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_tiktok_enabled", False)
    bot_configs["is_tiktok_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Pinterest
@bot.on(events.CallbackQuery(data='toogle_pinterest'))
async def TooglePinterest(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_pinterest_enabled", False)
    bot_configs["is_pinterest_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)


# Toogle Snapchat
@bot.on(events.CallbackQuery(data='toogle_snapchat'))
async def ToogleSnapchat(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_snapchat_enabled", False)
    bot_configs["is_snapchat_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)


# Toogle Likee
@bot.on(events.CallbackQuery(data='toogle_likee'))
async def ToogleLikee(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_likee_enabled", False)
    bot_configs["is_likee_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Jaco
@bot.on(events.CallbackQuery(data='toogle_jaco'))
async def ToogleJaco(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_jaco_enabled", False)
    bot_configs["is_jaco_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Toogle Twitter
@bot.on(events.CallbackQuery(data='toogle_twitter'))
async def ToogleTwitter(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_twitter_enabled", False)
    bot_configs["is_twitter_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)


# Toogle Tiktok Account
@bot.on(events.CallbackQuery(data='toogle_tiktokAccount'))
async def ToogleTiktokAccount(event):
    global bot_configs

    # Toggle the notification setting
    is_enabled = not bot_configs.get("is_tiktokAccount_enabled", False)
    bot_configs["is_tiktokAccount_enabled"] = is_enabled

    # Save updated configuration
    await SaveJsonData(bot_configs), await SettingsSection(event)



# Admin Section
@bot.on(events.CallbackQuery(data='admin_section')) 
async def AdminSection(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return

    await DeleteEvent(event)
    buttons = [
        [Button.inline('➕ اضافة مشرف', 'add_admin'), Button.inline('➖ حذف مشرف', 'delete_admin')],
        [Button.inline('🔙 رجوع', 'back_to_adminpanel')]
    ]

    await event.respond(f'''__
✨ يمكنك اضافة أو حذف المشرفين من هنا بكل سهولة!

عدد المشرفين : {len(admins_list)}
__''', buttons=buttons)


# Add Admin
@bot.on(events.CallbackQuery(data='add_admin'))
async def AddAdmin(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return
    
    await DeleteEvent(event)
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message('__أرسل رابط أو معرف أو ايدي الشخص:__')
            admin_info = (await conv.get_response()).message

        try:
            if str(admin_info).isdigit():
                user_entity = await bot.get_entity(int(admin_info))
            else:
                user_entity = await bot.get_entity(str(admin_info))
            admin_id = user_entity.id
        except:user_entity, admin_id = None, None

        # ADD ADMIN
        if user_entity == None:
            await event.respond('__المعرف خاطئ أو الشخص لم يقم بارسال /start في بوت__')
        else:
            bot_configs['admins'].append(admin_id)
            await SaveJsonData(bot_configs)

    except:pass
    await AdminSection(event)


# Delete Admin
@bot.on(events.CallbackQuery(data='delete_admin'))
async def DeleteAdmin(event):

    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return
    
    await DeleteEvent(event)

    buttons = []
    for admin_id in admins_list:
        try:
            user_entity = await bot.get_entity(admin_id)
            name = user_entity.first_name
            username = f'( @{user_entity.username} )' if user_entity.username != None else ''
        except:
            name, username = admin_id, ''

        buttons.append([Button.inline(f'❌ {name} {username}', f'deleteAdminID_{admin_id}')])

    buttons.append([Button.inline('🔙 رجوع', 'back_to_admin_section')])
    await event.respond('__اضغط على زر المشرف لحذفه من مشرفين البوت:__', buttons=buttons)


# Delete Admin ID
@bot.on(events.CallbackQuery(data=lambda b: b.startswith(b'deleteAdminID_')))
async def DeleteAdminID(event):
    
    admins_list = bot_configs.get('admins')
    if event.chat_id not in admins_list and event.chat_id != OWNER_ID:
        return
    
    admin_id = int(str(event.data.decode()).replace('deleteAdminID_', '').strip())

    # DELETE ADMIN
    bot_configs['admins'].remove(admin_id)
    await SaveJsonData(bot_configs)
    
    await DeleteAdmin(event)


















################################################################
@bot.on(events.NewMessage(incoming=True))
async def DirectLink(event):


    url = event.message.message

    if str(url).startswith('/start'):
        return
    

    channels_list = cursor.execute('SELECT * FROM join_channels')
    channels_list = cursor.fetchall()
    if not event.is_group and not event.is_channel:
        # CHECK IF USER JOINED ALL CHANNELS
        user_joined_all = True
        for channel in channels_list:
            try:
                check_user = await bot(GetParticipantRequest(channel=int(channel[0]), participant=event.chat_id))
            except errors.UserNotParticipantError:
                user_joined_all = False
                break
            except Exception as error:pass

        if user_joined_all == False:
            channels_buttons = []
            for channel in channels_list:
                channels_buttons.append([Button.url(f'{channel[1]}', channel[2])])
            
            bot_data = await bot.get_me()
            channels_buttons.append([Button.url('✅ تحقق', f'https://t.me/{bot_data.username}?start=start')])
            await event.respond('__اشترك في قناتنا أولا ثم اضغط تحقق__', buttons=channels_buttons)
            return
        
    
    if str(url).startswith('/s'):
        await event.respond(f'''
✅ **الروابط المدعومة :**

__
01. https://www.youtube.com/watch?v=xxxxxx
02. https://youtu.be/xxxxxx 
03. https://www.facebook.com/PageName-OrID/videos/xxxxxx/
04. https://web.facebook.com/watch/?v=xxxxxx
05. https://fb.watch/xxxxxx/
06. https://www.instagram.com/p/xxxxxx/                
07. https://www.tiktok.com/@username
08. @username ( tiktok username )
09. https://www.tiktok.com/@username/video/xxxxxx
10. https://www.tiktok.com/@username/photo/xxxxxx
11. https://vm.tiktok.com/xxxxxx/
12. https://vt.tiktok.com/xxxxxx/
13. https://www.pinterest.com/pin/xxxxxx/
14. https://pin.it/xxxxxx
15. https://www.snapchat.com/p/xxxxxx
16. https://snapchat.com/t/xxxxxx
17. https://t.snapchat.com/xxxxxx
18. https://l.likee.video/v/xxxxxx
19. https://l.jaco.live/xxxxxx                         
20. https://x.com/username/status/xxxxxx
21. https://twitter.com/username/status/xxxxxx
22. https://www.instagram.com/reel/xxxxxx
__''', buttons=[[Button.inline('🔙 رجوع', 'back_to_menu')]])
        return
    
    if str(url).startswith('/developer'):
        await event.respond('__This bot was developer by @Zkada__')
        return

    if event.chat_id not in download_list:
        print(f'checking : {url}')

        pattern = r"^(?:https:\/\/www\.tiktok\.com\/)?@[\w.]+$"
        if re.match(pattern, url):
            print(f'checked 1 : {url}')
            await TiktokAccount(event, target_url=url)
            return
        
        if str(url).startswith('@'):
            print(f'checked 2 : {url}')
            await TiktokAccount(event, target_url=url)
            return
        
        if str(url).startswith('http'):
            if "youtube.com/watch" in url or "youtu.be" in url:
                print(f'checked 3 : {url}')
                await DownloadYoutube(event, target_url=url)
                return

            if "facebook.com" in url or "fb.watch" in url:
                print(f'checked 4 : {url}')
                await DownloadFacebook(event, target_url=url)
                return

            if "instagram.com/p" in url or "instagram.com/reel" in url:
                print(f'checked 5 : {url}')
                await DownloadInstagram(event, target_url=url)
                return

            # if "tiktok.com" in url:
            #     await DownloadTiktok(event, target_url=url)
            #     return
            if (url.startswith("https://www.tiktok.com/@") and "/video/" in url) or url.startswith("https://vm.tiktok.com/"):
                await DownloadTiktok(event, target_url=url)
                return
            
            if (url.startswith("https://www.tiktok.com/@") and "/photo/" in url) or url.startswith("https://vt.tiktok.com/"):
                await DownloadTiktok(event, target_url=url)
                return
        
            if "pinterest" in url or "pin.it" in url:
                await DownloadPinterest(event, target_url=url)
                return

            if "snapchat.com/t" in url or "snapchat.com/p" in url:
                await DownloadSnapchat(event, target_url=url)
                return
            
            # https://t.snapchat.com/AUoQB0qp
            if "t.snapchat.com" in url:
                await DownloadSnapchat(event, target_url=url)
                return

            if "likee" in url:
                await DownloadLikee(event, target_url=url)
                return

            if "jaco" in url:
                await DownloadJaco(event, target_url=url)
                return

            if "twitter" in url or "x.com" in url:
                await DownloadTwitter(event, target_url=url)
                return
            
            await event.respond('__الرابط غير مدعوم, أرسل /s لمعرفة الروابط المدعومة__')

        # else:
        #     pattern = r'^[a-zA-Z0-9_.]{2,24}$'
        #     if re.match(pattern, url) and not (url.startswith('.') or url.endswith('.')):
        #         await TiktokAccount(event, target_url=f'@{url}')


# Record Download
async def RecordDownload(event, download_type, download_link, download_date):
    try:
        # Insert into download_history
        cursor.execute(
            """
            INSERT INTO download_history 
            (download_by, download_type, download_link, download_date) 
            VALUES (?, ?, ?, ?)
            """,
            (event.chat_id, download_type, download_link, download_date,)
        )

        # Fetch user data
        cursor.execute('SELECT * FROM bot_users WHERE user_id = ?', (event.chat_id,))
        user_data = cursor.fetchone()

        if user_data:
            # Update today_downloads and last_download_date in one query
            today_search = int(user_data[5]) + 1
            cursor.execute(
                '''
                UPDATE bot_users 
                SET today_downloads = ?, last_download_date = ?
                WHERE user_id = ?
                ''',
                (today_search, download_date, event.chat_id,)
            )

                
        # Commit transaction
        database.commit()
        
    except Exception as error:print(f'RecordDownload: {error}')



async def check_user_ban_vip(event):
    user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
    user_data = cursor.fetchone()

    bot_settings_data = cursor.execute('SELECT * FROM bot_settings WHERE setting_id = 1')
    bot_settings_data = cursor.fetchone()

    download_limit = bot_settings_data[1]
    is_vip, today_download_count, last_download_date = user_data[2], user_data[5], user_data[6]
    user_banned = user_data[7]

    if user_banned == 'YES':
        await event.respond('__تم حظرك من استخدام خدمات هذا البوت__')
        return True
    
    if is_vip:
        vip_datetime = datetime.strptime(str(is_vip), '%Y-%m-%d %H:%M:%S')
        current_datetime = datetime.now()

        # Check if VIP is expired
        if current_datetime > vip_datetime:
            await event.respond('__اشتراكك لقد انتهى, أنت الان في العضوية المجانية__')
            cursor.execute(f'UPDATE bot_users SET is_vip = NULL WHERE user_id = {event.chat_id}')
            cursor.execute(f'UPDATE bot_users SET last_download_date = NULL WHERE user_id = {event.chat_id}')
            database.commit()

            user_data = cursor.execute(f'SELECT * FROM bot_users WHERE user_id = {event.chat_id}')
            user_data = cursor.fetchone()
            is_vip, today_download_count, last_download_date = user_data[2], user_data[5], user_data[6]


    if not is_vip:
        if today_download_count == None:
            today_download_count = 0
            cursor.execute(f'UPDATE bot_users SET today_downloads = 0 WHERE user_id = {event.chat_id}')
            database.commit()

        if today_download_count >= download_limit:
            if last_download_date != None:
                last_download_date = datetime.strptime(str(last_download_date), '%Y-%m-%d %H:%M:%S')
                current_datetime = datetime.now()

                # Check if 24 hours have passed
                time_difference = current_datetime - last_download_date
                remaining_time = timedelta(hours=24) - time_difference
                if time_difference >= timedelta(hours=24):
                    cursor.execute(f'UPDATE bot_users SET today_downloads = 0 WHERE user_id = {event.chat_id}')
                    cursor.execute(f'UPDATE bot_users SET last_download_date = NULL WHERE user_id = {event.chat_id}')
                    database.commit()
                else:
                    hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    buttons = [[Button.inline('🔙 رجوع', 'back_to_menu')]]
                    await event.reply(f"__وصلت للحد الاقصى لعمليات التحميل اليومية, سيتم تصفير بعد {int(hours)} ساعة, {int(minutes)} دقيقة, و {int(seconds)} ثانية.__", buttons=buttons)
                    return True
            
            else:
                await event.reply('وصلت للحد الأقصى لعمليات التحميل اليومية')
                return True



# Tiktok Account
@bot.on(events.CallbackQuery(data='tiktok_account'))
async def TiktokAccount(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_tiktokAccount_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم كشف حسابات التيك توك!**

**- الروابط المدعومة:**__
1. https://www.tiktok.com/@username
2. @username
__
**للبدء، أرسل رابط/يوزر الحساب الذي ترغب كشفه!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url

        print ('account', url)
        if "tiktok.com" in url or str(url).startswith('@'):
            if str(url).startswith('@'):
                url = f'https://www.tiktok.com/{url}'
            
            msg_update1 = await event.respond("__🚀 جاري جلب المعلومات, انتظر قليلا...__")

            message, link_list = "", {}
            data = await get_tiktok_account_info(url)
            if data != None:
                message, link_list = await process_json(data, message, link_list)

            if data == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب المعلومات, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)

                bot_me = await bot.get_me()
                buttons = []

                for key, value in link_list.items():
                    buttons.append([Button.url(f'🔗 {key} 🔗', f'{value}')])
                buttons.append([Button.inline('🔙 رجوع', 'back_to_menu')])

                await bot.send_message(entity=event.chat_id, message=f'{message}\n\n@{bot_me.username}', buttons=buttons)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "tiktok Account Info", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except tiktok account info : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Youtube
@bot.on(events.CallbackQuery(data='download_youtube'))
async def DownloadYoutube(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_youtube_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try: 
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل الفيديوهات من اليوتيوب!**

**- الروابط المدعومة:**__
1. https://www.youtube.com/watch?v=xxxxxx
2. https://youtu.be/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "youtube.com/watch" in url or "youtu.be" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await youtube_download_up_to_720p(url, f'downloads/{q_id}')

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                
                video_data = await get_video_length_and_size(path)

                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline(f'⏳ المدة: {video_data.get("duration_seconds")}', 'length'), Button.inline(f'📦 الحجم: {video_data.get("size_mb")} MB', 'size')],
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}', buttons=buttons)
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "youtube", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except youtube : {error}')


    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Facebook
@bot.on(events.CallbackQuery(data='download_facebook'))
async def DownloadFacebook(event, target_url=None):

    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_facebook_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل الفيديوهات من الفيسبوك!**

**- الروابط المدعومة:**__
1. https://www.facebook.com/PageName-OrID/videos/xxxxxx/
2. https://web.facebook.com/watch/?v=xxxxxx
3. https://fb.watch/xxxxxx/
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "facebook.com" in url or "fb.watch" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await facebook_download_best_quality_video(url, f'downloads/{q_id}')

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                
                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}', buttons=buttons)
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "facebook", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except facebook : {error}')

    if event.chat_id in download_list:
            download_list.remove(event.chat_id)


# Download Instagram
@bot.on(events.CallbackQuery(data='download_instagram'))
async def DownloadInstagram(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_instagram_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل منشورات من الانستجرام!**

**- الروابط المدعومة:**__
1. https://www.instagram.com/p/xxxxxx/
2. https://www.instagram.com/reel/xxxxxx
__
**للبدء، أرسل رابط المنشور الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "instagram.com/p" in url or "instagram.com/reel" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            paths = await download_instagram_post_imageV2(url, f'{q_id}')
            
            if paths == None or len(paths) == 0:
                paths = [await TwitterDownload(url, f'{q_id}')]

            if paths == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                
                bot_me = await bot.get_me()
                
                for path in paths:
                    if not str(path).endswith('.txt') and not str(path).endswith('.xz'):
                        await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}')
                        await DeleteEvent(msg_update2)


                # Extract user information
                for path in paths:
                    if str(path).endswith('.xz'):
                        parsed_data = await open_and_print_json(path)
                        if parsed_data != None:
                            not_found = 'غير متاح'
                            user_info = parsed_data["node"]["owner"]
                            username = user_info.get("username", not_found)
                            full_name = user_info.get("full_name", not_found)
                            is_verified = user_info.get("is_verified", not_found)
                            posts = user_info.get("edge_owner_to_timeline_media", {}).get("count", not_found)
                            followers = user_info.get("edge_followed_by", {}).get("count", not_found)
                            profile_pic_url = user_info.get("profile_pic_url", not_found)
                            profile_url = f'https://www.instagram.com/{username}/'

                            buttons = [
                                [Button.url(f'👤 @{username}', profile_url)],
                                [Button.inline(f'📛 اسم الحساب: {full_name}', 'full_name')],
                                [Button.inline(f'✅ حساب موثق: {is_verified}', 'is_verified')],
                                [Button.inline(f'👥 المتابعين: {followers}', 'followers'), Button.inline(f'🖼️ المنشورات: {posts}', 'posts')],
                                [Button.inline('🔙 رجوع', 'back_to_menu')]
                            ]

                            await bot.send_message(entity=event.chat_id, file=profile_pic_url, message=f'@{bot_me.username}', buttons=buttons)

                try:
                    folder_path = f'{q_id}'
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                except:pass
                await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "instagram", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        try:
            folder_path = f'{q_id}'
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except:pass
        print(f'except instagram : {error}')

    
    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Tiktok
@bot.on(events.CallbackQuery(data='download_tiktok'))
async def DownloadTiktok(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_tiktok_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من التيكتوك!**

**- الروابط المدعومة:**__
1. https://www.tiktok.com/@username/video/xxxxxx
2. https://www.tiktok.com/@username/photo/xxxxxx
3. https://vm.tiktok.com/xxxxxx/
4. https://vt.tiktok.com/xxxxxx/
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        # if "tiktok.com" in url:
        if (url.startswith("https://www.tiktok.com/@") and "/video/" in url) or url.startswith("https://vm.tiktok.com/") or (url.startswith("https://www.tiktok.com/@") and "/photo/" in url) or url.startswith("https://vt.tiktok.com/"):
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            # else:
            #     path = await download_tiktok_video(url, f'downloads/{q_id}')

            # if path == None:
            #     path = await download_tiktok_video(url, f'downloads/{q_id}')

            paths = await download_tiktok_video(url, f'downloads/{q_id}')
            
            if paths == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                
                sent_message = None
                for path in paths:
                    print ("download paths:", paths)
                    sent_message = await bot.send_message(entity=event.chat_id, file=path)
                    # print(sent_message.media)
                    break

                if (url.startswith("https://www.tiktok.com/@") and "/photo/" in url) or url.startswith("https://vt.tiktok.com/"):
                    try:
                        path, data = await download_tiktok_image(url, f'downloads/{q_id}')
                    except:
                        path = None
                        data = False

                if (url.startswith("https://www.tiktok.com/@") and "/photo/" in url) or (url.startswith("https://vt.tiktok.com/")):
                    pass
                else:
                    data = await get_tiktok_infoV2(url)

                if data == False:
                    data = await get_tiktok_infoV2(url)
                    
                if data == None:
                    data = await fetch_tiktok_data(url)

                if sent_message and path and str(sent_message.media).startswith('MessageMediaPhoto'):
                    print("send:", path)
                    try:
                        await bot.send_message(entity=event.chat_id, file=path)
                    except:pass

                # new API
                import requests

                if data.get("followerCount") == None or data.get("heart") == None:
                    openUrl = requests.get(url, allow_redirects=True)
                    pattern = r"(https://www\.tiktok\.com/@[\w.-]+)"
                    match = re.search(pattern, openUrl.url)

                    if match:
                        new_url = match.group(1)
                        scrap_data = await get_tiktok_account_info(new_url)

                        # countine
                        data["id"] = scrap_data.get("id")
                        data["account_username"] = scrap_data.get("uniqueId")
                        data["account_name"] = scrap_data.get("nickname")
                        data["profile_image_url"] = scrap_data.get("arLarger")
                        data["account_verified"] = scrap_data.get("verified")

                        data["account_bio"] = scrap_data.get("signature")
                        data["followerCount"] = scrap_data.get("user_stats").get("followerCount")
                        data["followingCount"] = scrap_data.get("user_stats").get("followingCount")
                        data["heart"] = scrap_data.get("user_stats").get("heart")
                        data["heartCount"] = scrap_data.get("user_stats").get("heartCount")
                        data["videoCount"] = scrap_data.get("user_stats").get("videoCount")
                        # data["playCount"] = scrap_data.get("user_stats").get("videoCount")
                        data["account_diggCount"] = scrap_data.get("user_stats").get("diggCount")
                        data["friendCount"] = scrap_data.get("user_stats").get("friendCount")
                        data["locationCreated"] = scrap_data.get("region")


                # end new API

                try:
                    video_data = await get_video_length_and_size(path)
                except:
                    video_data = {
                        "duration_seconds": "0",
                        "size_bytes": "0",
                        "size_mb": "0"
                    }

                bot_me = await bot.get_me()
                buttons = [
                    [Button.url(f'👨🏻‍💻 الحساب : @{data.get("account_username")}', f'https://www.tiktok.com/@{data.get("account_username")}')],
                    [Button.inline(f'📛 الاسم : {data.get("account_name")}', 'tiktok_account_name'), Button.inline(f'موثق : {"✅ نعم" if data.get("account_verified") else "❌ لا"}', 'tiktok_account_verified')],
                    # [Button.inline(f'📸 صورة الحساب', f'tiktok_profile_image_url')],
                    [Button.inline(f'👍 الإعجابات : {data.get("likes")}', 'tiktok_likes'), Button.inline(f'💬 التعليقات : {data.get("comments")}', 'tiktok_comments')],
                    [Button.inline(f'⭐ المفضلات : {data.get("favorites")}', 'tiktok_favorites'), Button.inline(f'🔄 المشاركات : {data.get("shares")}', 'tiktok_shares')],
                    [Button.inline(f'👀 المشاهدات : {data.get("playCount")}', 'tiktok_play_count')],
                    [Button.inline(f'⏱ مدة الفيديو : {video_data.get("duration_seconds")}', 'length'), Button.inline(f'📦 الحجم: {video_data.get("size_mb")} MB', 'size')],
                    [Button.inline(f'👥 المتابعون : {data.get("followerCount")}', 'tiktok_follower_count'), Button.inline(f'👤 المتابعهم : {data.get("followingCount")}', 'tiktok_following_count')],
                    [Button.inline(f'❤️ القلوب : {data.get("heart")}', 'tiktok_heart'), Button.inline(f'💖 القلوب الكلية : {data.get("heartCount")}', 'tiktok_heart_count')],
                    [Button.inline(f'🎥 عدد الفيديوهات : {data.get("videoCount")}', 'tiktok_video_count')],
                    [Button.inline(f'👯‍♂️ الأصدقاء : {data.get("friendCount")}', 'tiktok_friend_count')],
                    [Button.inline(f'📍 موقع الإنشاء : {data.get("locationCreated")}', 'tiktok_location_created')],
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                if data.get("profile_image_url") == 'غير متاح':
                    pic_url = None
                else:
                    pic_url = data.get("profile_image_url")

                # await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}')
                await bot.send_message(entity=event.chat_id, file=pic_url, 
                    message=f'📝 BIO : {data.get("account_bio")}\n\n@{bot_me.username}',
                    buttons=buttons, force_document=False)
                
                await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "tiktok", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except tiktok : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Pinterest
@bot.on(events.CallbackQuery(data='download_pinterest'))
async def DownloadPinterest(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_pinterest_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من بينتريست!**

**- الروابط المدعومة:**__
1. https://www.pinterest.com/pin/xxxxxx/
2. https://pin.it/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "pinterest" in url or "pin.it" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await download_pinterest_video(url, f'downloads/{q_id}')

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")

                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}', buttons=buttons)
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "pinterest", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except pinterest : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Snapchat
@bot.on(events.CallbackQuery(data='download_snapchat'))
async def DownloadSnapchat(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_snapchat_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من بناب شات!**

**- الروابط المدعومة:**__
1. https://www.snapchat.com/p/xxxxxx
2. https://snapchat.com/t/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "snapchat.com/t" in url or "snapchat.com/p" in url or "t.snapchat.com" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            json_dict = await get_json(url)

            if json_dict:
                paths = await download_media(json_dict)
            else:paths = None

            if len(paths) == 0:
                paths = await SnapchatDownload(url, f'downloads/{q_id}')

            if paths == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                if json_dict:
                    user_data = await get_snapchat_info(json_dict)
                else:
                    user_data = await scrape_snapchat_profile(url)

                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline(f'👨🏻‍💻 الحساب: {user_data.get("title")}', 'title')],
                    [Button.inline(f'🖋️ الاسم المستخدم: {user_data.get("username")}', 'username')],
                    [Button.inline(f'📍 العنوان: {user_data.get("address")}', 'address')],
                    [Button.inline(f'👥 عدد المتابعين: {user_data.get("subscriberCount")}', 'subscriber_count'), Button.inline(f'🥽 عدد الستوري: {len(paths)}', 'story_count')],
                    [Button.inline('🔙 رجوع', 'back_to_menu')],
                ]

                the_message = f'''
📖 السيرة الذاتية: {user_data.get("bio")}

🌐 الموقع الإلكتروني: {user_data.get("websiteUrl")}
@{bot_me.username}
'''

                for path in paths:
                    print(path)
                    path = path
                    try:
                        await bot.send_message(entity=event.chat_id, file=path)
                    except Exception as error:
                        path = await download_file(path, 'temp_do.jpg')
                        if path:
                            await bot.send_message(entity=event.chat_id, file=path)

                    await DeleteFile(path), await DeleteEvent(msg_update2)

                profilePictureUrl = user_data.get("profilePictureUrl")
                if profilePictureUrl == None or profilePictureUrl == 'غير متاح':
                    await bot.send_message(entity=event.chat_id, message=the_message, buttons=buttons)
                else:
                    path = await download_file(profilePictureUrl, 'temp_do.jpg')
                    await bot.send_message(entity=event.chat_id, file=path, message=the_message, buttons=buttons)
                    await DeleteFile(path)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "snapchat", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except snapchat : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Likee
@bot.on(events.CallbackQuery(data='download_likee'))
async def DownloadLikee(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_likee_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من لايكي!**

**- الروابط المدعومة:**__
1. https://l.likee.video/v/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "likee.video/v" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await LikeeDownload(url, f'downloads/{q_id}') #multi_download_video

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")

                bot_me = await bot.get_me()
                buttons = [[Button.inline('🔙 رجوع', 'back_to_menu')]]
                await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}', buttons=buttons)
            
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "likee", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except likee : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Jaco
@bot.on(events.CallbackQuery(data='download_jaco'))
async def DownloadJaco(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_jaco_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return

    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من جاكو!**

**- الروابط المدعومة:**__
1. https://l.jaco.live/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "jaco.live/" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await download_jaco_video(url, f'downloads/{q_id}')

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")

                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                await bot.send_message(entity=event.chat_id, file=path, message=f'@{bot_me.username}', buttons=buttons)
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "jaco", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except jaco : {error}')

    if event.chat_id in download_list:
        download_list.remove(event.chat_id)


# Download Twitter
@bot.on(events.CallbackQuery(data='twitter_section'))
async def DownloadTwitter(event, target_url=None):
    global download_list

    maintenance_mode = bot_configs.get('is_bot_in_maintenance_mode')
    if event.chat_id != OWNER_ID and event.chat_id not in bot_configs.get('admins') and maintenance_mode:
        await event.respond('__البوت معطل حاليا, سنعود قريبا 😊__')
        return
    
    if not bot_configs['is_twitter_enabled']:
        await event.answer('هذه الخدمة متوقفة حاليا', alert=True)
        return

    await DeleteEvent(event)
    stop = await check_user_ban_vip(event)
    if stop == True:
        return
    
    try:
        async with bot.conversation(event.chat_id, timeout=120) as conv:
            if target_url == None:
                if event.chat_id not in download_list:
                    download_list.append(event.chat_id)
                await conv.send_message(f'''
**• مرحبًا بك في قسم تحميل فيديوهات من تويتر!**

**- الروابط المدعومة:**__
1. https://x.com/username/status/xxxxxx
2. https://twitter.com/username/status/xxxxxx
__
**للبدء، أرسل رابط الفيديو الذي ترغب في تحميله!**
''', link_preview=False)
                url = (await conv.get_response()).message
            else:
                url = target_url
        
        if "twitter" in url or "x.com" in url:
            msg_update1 = await event.respond("__🚀 جاري جلب الفيديو, انتظر قليلا...__")

            q_id = await generate_random_id()
            path = await TwitterDownload(url, f'downloads/{q_id}') # multi_download_video

            if path == None:
                await event.respond(
                    '__حدث خطأ أثناء جلب الفيديو, أعد المحاولة مرة اخرى__',
                    buttons=[[Button.inline('رجوع', 'back_to_menu')]]
                )
            else:
                await DeleteEvent(msg_update1)
                msg_update2 = await event.respond("__🚀 تم جلب الفيديو جاري الارسال, انتظر قليلا...__")
                await bot.send_message(entity=event.chat_id, file=path)

                image_url, reposts, quotes, likes, bookmarks = await GetTwitterInfoV2(url) # await extract_tweet_data(url)
                bot_me = await bot.get_me()
                buttons = [
                    [Button.inline(f'🔁 Reposts: {reposts}', 'reposts'), Button.inline(f'💬 Quotes: {quotes}', 'quotes')],
                    [Button.inline(f'❤️ Likes: {likes}', 'likes'), Button.inline(f'🔖 Bookmarks: {bookmarks}', 'bookmarks')],
                    [Button.inline('🔙 رجوع', 'back_to_menu')]
                ]

                await bot.send_message(entity=event.chat_id, message=f'@{bot_me.username}', buttons=buttons)
                await DeleteFile(path), await DeleteEvent(msg_update2)

                # Record Download
                download_date = datetime.now().replace(microsecond=0)
                await RecordDownload(event, "twitter", url, download_date)
        else:
            await event.respond("__الرابط الذي أرسلته غير مدعوم!__")

    except Exception as error:
        await event.respond('__عذرا يوجد ضغط على هذه الخدمة حاليا, حاول مجددا بعد عدة دقائق__', buttons=[[Button.inline('رجوع', 'back_to_menu')]])
        print(f'except twitter : {error}')


    if event.chat_id in download_list:
        download_list.remove(event.chat_id)











# RUN
print ('bot working...')
bot.run_until_disconnected()