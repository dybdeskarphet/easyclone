## [unreleased]

### 🚀 Features

- Introduce versioning system with --backup-dir
- *(client)* Log the archive path if versioning is enabled
- *(models)* Add prune_timeout for the future use of pruning logic
- *(client)* Add archive prune logic

### 🐛 Bug Fixes

- *(tree)* Check path_type in create_dirs_array
- *(client)* Fix file deletion deletion for pruning

### 📚 Documentation

- *(changelog)* Update CHANGELOG
- *(config.toml)* Add the new flags, fields and populate with explanatory comments
- *(changelog)* Update CHANGELOG
- *(config.toml)* Add prune_timeout to example config

### ⚙️ Miscellaneous Tasks

- Reshape the file structure entirely
- *(release)* Bump version
## [1.2.0] - 2026-07-02

### 🚀 Features

- Add daemon mode

### 🐛 Bug Fixes

- *(main)* Fix socket file being deleted when it belongs to an existing instance

### 📚 Documentation

- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG

### ⚙️ Miscellaneous Tasks

- *(systemd)* Add an example systemd service and timer
- *(release)* Bump version
## [1.1.1] - 2026-06-30

### 🐛 Bug Fixes

- *(operations)* Show empty paths log when there are empty paths

### 📚 Documentation

- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG
- *(changelog)* Update CHANGELOG

### ⚙️ Miscellaneous Tasks

- *(release)* Bump version
- *(cliff)* Exclude documentation commits
## [1.1.0] - 2026-06-25

### 🚀 Features

- Add the get-missing command for checking missing files and dirs

### 📚 Documentation

- *(CHANGELOG)* Add CHANGELOG with git-cliff
- *(pyproject)* Add changelog link to pyproject.toml
- *(README)* Add shields
- *(changelog)* Update CHANGELOG

### ⚙️ Miscellaneous Tasks

- Fix formatting
- *(release)* Add auto release creator
- *(pypi)* Add auto pypi publisher
- *(release)* Bump version
## [1.0.0] - 2025-09-17

### 🚀 Features

- *(main)* Add --show-finished argument to get-status
- *(main)* Delete socket file if SIGTERM or SIGINT is sent

### 🐛 Bug Fixes

- *(main)* Make socket cleanup run only with start-backup

### 💼 Other

- Bump version

### 📚 Documentation

- *(examples)* Update the example config
## [0.3.0] - 2025-07-15

### 🚀 Features

- *(config)* Use default values for some of the config values if doesn't exist
- *(paths)* Add support for `env` variables in paths

### 💼 Other

- Bump version
- Bump version

### 📚 Documentation

- *(README)* Update README
## [0.2.0] - 2025-07-06

### 🚀 Features

- Add empty_paths to IPC and add its CLI flag to get-status

### 🐛 Bug Fixes

- Exit and report if rclone is not in the PATH
- Strip slashes from root_dir config variable
- Warn and exit if easyclone is already running
- Expect CommandType when using make_backup_operation

### 🚜 Refactor

- *(rclone.operations)* Delete backup operations and use make_backup_operation function instead
## [0.1.0] - 2025-07-06

### 🚀 Features

- *(enums)* Add enum type for backup logs
- Implement the core bakcup logic and use it in main
- Run backup operation concurrently and get rclone args from the config
- Add file type property to PathItem (therefore to SyncStatusItem too)
- Create a tree from dirs and create dirs at remote through BFS
- Accept different type of commands in main.py using typer
- Add total_path_count and finished_path_count to the IPC
- *(main)* Rename read_ipc to get_status and add flags to it
- *(dirs)* Check if dir exists before creating it
- *(config)* Create a template config if config file doesn't exist

### 🐛 Bug Fixes

- *(config)* Fix config.toml file
- *(utils)* Fix red color typo
- *(dirs)* Fix fake root dir problem
- Some fixes related to task execution order and CLI arguments
- *(ipc.client)* Exit with 1 if no tasks are running
- *(main)* Make get-status show the entire JSON if all the flags are passed

### 🚜 Refactor

- Simplify rclone functions and use PathItem for paths
- Directly use config inside main and rename backup_paths to copy_paths
- Make the whole project more modular
- *(config)* Use a config singleton to make the config more accessible
- *(utils)* Split utils file
- Change the src directory to make the project packageable

### 📚 Documentation

- *(README)* Add warning
- Create a to-do for fixing multiple directories on concurrnet backups problem
- Improve the documentation and add LICENSE
- *(README)* Fix header level
- *(readme)* Update Installation methods

### ⚙️ Miscellaneous Tasks

- Reorganize file structure
- *(ipc.client)* Delete "as e" part in try-catch since it's not used
- *(backup.operations)* Make the code more readable
- Rename the project
