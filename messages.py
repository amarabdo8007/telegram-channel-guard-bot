"""
Messages Module
Contains all bot messages with Arabic language support
"""

from datetime import datetime

class Messages:
    def __init__(self):
        self.messages = {
            'ar': {
                'welcome': '''🛡️ مرحباً بك في بوت حماية القناة

هذا البوت يقوم بمراقبة المشرفين ويحميهم من إساءة استخدام صلاحياتهم.

الأوامر المتاحة:
/help - عرض المساعدة
/status - حالة البوت
/logs - عرض السجلات
/config - إعدادات البوت

⚠️ تأكد من منح البوت صلاحيات الإدارة اللازمة''',
                
                'help': '''📋 أوامر البوت:

الأوامر العامة:
/start - بدء استخدام البوت
/status - عرض حالة البوت والإحصائيات
/logs - عرض آخر الأحداث المسجلة
/config - عرض إعدادات البوت

أوامر إدارة المشرفين (للمالك فقط):
/add_admin [رقم المشرف] - إضافة مشرف للمراقبة
/remove_admin [رقم المشرف] - إزالة مشرف من المراقبة
/list_admins - عرض قائمة المشرفين المراقبين

🔧 وظائف البوت:
• مراقبة أنشطة المشرفين المحددين
• إزالة المشرفين الذين يحظرون الأعضاء العاديين تلقائياً
• تسجيل جميع الأحداث والتصرفات
• إشعارات فورية عند حدوث انتهاكات

⚡ البوت يعمل تلقائياً في القنوات المحددة''',
                
                'status_active': '''✅ حالة البوت: نشط

📊 الإحصائيات:
• القنوات المحمية: {protected_channels}
• المشرفين المراقبين: {monitored_admins}
• الحظر التلقائي: {'مفعل' if '{auto_ban_enabled}' else 'معطل'}

🕐 آخر تحديث: {timestamp}''',
                
                'unauthorized': '❌ غير مسموح لك باستخدام هذا الأمر',
                
                'admin_banned': '''⚠️ تم إزالة مشرف من القناة

👤 المشرف المحظور: @{admin_username}
📝 السبب: حظر العضو @{banned_user}
🕐 التوقيت: {timestamp}

تم حظر المشرف تلقائياً لإساءة استخدام الصلاحيات''',
                
                'logs_header': '📋 آخر الأحداث المسجلة:\n\n',
                
                'config_display': '''⚙️ إعدادات البوت:

🌐 اللغة: العربية
🔄 الحظر التلقائي: {auto_ban_status}
📢 الإشعارات: {notifications_status}
📊 حد المكالمات: {api_limit}/دقيقة

📁 القنوات المحمية: {protected_count}
👥 المشرفين المراقبين: {monitored_count}''',
                
                'no_logs': 'لا توجد سجلات متاحة',
                
                'action_member_banned': 'تم حظر عضو',
                'action_admin_banned': 'تم حظر مشرف',
                'action_start_command': 'تم تشغيل البوت',
                
                'only_creator_allowed': '❌ هذا الأمر متاح فقط لمالك القناة',
                'add_admin_usage': '📝 الاستخدام: /add_admin [رقم_المشرف]\nمثال: /add_admin 123456789',
                'remove_admin_usage': '📝 الاستخدام: /remove_admin [رقم_المشرف]\nمثال: /remove_admin 123456789',
                'invalid_user_id': '❌ رقم المستخدم غير صحيح',
                'admin_added_success': '✅ تم إضافة المشرف {admin_id} إلى قائمة المراقبة',
                'admin_add_failed': '❌ فشل في إضافة المشرف (تأكد من أنه مشرف فعلاً)',
                'admin_removed_success': '✅ تم إزالة المشرف {admin_id} من قائمة المراقبة',
                'admin_not_monitored': '❌ هذا المشرف غير موجود في قائمة المراقبة',
                'no_monitored_admins': '📝 لا يوجد مشرفين مراقبين حالياً',
                
                'monitored_admins_header': '👥 المشرفين المراقبين:\n\n'
            }
        }
    
    def get_message(self, message_key, language='ar', **kwargs):
        """Get a message in the specified language"""
        try:
            message = self.messages[language][message_key]
            if kwargs:
                return message.format(**kwargs)
            return message
        except KeyError:
            return f"Message not found: {message_key}"
    
    def get_status_message(self, status_info, language='ar'):
        """Generate status message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.get_message('status_active', language).format(
            protected_channels=status_info['protected_channels'],
            monitored_admins=status_info['monitored_admins'],
            auto_ban_enabled='مفعل' if status_info['auto_ban_enabled'] else 'معطل',
            timestamp=timestamp
        )
    
    def get_admin_banned_message(self, admin_username, banned_username, language='ar'):
        """Generate admin banned notification message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.get_message('admin_banned', language).format(
            admin_username=admin_username,
            banned_user=banned_username,
            timestamp=timestamp
        )
    
    def get_logs_message(self, logs, language='ar'):
        """Generate logs display message"""
        if not logs:
            return self.get_message('no_logs', language)
        
        message = self.get_message('logs_header', language)
        
        for log in logs[-10:]:  # Show last 10 logs
            timestamp = log.get('timestamp', '')
            action = log.get('action', '')
            user_id = log.get('user_id', '')
            admin_id = log.get('admin_id', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%m-%d %H:%M')
            except:
                formatted_time = timestamp[:16]
            
            # Translate action
            action_text = self._translate_action(action, language)
            
            if admin_id and user_id != admin_id:
                message += f"🕐 {formatted_time} - {action_text} (Admin: {admin_id}, User: {user_id})\n"
            else:
                message += f"🕐 {formatted_time} - {action_text} (User: {user_id})\n"
        
        return message
    
    def get_config_message(self, config, language='ar'):
        """Generate configuration display message"""
        auto_ban_status = 'مفعل' if config['channel_settings']['auto_ban_enabled'] else 'معطل'
        notifications_status = 'مفعل' if config['channel_settings'].get('notification_enabled', True) else 'معطل'
        api_limit = config['rate_limits'].get('api_calls_per_minute', 30)
        protected_count = len(config['channel_settings']['protected_channels'])
        monitored_count = len(config['channel_settings']['monitored_admins'])
        
        return self.get_message('config_display', language).format(
            auto_ban_status=auto_ban_status,
            notifications_status=notifications_status,
            api_limit=api_limit,
            protected_count=protected_count,
            monitored_count=monitored_count
        )
    
    def _translate_action(self, action, language='ar'):
        """Translate action names to Arabic"""
        action_translations = {
            'member_banned': 'تم حظر عضو',
            'admin_banned_for_abuse': 'تم حظر مشرف لإساءة الاستخدام',
            'start_command': 'تم تشغيل البوت',
            'status_command': 'تم طلب الحالة',
            'logs_command': 'تم طلب السجلات',
            'config_command': 'تم طلب الإعدادات'
        }
        
        return action_translations.get(action, action)
    
    def get_monitored_admins_message(self, admin_details, language='ar'):
        """Generate message showing monitored admins"""
        message = self.get_message('monitored_admins_header', language)
        
        for i, admin in enumerate(admin_details, 1):
            admin_id = admin.get('id', 'N/A')
            username = admin.get('username', '')
            first_name = admin.get('first_name', 'Unknown')
            status = admin.get('status', 'unknown')
            
            status_text = {
                'administrator': 'مشرف',
                'creator': 'منشئ القناة',
                'unknown': 'غير معروف'
            }.get(status, status)
            
            username_text = f"@{username}" if username else "لا يوجد"
            
            message += f"{i}. {first_name} ({admin_id})\n"
            message += f"   🔗 المعرف: {username_text}\n"
            message += f"   👤 الحالة: {status_text}\n\n"
        
        return message
