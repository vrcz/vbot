import os
import re
from telethon import TelegramClient, events
import yt_dlp
import asyncio

from config import API_ID, API_HASH, BOT_TOKEN, DEVELOPER_ID, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
from check import check_subscription  # استيراد دالة التحقق من الاشتراك

# إنشاء عميل Telegram
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# دالة لتحميل الفيديو
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',  # اسم ملف ثابت لتجنب مشكلة طول الاسم
        'noplaylist': True,
        'username': INSTAGRAM_USERNAME,  # إضافة اسم المستخدم
        'password': INSTAGRAM_PASSWORD,  # إضافة كلمة المرور
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            video_info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(video_info)
            return filename
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

# حدث لمعالجة الأوامر
@client.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    men = f"[{event.sender.first_name}](tg://user?id={user_id})"
    
    # سجل المستخدم والرسالة
    # add_user(user_id)  # تعليق لأننا لا نتعامل مع قاعدة البيانات هنا
    
    # تحقق من الاشتراك في القنوات المطلوبة إذا لم يكن المستخدم هو المطور
    if user_id != DEVELOPER_ID and not await check_subscription(client, user_id):
        await event.respond('يجب عليك الاشتراك في القنوات التالية لاستخدام هذا البوت:\n@voltbots\n@ctktc')
        return
    
    # تحقق مما إذا كانت الرسالة تحتوي على رابط
    urls = re.findall(r'(https?://\S+)', event.message.message)
    
    if event.message.message == '/start':
        await event.respond(f'مرحبًا عزيزي {men} \n أرسل لي رابط الفيديو وسأقوم بتحميله لك')
    elif urls:
        url = urls[0]
        status_message = await event.respond('**جاري تحميل الفيديو...**')
        
        video_path = download_video(url)
        if video_path:
            await client.send_file(event.chat_id, video_path)
            os.remove(video_path)
            await event.respond(f'**تم تحميل الفيديو بنجاح✅**')
        else:
            await event.respond('**فشل في تحميل الفيديو❌**')
        
        await status_message.delete()
    elif event.message.message == '/stats' and user_id == DEVELOPER_ID:
        # اضافة الاحصائيات هنا
        await event.respond('الإحصائيات')

# بدء العميل
client.run_until_disconnected()
