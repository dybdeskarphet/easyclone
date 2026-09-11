self:
{
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.services.easyclone;
  tomlFormat = pkgs.formats.toml { };

  filterNulls = lib.filterAttrs (_: v: v != null);

  generatedConfig = lib.recursiveUpdate {
    backup = {
      remote_name = cfg.backup.remoteName;
      root_dir = cfg.backup.rootDir;
      sync_paths = cfg.backup.syncPaths;
      copy_paths = cfg.backup.copyPaths;
      verbose_log = cfg.backup.verboseLog;
      versioning = filterNulls {
        enable = cfg.backup.versioning.enable;
        remote_name = cfg.backup.versioning.remoteName;
        path = cfg.backup.versioning.path;
        timestamp = cfg.backup.versioning.timestamp;
        prune_timeout = cfg.backup.versioning.pruneTimeout;
      };
    };
    rclone = {
      args = cfg.rclone.args;
      concurrent_limit = cfg.rclone.concurrentLimit;
    };
    daemon = {
      interval = cfg.daemon.interval;
      countdown = cfg.daemon.countdown;
    };
  } cfg.extraConfig;
in
{
  options.services.easyclone = {
    enable = lib.mkEnableOption "easyclone backup service";

    package = lib.mkOption {
      type = lib.types.package;
      default = self.packages.${pkgs.system}.default;
      defaultText = lib.literalExpression "self.packages.\${pkgs.system}.default";
      description = "The easyclone package to install and use.";
    };

    backup = {
      remoteName = lib.mkOption {
        type = lib.types.str;
        example = "GoogleDrive";
        description = "Name of the rclone remote configuration (defined in ~/.config/rclone/rclone.conf).";
      };

      rootDir = lib.mkOption {
        type = lib.types.str;
        default = "Backups";
        example = "Backups/MyPC";
        description = "The destination root directory on your remote cloud storage where backups are placed.";
      };

      syncPaths = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        example = [
          "~/Documents"
          "~/Pictures"
          "$XDG_CONFIG_HOME"
        ];
        description = "List of directory/file paths to perform 'sync' operations on (mirrors local to remote, deletes removed files).";
      };

      copyPaths = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        example = [ "~/Downloads/archive.tar.gz" ];
        description = "List of directory/file paths to perform 'copy' operations on (adds/updates only, never deletes).";
      };

      verboseLog = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = "Enables detailed rclone transfer logging by default.";
      };

      versioning = {
        enable = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = "Enable versioning of modified or deleted files using Rclone's --backup-dir mechanism.";
        };

        remoteName = lib.mkOption {
          type = lib.types.nullOr lib.types.str;
          default = null;
          example = "GoogleDrive";
          description = "Optional remote name. If omitted or null, defaults to backup.remoteName.";
        };

        path = lib.mkOption {
          type = lib.types.nullOr lib.types.str;
          default = null;
          example = "Backups/MyPC/Archive";
          description = "Directory path on the remote where archived versions are stored.";
        };

        timestamp = lib.mkOption {
          type = lib.types.str;
          default = "%Y-%m-%d_%H-%M-%S";
          description = "Python strftime format used to name backup session archive folders.";
        };

        pruneTimeout = lib.mkOption {
          type = lib.types.nullOr lib.types.str;
          default = null;
          example = "30d";
          description = "Optional duration to prune/purge old archive folders (e.g., '30d', '24h', '1h30m').";
        };
      };
    };

    rclone = {
      args = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [
          "--update"
          "--verbose"
          "--transfers 30"
          "--checkers 8"
          "--contimeout 60s"
          "--timeout 300s"
          "--retries 3"
          "--low-level-retries 10"
          "--stats 1s"
        ];
        description = "Rclone flags passed to every sync/copy/lsd/mkdir subprocess call.";
      };

      concurrentLimit = lib.mkOption {
        type = lib.types.int;
        default = 50;
        example = 4;
        description = "Maximum number of concurrent path sync/copy commands allowed to execute at once.";
      };
    };

    daemon = {
      interval = lib.mkOption {
        type = lib.types.int;
        default = 60;
        description = "Time interval in minutes between periodic daemon backups.";
      };

      countdown = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = "Display a countdown timer in the terminal during the waiting period.";
      };
    };

    timer = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = "Enable periodic systemd user timer to run easyclone start-backup.";
      };

      onBootSec = lib.mkOption {
        type = lib.types.str;
        default = "5min";
        description = "Time after boot before first backup run.";
      };

      onUnitActiveSec = lib.mkOption {
        type = lib.types.str;
        default = "1h";
        description = "Interval between backup runs.";
      };

      onCalendar = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        example = "hourly";
        description = "Systemd OnCalendar schedule expression (overrides onUnitActiveSec if set).";
      };

      persistent = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = "Catch up on missed backup runs when machine was powered off.";
      };
    };

    extraConfig = lib.mkOption {
      type = lib.types.attrs;
      default = { };
      description = "Extra configuration options to merge into ~/.config/easyclone/config.toml.";
    };
  };

  config = lib.mkIf cfg.enable {
    assertions = [
      {
        assertion =
          cfg.backup.versioning.enable
          -> (cfg.backup.versioning.path != null && cfg.backup.versioning.path != "");
        message = "services.easyclone.backup.versioning.path must be specified when versioning is enabled.";
      }
    ];

    home.packages = [ cfg.package ];

    xdg.configFile."easyclone/config.toml".source =
      tomlFormat.generate "easyclone-config.toml" generatedConfig;

    systemd.user.services.easyclone = {
      Unit = {
        Description = "Easyclone Backup Service";
        Wants = [ "network-online.target" ];
        After = [ "network-online.target" ];
      };

      Service = {
        Type = "oneshot";
        Nice = 19;
        IOSchedulingClass = "idle";
        TimeoutStopSec = "60s";
        ExecStart = "${cfg.package}/bin/easyclone start-backup";
      };

      Install = {
        WantedBy = [ "default.target" ];
      };
    };

    systemd.user.timers.easyclone = lib.mkIf cfg.timer.enable {
      Unit = {
        Description = "Timer for Easyclone Backup Service";
      };

      Timer = {
        OnBootSec = cfg.timer.onBootSec;
        Persistent = cfg.timer.persistent;
      }
      // (
        if cfg.timer.onCalendar != null then
          {
            OnCalendar = cfg.timer.onCalendar;
          }
        else
          {
            OnUnitActiveSec = cfg.timer.onUnitActiveSec;
          }
      );

      Install = {
        WantedBy = [ "timers.target" ];
      };
    };
  };
}
