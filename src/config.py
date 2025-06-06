from os import getenv
from pathlib import Path
from utypes.enums import LogLevel, PathType
from utypes.config import Config
from utils import log
import toml

def get_config(path_type: PathType, create: bool) -> Path:
    xdg_config_home = getenv("XDG_CONFIG_HOME")

    if xdg_config_home:
        config_dir = Path(xdg_config_home) / 'syncgdrive'
    else: 
        config_dir = Path.home() / '.config' / "syncgdrive"

    config_file = config_dir / "config.toml"

    if create:
        config_dir.mkdir(parents=True, exist_ok=True)
        if not config_file.exists():
            config_file.touch()

    if path_type is PathType.FILE:
        return config_file
    else:
        return config_dir

def load_config() -> Config:
    config_file = get_config(path_type=PathType.FILE, create=True)

    try:
        with open(config_file) as f:
            parsed_string = f.read()
    except FileNotFoundError:
        log(f"Config file not found at {config_file}.", LogLevel.ERROR)
        exit(1)
    except Exception as e:
        log(f"Error while opening the config file {config_file}: {e}", LogLevel.ERROR)
        exit(1)

    try:
        parsed_toml = toml.loads(parsed_string)
        validated_config = Config.model_validate(parsed_toml)
        return validated_config
    except Exception as e:
        log(f"Invalid config: {e}", LogLevel.ERROR)
        exit(1)
