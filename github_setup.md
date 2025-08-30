# ربط المشروع بـ GitHub

## الملفات الجاهزة ✅
- `.gitignore` - لتجاهل الملفات غير المرغوبة
- `README.md` - وصف المشروع باللغة العربية
- جميع ملفات الكود محضرة ومنظمة

## خطوات الربط:

### 1. من واجهة Replit (الأسهل):
- افتح الـ sidebar الأيسر
- ابحث عن أيقونة GitHub أو Version Control
- اضغط "Connect to GitHub"
- اختر "Create new repository"

### 2. إنشاء Repository يدوياً:
1. اذهب لـ GitHub.com
2. اضغط "New repository"
3. اسم المشروع: `telegram-channel-guard-bot`
4. الوصف: `بوت تليجرام لحماية القنوات مع دعم العربية`
5. اختر Public أو Private
6. لا تختر Add README (موجود بالفعل)
7. اضغط "Create repository"

### 3. من Terminal (للمطورين):
```bash
# إضافة الملفات
git add .

# إنشاء commit
git commit -m "Initial commit: Telegram Channel Guard Bot"

# ربط المشروع بـ GitHub
git remote add origin https://github.com/[username]/[repository-name].git

# رفع الكود
git push -u origin main
```

## بعد الربط:
- ✅ المشروع سيكون متاحاً على GitHub
- ✅ يمكن استنساخه واستخدامه من أي مكان
- ✅ نسخ احتياطية تلقائية
- ✅ إمكانية التعاون مع آخرين

## نصائح:
- تأكد من عدم رفع `TELEGRAM_BOT_TOKEN` (محمي في .gitignore)
- استخدم رسائل commit واضحة بالعربية أو الإنجليزية
- احرص على تحديث README عند إضافة ميزات جديدة