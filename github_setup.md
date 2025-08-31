# ربط المشروع بـ GitHub

## الملفات الجاهزة ✅
- `.gitignore` - لتجاهل الملفات غير المرغوبة
- `README.md` - وصف المشروع باللغة العربية
- `requirements.txt` - قائمة المكتبات المطلوبة
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

### 3. حل مشكلة Remote Origin الموجود:

إذا واجهت خطأ "UNKNOWN error adding origin"، اتبع هذه الخطوات:

```bash
# 1. شوف الـ remotes الحالية
git remote -v

# 2. امسح الـ remote القديم (إن وُجد)
git remote remove origin

# 3. أضف الـ repo الجديد
git remote add origin https://github.com/amarabdo8007/telegram-channel-guard-bot.git

# 4. أضف الملفات واعمل push
git add .
git commit -m "تحديث أولي: بوت حارس القناة"
git push -u origin main
```

### إذا كان Git محمي في Replit:

استخدم واجهة Replit:
1. اضغط على أيقونة الثلاث خطوط (☰) في الـ sidebar
2. اختر "Version Control" أو "Git"
3. اضغط "Connect to GitHub"
4. اختر repository موجود أو أنشئ جديد
5. املأ البيانات: `telegram-channel-guard-bot`

## بعد الربط:
- ✅ المشروع سيكون متاحاً على GitHub
- ✅ يمكن استنساخه واستخدامه من أي مكان
- ✅ نسخ احتياطية تلقائية
- ✅ إمكانية التعاون مع آخرين

## نصائح:
- تأكد من عدم رفع `TELEGRAM_BOT_TOKEN` (محمي في .gitignore)
- استخدم رسائل commit واضحة بالعربية أو الإنجليزية
- احرص على تحديث README عند إضافة ميزات جديدة