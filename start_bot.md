# تشغيل بوت تليجرام

## المشكلة
مكتبة python-telegram-bot تتطلب العمل في الـ main thread ولا يمكن تشغيلها في Replit workflows.

## الحل - التشغيل المباشر

### 1. افتح Terminal جديد في Replit

### 2. شغل البوت مباشرة:
```bash
python3 run_bot.py
```

### 3. البوت سيبدأ والرسائل ستظهر:
```
INFO - Starting Telegram bot in main thread...
INFO - Bot started and ready!
```

### 4. للتحقق من الـ HTTP server:
في terminal آخر:
```bash
curl http://localhost:5000/
```

## ملاحظات مهمة:
- لا تستخدم Replit workflows للبوت
- البوت يعمل فقط في main thread
- HTTP server يعمل في background للـ health checks
- للإيقاف: اضغط Ctrl+C في terminal

## إعداد البوت:
تأكد من وجود TELEGRAM_BOT_TOKEN في البيئة:
- اذهب للـ Secrets tab في Replit
- أضف TELEGRAM_BOT_TOKEN مع قيمة التوكن

## الاستخدام:
1. أرسل /start للبوت في تليجرام
2. استخدم /help لرؤية الأوامر المتاحة
3. استخدم /add_channel لإضافة قناة للمراقبة