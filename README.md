## بوت تحميل الفيديوهات (Telegram)

- يعتمد على Pyrogram و yt-dlp.
- يدعم وضعين للمصادقة: `BOT_TOKEN` (بوت عادي) أو `SESSION_STRING` (حساب مستخدم/يوزربوت).

### المتطلبات
- Python 3.10+

### التثبيت
```bash
python3 -m pip install --break-system-packages -r requirements.txt
```

### الإعداد
- انسخ `.env.example` إلى `.env` وعدّل القيم:
```
API_ID=123456
API_HASH=0123456789abcdef0123456789abcdef
# اختر واحد فقط من التاليين:
BOT_TOKEN=
SESSION_STRING=

# اختياري
DOWNLOAD_DIR=downloads
MAX_FILE_SIZE_MB=1900
OWNER_ID=
```

- إذا أردت استخدام جلسة مستخدم بدل تسجيل الدخول في كل تشغيل، ضع قيمة `SESSION_STRING` هنا. يمكنك توليدها عبر سكربت صغير باستخدام Pyrogram مرة واحدة:
```python
from pyrogram import Client
from pyrogram.session import StringSession

api_id = int(input("API_ID: "))
api_hash = input("API_HASH: ")
with Client(name="gen", api_id=api_id, api_hash=api_hash) as app:
    print("SESSION_STRING=", app.export_session_string())
```
- انسخ ناتج `SESSION_STRING` إلى ملف `.env`.

### التشغيل
```bash
python3 app.py
```

- أرسل رابط فيديو (YouTube, TikTok, Instagram, Twitter, ...). سيقوم البوت بتنزيله وإرساله لك.

### ملاحظات
- يتم احترام الحد الأقصى للحجم عبر `MAX_FILE_SIZE_MB` مع محاولة تخفيض الجودة تلقائيًا.
- الملفات المؤقتة يتم حفظها في مجلد `downloads/` ثم حذفها بعد الإرسال.