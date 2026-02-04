On Ubuntu, `systemctl` manages `systemd` unit files, which are stored in several key locations:

1.  **`/etc/systemd/system/`**: This is the primary location for custom service unit files that you create or modify. Unit files placed here take precedence over those in `/lib/systemd/system/`. This is generally the recommended place for system administrators to add their own service definitions.
2.  **`/lib/systemd/system/`**: This directory contains unit files installed by packages. You should generally avoid modifying files directly in this directory, as they might be overwritten during package updates.
3.  **`/run/systemd/system/`**: This directory stores runtime-generated unit files. Contents here are volatile and will be lost on reboot.
4.  **`~/.config/systemd/user/`**: This directory is used for user-specific `systemd` services, which are managed with `systemctl --user`.

For setting up your bot as a custom service that starts on boot and runs in the background, `/etc/systemd/system/` is the appropriate place for its `.service` unit file.