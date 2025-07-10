import os
from PIL import Image

def parse_atlas_size(atlas_path):
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

def fix_texture_if_needed(folder):
    for file in os.listdir(folder):
        if file.endswith(".atlas"):
            base_name = file.replace(".atlas", "")
            atlas_path = os.path.join(folder, file)
            png_path = os.path.join(folder, base_name + ".png")

            if not os.path.exists(png_path):
                print(f"⚠️ PNG not found: {png_path}")
                continue

            atlas_w, atlas_h = parse_atlas_size(atlas_path)
            if not atlas_w or not atlas_h:
                print(f"⚠️ Couldn't read size from atlas: {atlas_path}")
                continue

            with Image.open(png_path) as img:
                img_w, img_h = img.size
                if img_w != atlas_w or img_h != atlas_h:
                    print(f"🔧 Scaling {png_path} from {img_w}x{img_h} → {atlas_w}x{atlas_h}")
                    resized = img.resize((atlas_w, atlas_h), Image.BICUBIC)
                    resized.save(png_path)

def walk_models_folder(models_dir):
    for dirpath, dirnames, filenames in os.walk(models_dir):
        if any(f.endswith(".atlas") for f in filenames):
            fix_texture_if_needed(dirpath)

if __name__ == "__main__":
    MODELS_PATH = "./Models" 
    walk_models_folder(MODELS_PATH)
