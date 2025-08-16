# test_database.py
# سكريبت بسيط لاختبار إنشاء قاعدة بيانات SQLite

import sqlite3
import os

DATABASE_NAME = "test_predictions.db"

print("=== اختبار إنشاء قاعدة بيانات SQLite ===")
print(f"المجلد الحالي: {os.getcwd()}")
print(f"محاولة إنشاء قاعدة بيانات: {DATABASE_NAME}")

try:
    # محاولة إنشاء قاعدة البيانات
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    print("✅ تم الاتصال بقاعدة البيانات بنجاح")
    
    # إنشاء جدول بسيط
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        value INTEGER
    )
    """)
    
    print("✅ تم إنشاء الجدول بنجاح")
    
    # إدراج بيانات تجريبية
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 123))
    conn.commit()
    
    print("✅ تم إدراج البيانات بنجاح")
    
    # قراءة البيانات للتأكد
    cursor.execute("SELECT * FROM test_table")
    rows = cursor.fetchall()
    print(f"✅ البيانات المحفوظة: {rows}")
    
    conn.close()
    print("✅ تم إغلاق الاتصال")
    
    # التحقق من وجود الملف
    if os.path.exists(DATABASE_NAME):
        file_size = os.path.getsize(DATABASE_NAME)
        print(f"✅ ملف قاعدة البيانات موجود: {DATABASE_NAME} (الحجم: {file_size} بايت)")
    else:
        print(f"❌ ملف قاعدة البيانات غير موجود: {DATABASE_NAME}")
        
except sqlite3.Error as e:
    print(f"❌ خطأ في SQLite: {e}")
except Exception as e:
    print(f"❌ خطأ عام: {e}")

print("\n=== انتهى الاختبار ===")

