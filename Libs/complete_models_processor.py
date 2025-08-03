import os
import json
import shutil
from PIL import Image
from datetime import datetime

def rename_in_directory(base_dir):
    """ขั้นตอนที่ 1: เปลี่ยนชื่อไฟล์และโฟลเดอร์ แทนที่ # ด้วย _ และเปลี่ยนเป็นตัวเล็ก"""
    print("=== ขั้นตอนที่ 1: Rename Files and Folders ===")
    
    renamed_files = 0
    renamed_folders = 0
    
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # เปลี่ยนชื่อไฟล์ก่อน
        for name in files:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.join(root, name)
                new_name = name.replace("#", "_").lower()
                new_path = os.path.join(root, new_name)
                print(f"  เปลี่ยนชื่อไฟล์: {name} -> {new_name}")
                os.rename(old_path, new_path)
                renamed_files += 1

        # เปลี่ยนชื่อโฟลเดอร์
        for name in dirs:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.join(root, name)
                new_name = name.replace("#", "_").lower()
                new_path = os.path.join(root, new_name)
                print(f"  เปลี่ยนชื่อโฟลเดอร์: {name} -> {new_name}")
                os.rename(old_path, new_path)
                renamed_folders += 1
    
    print(f"เปลี่ยนชื่อไฟล์: {renamed_files} ไฟล์")
    print(f"เปลี่ยนชื่อโฟลเดอร์: {renamed_folders} โฟลเดอร์\n")

def fix_atlas_filenames(base_dir):
    """ขั้นตอนที่ 2: แก้ไขไฟล์ .atlas เปลี่ยน # เป็น _ และเป็นตัวเล็ก"""
    print("=== ขั้นตอนที่ 2: Fix Atlas Files ===")
    
    processed_files = 0
    changed_files = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".atlas"):
                path = os.path.join(root, file)
                print(f"  ประมวลผล: {file}")
                new_lines = []
                changed = False
                line_changes = 0

                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        if ".png" in line:
                            # แปลงเป็นตัวเล็ก
                            lower_line = line.lower()
                            # แก้ # เป็น _
                            fixed_line = lower_line.replace("#", "_")
                            new_lines.append(fixed_line)
                            if fixed_line != line:
                                changed = True
                                line_changes += 1
                                print(f"    แก้ไข: {line.strip()} -> {fixed_line.strip()}")
                        else:
                            # บรรทัดอื่นไม่เปลี่ยน
                            new_lines.append(line)

                if changed:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    print(f"    อัปเดตไฟล์ ({line_changes} บรรทัด)")
                    changed_files += 1
                else:
                    print(f"    ไม่ต้องแก้ไข")
                
                processed_files += 1
    
    print(f"ประมวลผลไฟล์ .atlas: {processed_files} ไฟล์")
    print(f"แก้ไขแล้ว: {changed_files} ไฟล์\n")

def parse_atlas_size(atlas_path):
    """อ่านขนาดจากไฟล์ .atlas"""
    try:
        with open(atlas_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().endswith('.png') and i+1 < len(lines):
                if lines[i+1].strip().startswith("size:"):
                    size_line = lines[i+1].strip()
                    size_str = size_line.replace("size:", "").strip()
                    width, height = map(int, size_str.split(","))
                    return width, height
        return None, None
    except Exception as e:
        print(f"    ❌ ไม่สามารถอ่าน atlas: {e}")
        return None, None

def resize_images_and_track_missing(base_dir):
    """ขั้นตอนที่ 3: ปรับขนาดรูปภาพและติดตามไฟล์ที่ไม่พบ"""
    print("=== ขั้นตอนที่ 3: Resize Images and Track Missing Files ===")
    
    missing_files = []
    processed_folders = 0
    resized_images = 0
    atlas_without_size = []
    
    for root, dirs, files in os.walk(base_dir):
        atlas_files = [f for f in files if f.endswith(".atlas")]
        
        if atlas_files:
            processed_folders += 1
            print(f"  ประมวลผลโฟลเดอร์: {os.path.relpath(root, base_dir)}")
            
            for atlas_file in atlas_files:
                base_name = atlas_file.replace(".atlas", "")
                atlas_path = os.path.join(root, atlas_file)
                png_path = os.path.join(root, base_name + ".png")
                
                print(f"    ตรวจสอบ: {base_name}")
                
                # ตรวจสอบว่ามีไฟล์ PNG หรือไม่
                if not os.path.exists(png_path):
                    print(f"    ❌ ไม่พบ PNG: {base_name}.png")
                    missing_files.append({
                        "folder": os.path.relpath(root, base_dir),
                        "atlas_file": atlas_file,
                        "missing_png": base_name + ".png",
                        "atlas_path": os.path.relpath(atlas_path, base_dir),
                        "expected_png_path": os.path.relpath(png_path, base_dir)
                    })
                    continue

                # อ่านขนาดจาก atlas
                atlas_w, atlas_h = parse_atlas_size(atlas_path)
                if not atlas_w or not atlas_h:
                    print(f"    ⚠️ ไม่สามารถอ่านขนาดจาก atlas: {atlas_file}")
                    atlas_without_size.append({
                        "folder": os.path.relpath(root, base_dir),
                        "atlas_file": atlas_file,
                        "atlas_path": os.path.relpath(atlas_path, base_dir)
                    })
                    continue

                # ตรวจสอบและปรับขนาดรูปภาพ
                try:
                    with Image.open(png_path) as img:
                        img_w, img_h = img.size
                        if img_w != atlas_w or img_h != atlas_h:
                            print(f"    🔧 ปรับขนาด: {img_w}x{img_h} -> {atlas_w}x{atlas_h}")
                            resized = img.resize((atlas_w, atlas_h), Image.LANCZOS)
                            resized.save(png_path)
                            resized_images += 1
                        else:
                            print(f"    ✅ ขนาดถูกต้องแล้ว: {img_w}x{img_h}")
                except Exception as e:
                    print(f"    ❌ ไม่สามารถประมวลผลรูปภาพ: {e}")
    
    # สร้างรายงาน
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "processed_folders": processed_folders,
            "resized_images": resized_images,
            "missing_png_files": len(missing_files),
            "atlas_without_size": len(atlas_without_size)
        },
        "missing_png_files": missing_files,
        "atlas_without_size": atlas_without_size
    }
    
    # บันทึกรายงานเป็น JSON
    report_path = os.path.join(base_dir, "missing_files_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"ประมวลผลโฟลเดอร์: {processed_folders} โฟลเดอร์")
    print(f"ปรับขนาดรูปภาพ: {resized_images} รูป")
    print(f"ไฟล์ PNG ที่ไม่พบ: {len(missing_files)} ไฟล์")
    print(f"Atlas ที่อ่านขนาดไม่ได้: {len(atlas_without_size)} ไฟล์")
    print(f"รายงานถูกบันทึกที่: {report_path}\n")
    
    return report

def copy_missing_textures(models_dir, texture_source_dir, missing_report):
    """ขั้นตอนที่ 4: คัดลอกไฟล์ texture ที่ไม่พบ พร้อมเปลี่ยนชื่อ"""
    print("=== ขั้นตอนที่ 4: Copy Missing Textures ===")
    
    if not os.path.exists(texture_source_dir):
        print(f"❌ ไม่พบโฟลเดอร์ texture: {texture_source_dir}")
        print("ข้ามขั้นตอนการคัดลอก texture\n")
        return None
    
    missing_files = missing_report.get('missing_png_files', [])
    if not missing_files:
        print("✅ ไม่มีไฟล์ที่ไม่พบ")
        print("ข้ามขั้นตอนการคัดลอก texture\n")
        return None
    
    print(f"🔍 พบไฟล์ที่ไม่พบ: {len(missing_files)} ไฟล์")
    print(f"กำลังค้นหาใน: {texture_source_dir}")
    
    # สร้างรายการไฟล์ใน texture source
    texture_files = {}
    for file in os.listdir(texture_source_dir):
        if file.endswith('.png'):
            # เก็บทั้งชื่อเดิมและชื่อที่แปลงแล้ว
            original_name = file
            converted_name = file.replace('#', '_').lower()
            texture_files[converted_name] = original_name
    
    print(f"🎨 พบไฟล์ texture: {len(texture_files)} ไฟล์")
    
    copied_count = 0
    not_found_count = 0
    already_exists_count = 0
    copy_errors = []
    
    # ประมวลผลไฟล์ที่ไม่พบ
    for missing_item in missing_files:
        folder_path = os.path.join(models_dir, missing_item['folder'])
        missing_png = missing_item['missing_png']
        target_path = os.path.join(folder_path, missing_png)
        
        print(f"  📁 ประมวลผล: {missing_item['folder']}")
        print(f"     ต้องการไฟล์: {missing_png}")
        
        # ตรวจสอบว่ามีไฟล์ใน texture source หรือไม่
        if missing_png in texture_files:
            source_file = texture_files[missing_png]
            source_path = os.path.join(texture_source_dir, source_file)
            
            # ตรวจสอบว่าไฟล์ปลายทางมีอยู่แล้วหรือไม่
            if os.path.exists(target_path):
                print(f"     ⚠️ ไฟล์มีอยู่แล้ว: {missing_png}")
                already_exists_count += 1
                continue
            
            # สร้างโฟลเดอร์หากไม่มี
            os.makedirs(folder_path, exist_ok=True)
            
            # คัดลอกไฟล์
            try:
                shutil.copy2(source_path, target_path)
                print(f"     ✅ คัดลอกสำเร็จ: {source_file} -> {missing_png}")
                copied_count += 1
            except Exception as e:
                print(f"     ❌ คัดลอกล้มเหลว: {e}")
                copy_errors.append({
                    'source': source_path,
                    'target': target_path,
                    'error': str(e)
                })
        else:
            print(f"     ❌ ไม่พบไฟล์: {missing_png}")
            not_found_count += 1
    
    # สรุปผลลัพธ์
    print(f"\n📊 สรุปผลการคัดลอก texture:")
    print(f"   คัดลอกสำเร็จ: {copied_count} ไฟล์")
    print(f"   ไม่พบไฟล์: {not_found_count} ไฟล์")
    print(f"   มีอยู่แล้ว: {already_exists_count} ไฟล์")
    print(f"   ข้อผิดพลาด: {len(copy_errors)} ไฟล์")
    
    if not_found_count > 0:
        print(f"\n💡 เคล็ดลับ: ไฟล์ที่ไม่พบอาจ:")
        print(f"   - ไม่มีใน {texture_source_dir}")
        print(f"   - มีชื่อที่แตกต่างจากที่คาดหวัง")
        print(f"   - อยู่ในโฟลเดอร์อื่น")
    
    # บันทึกผลลัพธ์
    result_report = {
        'timestamp': datetime.now().isoformat(),
        'source_texture_dir': texture_source_dir,
        'models_dir': models_dir,
        'summary': {
            'total_missing': len(missing_files),
            'copied_successfully': copied_count,
            'not_found': not_found_count,
            'already_exists': already_exists_count,
            'copy_errors': len(copy_errors)
        },
        'copy_errors': copy_errors
    }
    
    result_path = os.path.join(models_dir, 'texture_copy_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_report, f, indent=2, ensure_ascii=False)
    
    print(f"📋 รายงานผลลัพธ์บันทึกที่: {result_path}\n")
    
    return result_report

def resize_copied_images(models_dir, copy_result):
    """ขั้นตอนที่ 5: ปรับขนาดรูปภาพที่เพิ่งคัดลอกมา"""
    
    if not copy_result or copy_result['summary']['copied_successfully'] == 0:
        return None
    
    # อ่านรายงานไฟล์ที่ไม่พบเพื่อหาโฟลเดอร์ที่มีไฟล์ใหม่
    missing_report_path = os.path.join(models_dir, "missing_files_report.json")
    
    if not os.path.exists(missing_report_path):
        print("❌ ไม่พบรายงานไฟล์ที่ไม่พบ ข้ามการปรับขนาด")
        return None
    
    with open(missing_report_path, 'r', encoding='utf-8') as f:
        missing_report = json.load(f)
    
    missing_files = missing_report.get('missing_png_files', [])
    resized_count = 0
    resize_errors = []
    
    print(f"  กำลังตรวจสอบและปรับขนาดไฟล์ที่เพิ่งคัดลอก...")
    
    for missing_item in missing_files:
        folder_path = os.path.join(models_dir, missing_item['folder'])
        atlas_file = missing_item['atlas_file']
        png_file = missing_item['missing_png']
        
        atlas_path = os.path.join(folder_path, atlas_file)
        png_path = os.path.join(folder_path, png_file)
        
        # ตรวจสอบว่าไฟล์ PNG มีอยู่แล้วหรือไม่ (เพิ่งคัดลอกมา)
        if not os.path.exists(png_path):
            continue
        
        # ตรวจสอบว่าไฟล์ atlas มีอยู่หรือไม่
        if not os.path.exists(atlas_path):
            continue
        
        print(f"    ตรวจสอบ: {missing_item['folder']}/{png_file}")
        
        # อ่านขนาดจาก atlas
        atlas_w, atlas_h = parse_atlas_size(atlas_path)
        if not atlas_w or not atlas_h:
            print(f"      ⚠️ ไม่สามารถอ่านขนาดจาก atlas: {atlas_file}")
            continue
        
        # ตรวจสอบและปรับขนาดรูปภาพ
        try:
            with Image.open(png_path) as img:
                img_w, img_h = img.size
                if img_w != atlas_w or img_h != atlas_h:
                    print(f"      🔧 ปรับขนาด: {img_w}x{img_h} -> {atlas_w}x{atlas_h}")
                    resized = img.resize((atlas_w, atlas_h), Image.LANCZOS)
                    resized.save(png_path)
                    resized_count += 1
                else:
                    print(f"      ✅ ขนาดถูกต้องแล้ว: {img_w}x{img_h}")
        except Exception as e:
            print(f"      ❌ ไม่สามารถปรับขนาดรูปภาพ: {e}")
            resize_errors.append({
                'file': png_path,
                'error': str(e)
            })
    
    print(f"  ปรับขนาดรูปภาพเพิ่มเติม: {resized_count} รูป")
    if resize_errors:
        print(f"  ข้อผิดพลาดการปรับขนาด: {len(resize_errors)} ไฟล์")
    print()
    
    return {
        'resized_count': resized_count,
        'resize_errors': resize_errors
    }

def process_models_complete(models_dir, texture_source_dir=None):
    """ประมวลผลโมเดลทั้งหมดตามลำดับ"""
    if not os.path.exists(models_dir):
        print(f"❌ ไม่พบโฟลเดอร์: {models_dir}")
        return None
    
    print("🚀 เริ่มประมวลผลโมเดลทั้งหมด")
    print(f"โฟลเดอร์: {models_dir}")
    if texture_source_dir:
        print(f"Texture Source: {texture_source_dir}")
    print(f"เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # ขั้นตอนที่ 1: เปลี่ยนชื่อ
        rename_in_directory(models_dir)
        
        # ขั้นตอนที่ 2: แก้ไข atlas
        fix_atlas_filenames(models_dir)
        
        # ขั้นตอนที่ 3: ปรับขนาดรูปภาพและติดตามไฟล์ที่ไม่พบ
        missing_report = resize_images_and_track_missing(models_dir)
        
        copy_result = None
        resize_result = None
        if texture_source_dir and missing_report:
            copy_result = copy_missing_textures(models_dir, texture_source_dir, missing_report)
            
            # ขั้นตอนที่ 5: ปรับขนาดรูปภาพที่เพิ่งคัดลอกมา
            if copy_result and copy_result['summary']['copied_successfully'] > 0:
                print("=== ขั้นตอนที่ 5: Resize Newly Copied Images ===")
                print(f"กำลังปรับขนาดรูปภาพที่เพิ่งคัดลอก {copy_result['summary']['copied_successfully']} ไฟล์")
                resize_result = resize_copied_images(models_dir, copy_result)
        
        print("=" * 60)
        print("🎉 ประมวลผลเสร็จสิ้น!")
        
        if missing_report:
            print(f"\n📊 สรุปผลลัพธ์:")
            print(f"- โฟลเดอร์ที่ประมวลผล: {missing_report['summary']['processed_folders']}")
            print(f"- รูปภาพที่ปรับขนาด (ครั้งแรก): {missing_report['summary']['resized_images']}")
            print(f"- ไฟล์ PNG ที่ไม่พบ: {missing_report['summary']['missing_png_files']}")
            print(f"- Atlas ที่อ่านขนาดไม่ได้: {missing_report['summary']['atlas_without_size']}")
            
            if copy_result:
                print(f"- Texture ที่คัดลอกสำเร็จ: {copy_result['summary']['copied_successfully']}")
                print(f"- Texture ที่ไม่พบ: {copy_result['summary']['not_found']}")
                
                if resize_result:
                    print(f"- รูปภาพที่ปรับขนาด (หลังคัดลอก): {resize_result['resized_count']}")
            
            if missing_report['summary']['missing_png_files'] > 0:
                remaining_missing = missing_report['summary']['missing_png_files']
                if copy_result:
                    remaining_missing -= copy_result['summary']['copied_successfully']
                
                if remaining_missing > 0:
                    print(f"\n📋 ไฟล์ที่ยังไม่พบ: {remaining_missing} ไฟล์")
                    print(f"ดูรายละเอียดได้ที่ {models_dir}/missing_files_report.json")
                else:
                    print(f"\n🎉 ไฟล์ texture ครบถ้วนแล้ว!")
        
        return {
            'missing_report': missing_report,
            'copy_result': copy_result,
            'resize_result': resize_result
        }
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

def main():
    MODELS_DIR = "./Models"
    TEXTURE_SOURCE_DIR = "./Spine/Texture2D"
    
    print("=== Complete Models Processor (All-in-One) ===")
    print("ลำดับการทำงาน:")
    print("1. เปลี่ยนชื่อไฟล์และโฟลเดอร์ (# -> _, ตัวเล็ก)")
    print("2. แก้ไขไฟล์ .atlas")
    print("3. ปรับขนาดรูปภาพและติดตามไฟล์ที่ไม่พบ")
    print("4. คัดลอก texture ที่ไม่พบ (ถ้ามี)")
    print("5. ปรับขนาดรูปภาพที่เพิ่งคัดลอก")
    print()
    
    # ตรวจสอบว่ามี texture source หรือไม่
    if not os.path.exists(TEXTURE_SOURCE_DIR):
        print(f"⚠️ ไม่พบโฟลเดอร์ texture: {TEXTURE_SOURCE_DIR}")
        print("จะข้ามขั้นตอนการคัดลอก texture")
        TEXTURE_SOURCE_DIR = None
    
    result = process_models_complete(MODELS_DIR, TEXTURE_SOURCE_DIR)
    
    if result and result['missing_report']:
        missing_count = result['missing_report']['summary']['missing_png_files']
        copied_count = 0
        resized_after_copy = 0
        
        if result['copy_result']:
            copied_count = result['copy_result']['summary']['copied_successfully']
        
        if result['resize_result']:
            resized_after_copy = result['resize_result']['resized_count']
        
        remaining = missing_count - copied_count
        
        if remaining > 0:
            print(f"\n💡 ยังมีไฟล์ที่ไม่พบอีก {remaining} ไฟล์")
            print(f"ตรวจสอบรายละเอียดได้ที่ {MODELS_DIR}/missing_files_report.json")
        elif copied_count > 0:
            print(f"\n🎉 ประมวลผลเสร็จสมบูรณ์!")
            print(f"คัดลอก texture: {copied_count} ไฟล์")
            if resized_after_copy > 0:
                print(f"ปรับขนาดเพิ่มเติม: {resized_after_copy} ไฟล์")

if __name__ == "__main__":
    main()