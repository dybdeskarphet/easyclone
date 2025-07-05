# ☁️ easyclone

**easyclone** is a lightweight, configurable CLI tool that wraps `rclone` to behave more like Google's *Backup and Sync* app.

You define what to back up, where to back it up, and EasyClone handles the syncs and copies — clean, fast, and reliable.

## 🚀 Features

* 🔁 Sync & Copy support per-path
* 📁 Backup multiple paths at once
* 🧠 Human-friendly TOML config
* 🛠️ IPC-ready architecture for future GUI or monitoring tools
* 🔊 Optional verbose logging

## 🛠️ Requirements

* Python **3.13+**
* [`rclone`](https://rclone.org/) installed and accessible in your `$PATH`
* `pydantic>=2.11.5`
* `toml>=0.10.2`
* `typer>=0.16.0`

## 🧪 Example Usage

```bash
easyclone start-backup
```

It will:

* Sync the paths in `sync_paths`
* Copy the paths in `copy_paths`
* Use the `remote_name` and `root_dir` to target your cloud storage

## 🙋‍♀️ Contributing

PRs welcome. Bug reports even more welcome.

## ❓ FAQ

Why does it create the folders first?
> Because services like Google Drive support multiple folders with the same name in the same directory. So when you try to concurrently backup paths from the same directory, it will create the parent directory more than once, and we don't want that.

## 📄 License

GPLv3 — do whatever you want, just don't blame me if you sync your `/` folder to the cloud :)

