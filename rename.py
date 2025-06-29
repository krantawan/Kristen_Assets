import os

def rename_in_directory(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # Rename files first
        for name in files:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.join(root, name)
                new_name = name.replace("#", "_").lower()
                new_path = os.path.join(root, new_name)
                print(f"Renaming file: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

        # Rename directories
        for name in dirs:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.join(root, name)
                new_name = name.replace("#", "_").lower()
                new_path = os.path.join(root, new_name)
                print(f"Renaming folder: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

if __name__ == "__main__":
    # เปลี่ยน path ตรงนี้ให้ชี้ไปที่ Models folder
    base_directory = r"./Models"
    rename_in_directory(base_directory)
