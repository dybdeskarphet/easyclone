from config import get_config_value, load_config
from utils import organize_paths

def main():
    config = load_config()
    backup_paths: list[str] = get_config_value(config, "backup", "backup_paths")
    remote_name = get_config_value(config, "backup", "remote_name").rstrip("/\\")
    root_dir = get_config_value(config, "backup", "root_dir").rstrip("/\\")

    organized_backup_paths = organize_paths(backup_paths, remote_name, root_dir)
    print(organized_backup_paths)

if __name__ == "__main__":
    main()
