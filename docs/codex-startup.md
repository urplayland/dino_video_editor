# Codex startup after a server reboot

`ops/systemd/codex-startup.service` starts the existing managed Codex daemon as `ubuntu` when the server reaches its normal boot target and networking is ready. It uses the supported `codex remote-control start` lifecycle command, the user's existing login and remote-control configuration, and the normal CLI symlink so package updates do not require a version-specific service edit.

The start command reuses an already running managed daemon. The systemd unit is a startup launcher: `active (exited)` is expected after the command succeeds. Codex continues to manage the background daemon itself. The unit retries failed startup commands up to five times per five minutes; it does not independently monitor every later daemon exit or resume an interactive terminal UI.

Installed unit: `/etc/systemd/system/codex-startup.service`. It is enabled for `multi-user.target`, does not depend on an SSH login or user lingering, and does not modify cron. It adds no listener configuration or public port. Authentication stays under the user's private Codex home; no token or pairing code belongs in this repository.

```sh
sudo systemctl status codex-startup.service
/home/ubuntu/.local/bin/codex app-server daemon version
sudo journalctl -u codex-startup.service -b --no-pager
```

To deploy this template after restoration:

```sh
sudo install -m 0644 ops/systemd/codex-startup.service /etc/systemd/system/codex-startup.service
sudo systemd-analyze verify /etc/systemd/system/codex-startup.service
sudo systemctl daemon-reload
sudo systemctl enable --now codex-startup.service
```

To disable future boot launches, run `sudo systemctl disable codex-startup.service`. Use the native Codex lifecycle commands for deliberate daemon stops/restarts; stopping an owned daemon can interrupt active work.

Validation: unit syntax, enabled boot link, a successful launch against the existing daemon, and unchanged daemon PID were checked during installation. A separate owner-authorized reboot test passed on 2026-11-04: the server booted at14:43:03 UTC, systemd launched this unit at14:43:17 UTC, and the managed daemon started at14:43:32 UTC inside `/system.slice/codex-startup.service`. An independent postboot observer checked process ownership before querying Codex and confirmed one running managed daemon, a successful startup unit, and passing kernel/network/SSH/cron/OCI-agent checks. The temporary observer removed its own startup registration; existing cron jobs were preserved. Detailed host logs remain private under `local/diagnostics/codex-boot-test/`.

Official lifecycle reference: https://learn.chatgpt.com/docs/cli/reference#codex-remote-control

## Other checkout: freetierinstance

The checkout at `/srv/dino_video/dino_video_editor` uses `/etc/systemd/system/codex-remote.service` instead. See [that host's service templates and operating guide](../tools/remote-access/README.md). Only one Codex boot launcher should be enabled per host; do not install this document's `/srv/video_editor` template blindly on the other checkout.
