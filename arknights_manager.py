import os
import sys
import shutil
import subprocess
from datetime import datetime

def run_script(script_name, description):
    """รัน script และแสดงผลลัพธ์"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"กำลังรัน: {script_name}")
    print(f"เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # รัน script และแสดงผลแบบ real-time
        result = subprocess.run([sys.executable, script_name], 
                              check=True, 
                              text=True)
        
        print(f"\n{'='*60}")
        print(f"✅ {description} เสร็จสิ้น")
        print(f"{'='*60}\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n{'='*60}")
        print(f"❌ {description} ล้มเหลว")
        print(f"Error code: {e.returncode}")
        print(f"{'='*60}\n")
        return False
    except FileNotFoundError:
        print(f"\n❌ ไม่พบไฟล์: {script_name}")
        print("กรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ Libs/\n")
        return False
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}\n")
        return False

def check_required_files():
    """ตรวจสอบว่ามีไฟล์ที่จำเป็นหรือไม่"""
    required_files = [
        "Libs/download_arknights_assets.py",
        "Libs/copy_repo_to_model.py", 
        "Libs/complete_models_processor.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(os.path.basename(file))
    
    if missing_files:
        print("❌ ไม่พบไฟล์ที่จำเป็นในโฟลเดอร์ Libs:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nกรุณาตรวจสอบว่าไฟล์ทั้งหมดอยู่ในโฟลเดอร์ Libs/")
        print("โครงสร้างที่ถูกต้อง:")
        print("  Libs/")
        print("    ├── download_arknights_assets.py")
        print("    ├── copy_repo_to_model.py")
        print("    └── complete_models_processor.py")
        return False
    
    return True

def show_directory_status():
    """แสดงสถานะโฟลเดอร์ต่างๆ"""
    directories = {
        "./arknights_partial_repo": "Repository Cache",
        "./Operators": "Character Images",
        "./Portraits": "Character Portraits", 
        "./Skills": "Skill Images",
        "./Bskills": "Building Skill Images",
        "./Models": "Character Models",
        "./Spine/Texture2D": "Texture Source",
        "./Libs": "Script Files"
    }
    
    print("\n📁 สถานะโฟลเดอร์:")
    for dir_path, description in directories.items():
        if os.path.exists(dir_path):
            try:
                file_count = len([f for f in os.listdir(dir_path) 
                                if os.path.isfile(os.path.join(dir_path, f))])
                folder_count = len([f for f in os.listdir(dir_path) 
                                  if os.path.isdir(os.path.join(dir_path, f))])
                print(f"   ✅ {description}: {folder_count} โฟลเดอร์, {file_count} ไฟล์")
            except:
                print(f"   ✅ {description}: มีอยู่")
        else:
            print(f"   ❌ {description}: ไม่มี")

def clear_cache():
    """ลบ repository cache"""
    cache_dir = "./arknights_partial_repo"
    
    if not os.path.exists(cache_dir):
        print("💡 ไม่มี cache ที่ต้องลบ")
        return
    
    # คำนวณขนาด cache
    total_size = 0
    file_count = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(cache_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        print(f"📦 Repository Cache ขนาด: {size_mb:.1f} MB ({file_count:,} ไฟล์)")
        print(f"📍 ตำแหน่ง: {cache_dir}")
        
        confirm = input("\n❓ ต้องการลบ cache หรือไม่? (y/N): ").strip().lower()
        
        if confirm == 'y':
            print("🗑️ กำลังลบ cache...")
            
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ ลบ cache สำเร็จ! ประหยัดพื้นที่ {size_mb:.1f} MB")
                print("💡 การดาวน์โหลดครั้งต่อไปจะใช้เวลานานกว่าปกติ")
            except Exception as e:
                print(f"❌ ไม่สามารถลบ cache ได้: {e}")
        else:
            print("ยกเลิกการลบ cache")
            
    except Exception as e:
        print(f"❌ ไม่สามารถคำนวณขนาด cache ได้: {e}")

def auto_mode():
    """โหมดอัตโนมัติ - ทำทุกขั้นตอน"""
    print("🤖 โหมดอัตโนมัติ")
    print("จะทำการดาวน์โหลด คัดลอก และประมวลผลโมเดลอัตโนมัติ")
    
    confirm = input("\nต้องการดำเนินการต่อหรือไม่? (y/N): ").strip().lower()
    if confirm != 'y':
        print("ยกเลิกการทำงาน")
        return
    
    start_time = datetime.now()
    
    # ขั้นตอนที่ 1: ดาวน์โหลดและคัดลอก
    step1_success = run_script("Libs/download_arknights_assets.py", 
                              "ดาวน์โหลดและคัดลอกไฟล์จาก GitHub")
    
    if not step1_success:
        print("❌ ขั้นตอนที่ 1 ล้มเหลว หยุดการทำงาน")
        return
    
    # ขั้นตอนที่ 2: ประมวลผลโมเดล
    step2_success = run_script("Libs/complete_models_processor.py",
                              "ประมวลผลโมเดล (Rename, Fix Atlas, Resize, Copy Texture)")
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n🎉 โหมดอัตโนมัติเสร็จสิ้น!")
    print(f"⏱️ ใช้เวลาทั้งหมด: {duration}")
    print(f"✅ ขั้นตอนที่ 1: {'สำเร็จ' if step1_success else 'ล้มเหลว'}")
    print(f"✅ ขั้นตอนที่ 2: {'สำเร็จ' if step2_success else 'ล้มเหลว'}")
    
    if step1_success and step2_success:
        print("\n🎊 ประมวลผลเสร็จสมบูรณ์! ไฟล์พร้อมใช้งาน")
    else:
        print("\n⚠️ มีขั้นตอนที่ล้มเหลว กรุณาตรวจสอบ")

def manual_mode():
    """โหมดแมนนวล - เลือกขั้นตอนเอง"""
    while True:
        print("\n" + "="*60)
        print("🔧 โหมดแมนนวล")
        print("="*60)
        print("1. ดาวน์โหลดและคัดลอกไฟล์จาก GitHub")
        print("2. คัดลอกโมเดลจาก Repository Cache ไป Models") 
        print("3. ประมวลผลโมเดล (Rename, Fix Atlas, Resize, Copy Texture)")
        print("4. แสดงสถานะโฟลเดอร์")
        print("5. 🗑️ ลบ Repository Cache")
        print("0. กลับเมนูหลัก")
        print("="*60)
        
        choice = input("เลือกขั้นตอน (0-5): ").strip()
        
        if choice == "1":
            run_script("Libs/download_arknights_assets.py", 
                      "ดาวน์โหลดและคัดลอกไฟล์จาก GitHub")
        
        elif choice == "2":
            run_script("Libs/copy_repo_to_model.py",
                      "คัดลอกโมเดลจาก Repository Cache")
        
        elif choice == "3":
            run_script("Libs/complete_models_processor.py",
                      "ประมวลผลโมเดล")
        
        elif choice == "4":
            show_directory_status()
        
        elif choice == "5":
            clear_cache()
        
        elif choice == "0":
            break
        
        else:
            print("❌ ตัวเลือกไม่ถูกต้อง กรุณาเลือก 0-5")
        
        input("\nกด Enter เพื่อดำเนินการต่อ...")

def show_help():
    """แสดงคำแนะนำการใช้งาน"""
    print("\n" + "="*60)
    print("📖 คำแนะนำการใช้งาน")
    print("="*60)
    print("""
🤖 โหมดอัตโนมัติ (Auto):
   - ดาวน์โหลดไฟล์จาก GitHub อัตโนมัติ
   - คัดลอกไฟล์ไปยังโฟลเดอร์ที่กำหนด
   - ประมวลผลโมเดลครบทุกขั้นตอน
   - เหมาะสำหรับผู้ใช้ใหม่หรือต้องการความสะดวก

🔧 โหมดแมนนวล (Manual):
   1. ดาวน์โหลดและคัดลอก - ดึงไฟล์จาก GitHub
   2. คัดลอกโมเดล - คัดลอกเฉพาะโมเดลจาก cache
   3. ประมวลผลโมเดล - แก้ไขและปรับปรุงโมเดล
   4. แสดงสถานะ - ดูข้อมูลโฟลเดอร์ต่างๆ
   5. ลบ cache - ประหยัดพื้นที่ดิสก์

📁 โฟลเดอร์ที่จะถูกสร้าง:
   - ./Operators - รูปตัวละคร
   - ./Portraits - รูป Portrait ตัวละคร  
   - ./Skills - รูปสกิล
   - ./Bskills - รูปสกิล Building
   - ./Models - โมเดล 3D ตัวละคร
   - ./arknights_partial_repo - Cache ของ Repository

💡 เคล็ดลับ:
   - ใช้โหมดอัตโนมัติครั้งแรก
   - ใช้โหมดแมนนวลเมื่อต้องการอัปเดตเฉพาะส่วน
   - ตรวจสอบสถานะโฟลเดอร์เป็นประจำ
   - เก็บโฟลเดอร์ ./Spine/Texture2D ไว้สำหรับ texture source
   - ลบ cache เพื่อประหยัดพื้นที่หากไม่ต้องการอัปเดตบ่อย
""")

def main():
    """เมนูหลัก"""
    print("="*60)
    print("🎮 Arknights Assets Manager")
    print("="*60)
    print("จัดการการดาวน์โหลดและประมวลผล Arknights Assets")
    print(f"เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ตรวจสอบไฟล์ที่จำเป็น
    if not check_required_files():
        input("\nกด Enter เพื่อออก...")
        return
    
    while True:
        print("\n" + "="*60)
        print("📋 เมนูหลัก")
        print("="*60)
        print("1. 🤖 Auto - ทำทุกขั้นตอนอัตโนมัติ")
        print("2. 🔧 Manual - เลือกขั้นตอนเอง") 
        print("3. 📁 แสดงสถานะโฟลเดอร์")
        print("4. 🗑️ ลบ Repository Cache")
        print("5. 📖 คำแนะนำการใช้งาน")
        print("0. 🚪 ออกจากโปรแกรม")
        print("="*60)
        
        choice = input("เลือกตัวเลือก (0-5): ").strip()
        
        if choice == "1":
            auto_mode()
        
        elif choice == "2":
            manual_mode()
        
        elif choice == "3":
            show_directory_status()
            input("\nกด Enter เพื่อดำเนินการต่อ...")
        
        elif choice == "4":
            clear_cache()
            input("\nกด Enter เพื่อดำเนินการต่อ...")
        
        elif choice == "5":
            show_help()
            input("\nกด Enter เพื่อกลับเมนูหลัก...")
        
        elif choice == "0":
            print("\n👋 ขอบคุณที่ใช้งาน Arknights Assets Manager!")
            break
        
        else:
            print("❌ ตัวเลือกไม่ถูกต้อง กรุณาเลือก 0-5")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 การทำงานถูกยกเลิกโดยผู้ใช้")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        input("กด Enter เพื่อออก...")