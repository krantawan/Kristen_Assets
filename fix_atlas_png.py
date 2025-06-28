import os

def fix_atlas_filenames(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".atlas"):
                path = os.path.join(root, file)
                print(f"Processing: {path}")
                new_lines = []
                changed = False

                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        if ".png" in line:
                            # แปลงเป็นตัวเล็ก
                            lower_line = line.lower()
                            # แก้ # เป็น _
                            fixed_line = lower_line.replace("#", "_")
                            new_lines.append(fixed_line)
                            changed = True
                            print(f"  Fixed: {line.strip()} -> {fixed_line.strip()}")
                        else:
                            # บรรทัดอื่นไม่เปลี่ยน
                            new_lines.append(line)

                if changed:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    print("  File updated.\n")
                else:
                    print("  No changes needed.\n")

if __name__ == "__main__":
    base_directory = r"./Models"
    fix_atlas_filenames(base_directory)
