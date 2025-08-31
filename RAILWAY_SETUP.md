# دليل النشر على Railway - خطوة بخطوة

## 🚄 إعداد Railway للبوت

### 1. إنشاء المشروع
- اذهب لـ [railway.app](https://railway.app)
- سجل دخول أو أنشئ حساب جديد
- اضغط "New Project"
- اختر "Deploy from GitHub repo"

### 2. ربط GitHub Repository
- اختر repository: `telegram-channel-guard-bot`
- اضغط "Deploy Now"

### 3. إعداد المتغيرات (Variables)
- اذهب لـ Variables tab
- أضف متغير جديد:
  ```
  TELEGRAM_BOT_TOKEN = your_actual_bot_token_here
  ```

### 4. إعداد Start Command (مهم جداً!)
- اذهب لـ **Settings** → **Deploy**
- ابحث عن **"Start Command"**
- احذف أي command موجود
- اكتب: `python3 run_bot.py`
- احفظ التغييرات

### 5. تغيير نوع الخدمة (موصى به)
- في الـ Dashboard الرئيسي
- غير اسم الخدمة من "web" إلى "bot" أو "worker"
- هذا يمنع Railway من توقع HTTP port

### 6. إعادة النشر
- اضغط **"Redeploy"** 
- أو ادفع أي تعديل للكود على GitHub

## 📊 مراقبة الحالة

### فحص اللوجات:
- اذهب لـ **Deployments** tab
- اضغط على آخر deployment
- راقب اللوجات وابحث عن:
  ```
  Bot started and ready!
  Application started
  ```

### علامات النجاح:
✅ لا توجد أخطاء في اللوجات  
✅ ظهور رسالة "Bot started"  
✅ الخدمة تظهر "Running" وليس "Crashed"  
✅ البوت يرد على `/start` في تليجرام  

## 🔧 حل المشاكل الشائعة

### مشكلة: "Port already in use"
**الحل**: تأكد من Start Command: `python3 run_bot.py`

### مشكلة: "Application crashed"
**الحل**: تحقق من TELEGRAM_BOT_TOKEN في Variables

### مشكلة: "Bot not responding"
**الحل**: تحقق من اللوجات للأخطاء

## 📋 Checklist النهائي

- [ ] GitHub repository متصل
- [ ] TELEGRAM_BOT_TOKEN مُضاف في Variables
- [ ] Start Command: `python3 run_bot.py`
- [ ] نوع الخدمة worker (ليس web)
- [ ] Deployment ناجح بدون أخطاء
- [ ] البوت يرد في تليجرام

---
**بعد اتباع هذه الخطوات، البوت سيعمل 24/7 على Railway بدون توقف!**