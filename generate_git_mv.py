import os

def generate_git_mv_commands(base_dir):
    commands = []
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in files:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.relpath(os.path.join(root, name))
                new_name = name.replace("#", "_").lower()
                new_path = os.path.relpath(os.path.join(root, new_name))
                cmd = f'git mv -f "{old_path}" "{new_path}"'
                commands.append(cmd)

        for name in dirs:
            if "#" in name or any(c.isupper() for c in name):
                old_path = os.path.relpath(os.path.join(root, name))
                new_name = name.replace("#", "_").lower()
                new_path = os.path.relpath(os.path.join(root, new_name))
                cmd = f'git mv -f "{old_path}" "{new_path}"'
                commands.append(cmd)

    return commands

if __name__ == "__main__":
    base_directory = r"./Models"
    cmds = generate_git_mv_commands(base_directory)
    print("\n# ====== GIT MV COMMANDS ======\n")
    for c in cmds:
        print(c)
