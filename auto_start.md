# طرق تشغيل البوت تلقائياً بدون Run

## المشكلة
Run button قد يتوقف أو يعيد التشغيل تلقائياً.

## الحلول المتاحة:

### 1. ⭐ التشغيل من Terminal (الأفضل)
```bash
./startup.sh
```
أو
```bash
python3 run_bot.py
```

### 2. التشغيل مع Keep-Alive
```bash
python3 keep_alive.py
```
هذا سيعيد تشغيل البوت تلقائياً إذا توقف.

### 3. التشغيل في الخلفية
```bash
nohup python3 run_bot.py > bot.log 2>&1 &
```

### 4. التحقق من حالة البوت
```bash
ps aux | grep run_bot.py
```

### 5. إيقاف البوت
```bash
pkill -f "python3 run_bot.py"
```

## مميزات كل طريقة:

### startup.sh
✅ مراقبة تلقائية  
✅ رسائل واضحة  
✅ فحص التوكن  

### run_bot.py
✅ تشغيل مباشر  
✅ سريع وبسيط  

### keep_alive.py
✅ إعادة تشغيل تلقائية  
✅ health check server  

## نصائح:
- استخدم terminal منفصل للبوت
- اتركه يعمل في الخلفية
- راقب اللوجات للتأكد من العمل السليم
- البوت يعمل حتى لو أغلقت Replit (على السيرفر)