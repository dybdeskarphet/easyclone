# Systemd Timer

Instead of running `easyclone daemon` in a continuous background loop, you can use `systemd` user timers to natively schedule your backups. This is more robust and survives reboots gracefully.

1. Copy the `.service` and `.timer` files to your user systemd directory:

   ```bash
   mkdir -p ~/.config/systemd/user/
   cp easyclone.service easyclone.timer ~/.config/systemd/user/
   ```

2. Reload the systemd daemon to recognize the new files:

   ```bash
   systemctl --user daemon-reload
   ```

3. Enable and start the timer:
   ```bash
   systemctl --user enable --now easyclone.timer
   ```
