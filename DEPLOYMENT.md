# دليل النشر - Deployment Guide

## 🚀 نشر البوت على منصات مختلفة

### Railway 🚄

1. **إنشاء حساب**: سجل في railway.app
2. **ربط GitHub**: اختر المشروع من GitHub
3. **إعداد المتغيرات**:
   - `TELEGRAM_BOT_TOKEN` = توكن البوت
4. **التشغيل**: Railway سيكتشف `requirements.txt` تلقائياً

### Heroku ☁️

1. **إنشاء تطبيق جديد**
2. **ربط GitHub Repository**
3. **إعداد Config Vars**:
   - `TELEGRAM_BOT_TOKEN` = توكن البوت
4. **تفعيل Worker**: 
   ```
   heroku ps:scale worker=1 -a your-app-name
   ```

### Render 🌐

1. **إنشاء Web Service جديد**
2. **ربط GitHub Repository**
3. **إعدادات البناء**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 run_bot.py`
4. **متغيرات البيئة**:
   - `TELEGRAM_BOT_TOKEN` = توكن البوت

### VPS / Server خاص 💻

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3 python3-pip -y

# استنساخ المشروع
git clone https://github.com/your-username/telegram-channel-guard-bot.git
cd telegram-channel-guard-bot

# تثبيت المتطلبات
pip3 install -r requirements.txt

# إعداد متغير البيئة
export TELEGRAM_BOT_TOKEN="your_token_here"

# تشغيل البوت
python3 run_bot.py

# أو للتشغيل في الخلفية
nohup python3 run_bot.py > bot.log 2>&1 &
```

### Docker 🐳

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "run_bot.py"]
```

## 📋 الملفات المطلوبة للنشر:

✅ `requirements.txt` - المكتبات (تم إعداده)  
✅ `Procfile` - إعدادات التشغيل (تم تحديثه)  
✅ `run_bot.py` - النقطة الرئيسية للتشغيل  
✅ جميع ملفات الكود الأساسية  

## 🔐 أمان النشر:

- ✅ **لا تشارك TELEGRAM_BOT_TOKEN** في الكود
- ✅ **استخدم متغيرات البيئة** في منصة النشر
- ✅ **فعل .gitignore** لحماية الملفات الحساسة
- ✅ **راجع الأذونات** قبل جعل المشروع public

## 🔧 اختبار بعد النشر:

1. **أرسل /start للبوت** في تليجرام
2. **تحقق من اللوجات** في منصة النشر
3. **اختبر الأوامر الأساسية**: /help, /status
4. **تحقق من HTTP endpoint**: `[app-url]/`

---
**ملاحظة**: تأكد من إعداد TELEGRAM_BOT_TOKEN في متغيرات البيئة لكل منصة نشر.