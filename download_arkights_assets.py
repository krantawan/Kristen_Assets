import os
import shutil
import subprocess
import glob
from pathlib import Path

def run_command(command, cwd=None, show_output=False):
    """รันคำสั่ง shell และแสดงผลลัพธ์"""
    try:
        if show_output:
            print(f"กำลังรัน: {command}")
        
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=not show_output, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"Error running command: {command}")
            if not show_output:
                print(f"Error output: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"Exception running command: {command}")
        print(f"Error: {e}")
        return False

def setup_partial_clone(repo_url, local_path, branch="cn", paths_to_include=None):
    """ใช้ partial clone + sparse checkout แบบเข้มงวด"""
    
    if paths_to_include is None:
        paths_to_include = ["assets/dyn/arts/characters/", "assets/dyn/arts/charportraits/"]
    
    if os.path.exists(local_path):
        print(f"Repository มีอยู่แล้วที่: {local_path}")
        print("กำลังอัปเดต...")
        
        # อัปเดตแบบระมัดระวัง
        if not run_command(f"git checkout {branch}", cwd=local_path):
            return False
        if not run_command("git pull origin " + branch + " --depth 1", cwd=local_path, show_output=True):
            return False
            
        print("อัปเดต repository สำเร็จ")
        return True
    
    print(f"กำลังใช้ partial clone จาก: {repo_url}")
    print(f"Branch: {branch}")
    print(f"โฟลเดอร์ที่จะดาวน์โหลด: {paths_to_include}")
    
    try:
        # วิธีใหม่: ใช้ partial clone แบบเข้มงวด
        
        # ขั้นตอนที่ 1: partial clone โดยไม่ checkout อะไรเลย
        print("1. กำลังสร้าง partial clone...")
        clone_cmd = f"git clone --filter=blob:none --no-checkout --single-branch --branch {branch} --depth 1 {repo_url} {local_path}"
        if not run_command(clone_cmd, show_output=True):
            return False
        
        # ขั้นตอนที่ 2: ตั้งค่า sparse checkout
        print("2. กำลังตั้งค่า sparse checkout...")
        if not run_command("git sparse-checkout init --cone", cwd=local_path):
            return False
        
        # ขั้นตอนที่ 3: กำหนดโฟลเดอร์ที่ต้องการ
        print("3. กำลังกำหนดโฟลเดอร์ที่ต้องการ...")
        sparse_paths = " ".join([f'"{path}"' for path in paths_to_include])
        if not run_command(f"git sparse-checkout set {sparse_paths}", cwd=local_path):
            return False
        
        # ขั้นตอนที่ 4: checkout เฉพาะไฟล์ที่ต้องการ
        print("4. กำลัง checkout ไฟล์ที่ต้องการ...")
        if not run_command("git checkout", cwd=local_path, show_output=True):
            return False
        
        print("Partial clone + sparse checkout สำเร็จ!")
        return True
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        # ลบโฟลเดอร์ที่อาจถูกสร้างไว้บางส่วน
        if os.path.exists(local_path):
            try:
                shutil.rmtree(local_path)
            except:
                pass
        return False

def should_skip_file(filename):
    """ตรวจสอบว่าควรข้ามไฟล์นี้หรือไม่ (ลงท้ายด้วย 'b.png')"""
    return filename.endswith('b.png')

def copy_character_images(source_dir, output_dir):
    """คัดลอกรูปภาพ character จากโฟลเดอร์ source ไป output"""
    
    # สร้างโฟลเดอร์ output หากยังไม่มี
    os.makedirs(output_dir, exist_ok=True)
    
    characters_path = os.path.join(source_dir, "assets", "dyn", "arts", "characters")
    
    if not os.path.exists(characters_path):
        print(f"ไม่พบโฟลเดอร์: {characters_path}")
        return
    
    print(f"กำลังสแกนโฟลเดอร์: {characters_path}")
    
    # หาโฟลเดอร์ character ทั้งหมด
    character_folders = [d for d in os.listdir(characters_path) 
                        if os.path.isdir(os.path.join(characters_path, d)) 
                        and d.startswith('char_')]
    
    if not character_folders:
        print("ไม่พบโฟลเดอร์ character")
        return
    
    print(f"พบ {len(character_folders)} character folders")
    
    total_copied = 0
    total_skipped = 0
    total_existing = 0
    
    for i, folder_name in enumerate(sorted(character_folders), 1):
        print(f"\n[{i}/{len(character_folders)}] กำลังประมวลผล: {folder_name}")
        
        folder_path = os.path.join(characters_path, folder_name)
        
        # หาไฟล์ .png ทั้งหมดในโฟลเดอร์
        png_files = glob.glob(os.path.join(folder_path, "*.png"))
        
        folder_copied = 0
        folder_skipped = 0
        folder_existing = 0
        
        for png_file in png_files:
            filename = os.path.basename(png_file)
            
            # ตรวจสอบว่าควรข้ามไฟล์นี้หรือไม่
            if should_skip_file(filename):
                print(f"  ข้าม: {filename} (ลงท้ายด้วย 'b.png')")
                folder_skipped += 1
                continue
            
            # ตรวจสอบว่าไฟล์มีอยู่แล้วหรือไม่
            dest_path = os.path.join(output_dir, filename)
            if os.path.exists(dest_path):
                print(f"  มีอยู่แล้ว: {filename}")
                folder_existing += 1
                continue
            
            # คัดลอกไฟล์
            try:
                shutil.copy2(png_file, dest_path)
                print(f"  คัดลอก: {filename}")
                folder_copied += 1
            except Exception as e:
                print(f"  ล้มเหลว: {filename} - {e}")
        
        total_copied += folder_copied
        total_skipped += folder_skipped
        total_existing += folder_existing
        
        if png_files:
            print(f"  โฟลเดอร์ {folder_name}: คัดลอก {folder_copied}, ข้าม {folder_skipped}, มีอยู่แล้ว {folder_existing}")
    
    print(f"\n=== สรุปผลการคัดลอก Characters ===")
    print(f"คัดลอกใหม่: {total_copied} ไฟล์")
    print(f"ข้ามไฟล์: {total_skipped} ไฟล์") 
    print(f"มีอยู่แล้ว: {total_existing} ไฟล์")
    print(f"บันทึกไฟล์ในโฟลเดอร์: {output_dir}")

def get_repo_size_info(repo_path):
    """แสดงขนาดของ repository"""
    if not os.path.exists(repo_path):
        return
    
    try:
        # คำนวณขนาดโฟลเดอร์
        total_size = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(repo_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        # แปลงขนาดเป็น MB
        size_mb = total_size / (1024 * 1024)
        
        print(f"ขนาด repository: {size_mb:.1f} MB ({file_count:,} ไฟล์)")
        
        # แสดงขนาดโฟลเดอร์เฉพาะ
        assets_path = os.path.join(repo_path, "assets")
        if os.path.exists(assets_path):
            assets_size = 0
            assets_files = 0
            for dirpath, dirnames, filenames in os.walk(assets_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        assets_size += os.path.getsize(file_path)
                        assets_files += 1
            
            assets_size_mb = assets_size / (1024 * 1024)
            print(f"ขนาดโฟลเดอร์ assets: {assets_size_mb:.1f} MB ({assets_files:,} ไฟล์)")
        
    except Exception as e:
        print(f"ไม่สามารถคำนวณขนาดได้: {e}")

def copy_character_portraits(source_dir, output_dir):
    """คัดลอกรูปภาพ character portraits จากโฟลเดอร์ source ไป output"""
    
    # สร้างโฟลเดอร์ output หากยังไม่มี
    os.makedirs(output_dir, exist_ok=True)
    
    portraits_path = os.path.join(source_dir, "assets", "dyn", "arts", "charportraits")
    
    if not os.path.exists(portraits_path):
        print(f"ไม่พบโฟลเดอร์: {portraits_path}")
        return
    
    print(f"กำลังสแกนโฟลเดอร์: {portraits_path}")
    
    # หาไฟล์ .png ทั้งหมดในโฟลเดอร์ portraits
    png_files = glob.glob(os.path.join(portraits_path, "*.png"))
    
    if not png_files:
        print("ไม่พบไฟล์ portraits")
        return
    
    print(f"พบ {len(png_files)} portrait files")
    
    copied = 0
    skipped = 0
    existing = 0
    
    for png_file in png_files:
        filename = os.path.basename(png_file)
        
        # ตรวจสอบว่าควรข้ามไฟล์นี้หรือไม่
        if should_skip_file(filename):
            print(f"  ข้าม: {filename} (ลงท้ายด้วย 'b.png')")
            skipped += 1
            continue
        
        # ตรวจสอบว่าไฟล์มีอยู่แล้วหรือไม่
        dest_path = os.path.join(output_dir, filename)
        if os.path.exists(dest_path):
            print(f"  มีอยู่แล้ว: {filename}")
            existing += 1
            continue
        
        # คัดลอกไฟล์
        try:
            shutil.copy2(png_file, dest_path)
            print(f"  คัดลอก: {filename}")
            copied += 1
        except Exception as e:
            print(f"  ล้มเหลว: {filename} - {e}")
    
    print(f"\n=== สรุปผลการคัดลอก Portraits ===")
    print(f"คัดลอกใหม่: {copied} ไฟล์")
    print(f"ข้ามไฟล์: {skipped} ไฟล์") 
    print(f"มีอยู่แล้ว: {existing} ไฟล์")
    print(f"บันทึกไฟล์ในโฟลเดอร์: {output_dir}")

def copy_skills_images(source_dir, output_dir):
    """คัดลอกรูปภาพ skills จากโฟลเดอร์ source ไป output"""
    
    # สร้างโฟลเดอร์ output หากยังไม่มี
    os.makedirs(output_dir, exist_ok=True)
    
    skills_path = os.path.join(source_dir, "assets", "dyn", "arts", "skills")
    
    if not os.path.exists(skills_path):
        print(f"ไม่พบโฟลเดอร์: {skills_path}")
        return
    
    print(f"กำลังสแกนโฟลเดอร์: {skills_path}")
    
    # หาไฟล์ .png ทั้งหมดในโฟลเดอร์ skills
    png_files = glob.glob(os.path.join(skills_path, "*.png"))
    
    if not png_files:
        print("ไม่พบไฟล์ skills")
        return
    
    print(f"พบ {len(png_files)} skill files")
    
    copied = 0
    skipped = 0
    existing = 0
    
    for png_file in png_files:
        filename = os.path.basename(png_file)
        
        # ตรวจสอบว่าควรข้ามไฟล์นี้หรือไม่
        if should_skip_file(filename):
            print(f"  ข้าม: {filename} (ลงท้ายด้วย 'b.png')")
            skipped += 1
            continue
        
        # ตรวจสอบว่าไฟล์มีอยู่แล้วหรือไม่
        dest_path = os.path.join(output_dir, filename)
        if os.path.exists(dest_path):
            print(f"  มีอยู่แล้ว: {filename}")
            existing += 1
            continue
        
        # คัดลอกไฟล์
        try:
            shutil.copy2(png_file, dest_path)
            print(f"  คัดลอก: {filename}")
            copied += 1
        except Exception as e:
            print(f"  ล้มเหลว: {filename} - {e}")
    
    print(f"\n=== สรุปผลการคัดลอก Skills ===")
    print(f"คัดลอกใหม่: {copied} ไฟล์")
    print(f"ข้ามไฟล์: {skipped} ไฟล์") 
    print(f"มีอยู่แล้ว: {existing} ไฟล์")
    print(f"บันทึกไฟล์ในโฟลเดอร์: {output_dir}")
    """แสดงขนาดของ repository"""
    if not os.path.exists(repo_path):
        return
    
    try:
        # คำนวณขนาดโฟลเดอร์
        total_size = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(repo_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        # แปลงขนาดเป็น MB
        size_mb = total_size / (1024 * 1024)
        
        print(f"ขนาด repository: {size_mb:.1f} MB ({file_count:,} ไฟล์)")
        
        # แสดงขนาดโฟลเดอร์เฉพาะ
        assets_path = os.path.join(repo_path, "assets")
        if os.path.exists(assets_path):
            assets_size = 0
            assets_files = 0
            for dirpath, dirnames, filenames in os.walk(assets_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        assets_size += os.path.getsize(file_path)
                        assets_files += 1
            
            assets_size_mb = assets_size / (1024 * 1024)
            print(f"ขนาดโฟลเดอร์ assets: {assets_size_mb:.1f} MB ({assets_files:,} ไฟล์)")
        
    except Exception as e:
        print(f"ไม่สามารถคำนวณขนาดได้: {e}")

def main():
    # ตั้งค่า
    REPO_URL = "https://github.com/ArknightsAssets/ArknightsAssets2.git"
    LOCAL_REPO = "./arknights_partial_repo"
    OPERATORS_DIR = "./Operators"
    PORTRAITS_DIR = "./Portraits"
    SKILLS_DIR = "./Skills"
    BRANCH = "cn"
    SPARSE_PATHS = [
        "assets/dyn/arts/characters",
        "assets/dyn/arts/charportraits",
        "assets/dyn/arts/skills"
    ]
    
    print("=== Arknights Assets Partial Clone + Sparse Checkout Script ===")
    print(f"Repository: {REPO_URL}")
    print(f"Branch: {BRANCH}")
    print(f"Local Repository: {LOCAL_REPO}")
    print(f"Sparse Paths:")
    for path in SPARSE_PATHS:
        print(f"  - {path}")
    print(f"Output Directories:")
    print(f"  - Characters: {OPERATORS_DIR}")
    print(f"  - Portraits: {PORTRAITS_DIR}")
    print(f"  - Skills: {SKILLS_DIR}")
    print(f"Filter: ข้ามไฟล์ที่ลงท้ายด้วย 'b.png'")
    print("\n🎯 ใช้ partial clone + sparse checkout เพื่อดาวน์โหลดเฉพาะที่ต้องการ!")
    
    try:
        # ขั้นตอนที่ 1: ตั้งค่า partial clone
        print(f"\n=== ขั้นตอนที่ 1: Partial Clone + Sparse Checkout ===")
        if not setup_partial_clone(REPO_URL, LOCAL_REPO, BRANCH, SPARSE_PATHS):
            print("ล้มเหลวในการตั้งค่า partial clone")
            return
        
        # แสดงขนาด repository
        get_repo_size_info(LOCAL_REPO)
        
        # ขั้นตอนที่ 2: คัดลอกไฟล์ Characters
        print(f"\n=== ขั้นตอนที่ 2: คัดลอกไฟล์ Characters ===")
        copy_character_images(LOCAL_REPO, OPERATORS_DIR)
        
        # ขั้นตอนที่ 3: คัดลอกไฟล์ Portraits
        print(f"\n=== ขั้นตอนที่ 3: คัดลอกไฟล์ Portraits ===")
        copy_character_portraits(LOCAL_REPO, PORTRAITS_DIR)
        
        # ขั้นตอนที่ 4: คัดลอกไฟล์ Skills
        print(f"\n=== ขั้นตอนที่ 4: คัดลอกไฟล์ Skills ===")
        copy_skills_images(LOCAL_REPO, SKILLS_DIR)
        
        print(f"\n=== เสร็จสิ้น ===")
        print(f"Repository ถูกเก็บไว้ที่: {LOCAL_REPO}")
        print(f"Characters ถูกบันทึกที่: {OPERATORS_DIR}")
        print(f"Portraits ถูกบันทึกที่: {PORTRAITS_DIR}")
        print(f"Skills ถูกบันทึกที่: {SKILLS_DIR}")
        print("สามารถรัน script อีกครั้งเพื่ออัปเดตได้เร็วมาก")
        
    except KeyboardInterrupt:
        print("\n\nการทำงานถูกยกเลิกโดยผู้ใช้")
        if os.path.exists(LOCAL_REPO):
            try:
                shutil.rmtree(LOCAL_REPO)
                print(f"ลบโฟลเดอร์ชั่วคราว: {LOCAL_REPO}")
            except:
                pass
    except Exception as e:
        print(f"\nเกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()