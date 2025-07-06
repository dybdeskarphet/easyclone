from __future__ import annotations
from threading import Lock
from os import getenv
from pathlib import Path
from easyclone.utypes.enums import LogLevel
from easyclone.utypes.config import BackupConfigModel, ConfigModel, RcloneConfigModel
import toml

class Config:
    _instance: Config | None = None
    _lock: Lock = Lock()
    _path: Path = Path.home() / '.config' / "easyclone" / "config.toml"
    _config: ConfigModel | None = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                instance = super().__new__(cls)
                instance._get_config_path()
                instance._config = instance._load_config()
                cls._instance = instance

        return cls._instance

    def _get_config_path(self):
        xdg_config_home = getenv("XDG_CONFIG_HOME")

        empty_config = ConfigModel(
            backup=BackupConfigModel(
                sync_paths=[],
                copy_paths=[],
                remote_name="GoogleDrive",
                root_dir="Backups/PC",
                verbose_log=False
            ),
            rclone=RcloneConfigModel(
                args=[
                    "--update",
                    "--verbose",
                    "--transfers 30",
                    "--checkers 8",
                    "--contimeout 60s",
                    "--timeout 300s",
                    "--retries 3",
                    "--low-level-retries 10",
                    "--stats 1s"
                ],
                concurrent_limit=50
            )
        )
    
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / 'easyclone'
        else: 
            config_dir = Path.home() / '.config' / "easyclone"
    
        config_file = config_dir / "config.toml"

        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)

        if not config_file.exists():
            config_file.touch()
            with open(config_file, "w") as f:
                _ = toml.dump(empty_config.model_dump(), f)
    
        self._path = config_file

    def _load_config(self):
        from easyclone.utils.essentials import log
        self._get_config_path()

        try:
            with open(self._path) as f:
                parsed_string = f.read()
        except FileNotFoundError:
            log(f"Config file not found at {self._path}.", LogLevel.ERROR)
            exit(1)
        except Exception as e:
            log(f"Error while opening the config file {self._path}: {e}", LogLevel.ERROR)
            exit(1)

        try:
            parsed_toml = toml.loads(parsed_string)
            validated_config = ConfigModel.model_validate(parsed_toml)

            # Normalize config
            validated_config.backup.root_dir = validated_config.backup.root_dir.strip("/")

            return validated_config
        except Exception as e:
            log(f"Invalid config: {e}", LogLevel.ERROR)
            exit(1)

    def config(self) -> ConfigModel:
        if self._config is None:
            raise RuntimeError("Config is not loaded yet")
        return self._config

cfg = Config().config()
