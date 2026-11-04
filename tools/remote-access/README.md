# Server remote access

## Codex: installed system boot service

This server uses Ubuntu user `ubuntu` (UID1001), home `/home/ubuntu`, Codex0.166.0, and the existing ChatGPT login. Repository instructions were read; no applicable CLAUDE.md or maintenance-specific file was found. Do not copy these user/path values onto another server without checking them there.

Installed service: `/etc/systemd/system/codex-remote.service`.

Versioned template: [codex-remote.service](codex-remote.service).

The service runs `/home/ubuntu/.local/bin/codex remote-control start --json` as `ubuntu`, after `network-online.target`. The stable CLI symlink is used rather than pinning a versioned package executable. Existing `HOME`/`CODEX_HOME`, authentication, daemon socket and remote identity are reused. No API key, pairing code, new login or public WebSocket listener is configured. The command is supported by the installed CLI and [official OpenAI documentation](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-remote-control).

`Type=oneshot` plus `RemainAfterExit=yes` means the expected healthy systemd state is **active (exited)**. The native Codex daemon runs separately. This unit is **boot startup, not continuous crash monitoring**. Failed startup is retried every10seconds, with at most3attempts within10minutes and a45second per-attempt timeout. Once startup succeeds, systemd does not continuously check the detached daemon. Network-online ordering does not guarantee the remote provider is reachable; exhausted retries need manual recovery.

`KillMode=process` and the absence of an ExecStop prevent stopping/restarting the launcher from killing native Codex sessions. Use the native daemon's stop/restart commands only when intentionally interrupting active work. Do not add a second watchdog, cron launcher or public listener.

Operations:

```sh
systemctl status codex-remote.service --no-pager
systemctl is-enabled codex-remote.service
journalctl -u codex-remote.service -n 30 --no-pager
/home/ubuntu/.local/bin/codex app-server daemon version
/home/ubuntu/.local/bin/codex doctor --summary
```

After an exhausted startup failure, inspect connectivity/authentication first, then:

```sh
sudo systemctl reset-failed codex-remote.service
sudo systemctl restart codex-remote.service
```

Reinstall after reviewing the unit's machine-specific user/path settings:

```sh
sudo install -o root -g root -m0644 tools/remote-access/codex-remote.service /etc/systemd/system/codex-remote.service
sudo systemd-analyze verify /etc/systemd/system/codex-remote.service
sudo systemctl daemon-reload
sudo systemctl enable --now codex-remote.service
```

Uninstalling the boot launcher deliberately leaves the native daemon alone:

```sh
sudo systemctl disable --now codex-remote.service
sudo rm /etc/systemd/system/codex-remote.service
sudo systemctl daemon-reload
```

Validation on2026-11-04: unit syntax passed (systemd also printed unrelated pre-existing monitoring-agent executable-permission warnings); system launcher enabled and startup returned connected/exit0. Native app-server PID1497459 and its process start time were unchanged, as were existing auth/config file metadata and the user's crontab hash. Codex doctor returned exit0 with a pre-existing session-history/database parity warning (one missing active index row and four stale archived rows); no history/database repair was attempted. Auth, daemon and remote connectivity checks remain usable. No public Codex TCP listener was found. The preliminary same-name **user** watchdog was disabled and removed before final validation. Private diagnostics are under ignored `local/diagnostics/remote-services-20261104`. No reboot was performed; actual cold-boot recovery is not yet tested.

## Claude: three approved workspace user services

`claude-remote@video.service`, `claude-remote@bursa.service` and `claude-remote@family.service` are installed under `/home/ubuntu/.config/systemd/user/`, with non-secret workspace/name configurations under `/home/ubuntu/.config/flh-remote/{video,bursa,family}.conf`. The respective roots are `/srv/dino_video/dino_video_editor`, `/srv/bursa-sim/bursa-sim` and `/srv/family-hub-monorepo`. It uses [claude-remote.py](claude-remote.py), installed at `/home/ubuntu/.local/lib/flh-remote/claude-remote.py`, and the existing Claude login. Ubuntu user lingering is enabled so this user service starts without an SSH login. Default permission approvals are retained; no bypass mode is configured. Capacity is limited to one session.

```sh
systemctl --user status claude-remote@video.service --no-pager
systemctl --user is-enabled claude-remote@video.service
journalctl --user -u claude-remote@video.service -n30 --no-pager
```

The video workspace trust confirmation was accepted through Claude's native dialog, then the terminal test server was stopped and replaced with the enabled systemd service. Connection was verified. A controlled service restart was performed; no existing interactive Claude sessions in other workspaces were stopped. Automatic approval initially rejected the proposed three-workspace operation before execution, pending scope confirmation. The owner subsequently explicitly selected all three workspaces. Bursa and Family Hub instances were then installed/enabled using their existing trusted workspaces, without stopping their interactive terminals. All three services were verified active, enabled and connected.

Claude session restoration is provider-limited: according to [official Claude documentation](https://code.claude.com/docs/en/remote-control#resume-sessions-after-stopping-the-server), the server can restore remote sessions for roughly four hours. Longer downtime may create a new session URL, even though the service automatically returns. Expired sign-ins, account restrictions and upstream outages still require attention. Never treat boot automation as a guarantee that every old link stays valid forever.

## Distinguish the other host's template

A concurrent upstream commit added `ops/systemd/codex-startup.service` and `docs/codex-startup.md` for the other checkout at `/srv/video_editor`. It was retained during rebase and is not installed on this machine (`freetierinstance`). This machine uses only `/etc/systemd/system/codex-remote.service`, with its source template here and WorkingDirectory `/home/ubuntu`. Never enable both names on the same host. The previous Codex user watchdog is absent. The native managed daemon PID/start time remained unchanged through both manual launcher starts. No server reboot was requested or performed.
