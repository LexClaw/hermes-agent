from types import SimpleNamespace

from gateway import run as gateway_run
from gateway.config import Platform


SMS_MISSING_WEBHOOK = (
    "[sms] Refusing to start: SMS_WEBHOOK_URL is required for Twilio "
    "signature validation. Set it to the public URL configured in your "
    "Twilio console (e.g. https://example.com/webhooks/twilio). "
    "For local development without validation, set "
    "SMS_INSECURE_NO_SIGNATURE=true (NOT recommended for production)."
)


def test_sms_missing_webhook_surfaces_mc_card_and_morning_notice(tmp_path, monkeypatch):
    helper = tmp_path / "mc-card-from-cron.py"
    helper.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    held_dir = tmp_path / "held"
    calls = []

    def fake_run(cmd, text, capture_output, timeout, check):
        calls.append(
            {
                "cmd": cmd,
                "body": (tmp_path / "missing").read_text(encoding="utf-8")
                if False
                else None,
            }
        )
        body_file = cmd[cmd.index("--body-file") + 1]
        calls[-1]["body"] = open(body_file, encoding="utf-8").read()
        return SimpleNamespace(returncode=0, stdout='{"action":"create","id":"kn123"}', stderr="")

    monkeypatch.setenv("HERMES_MC_CARD_FROM_CRON", str(helper))
    monkeypatch.setenv("HERMES_CRON_HELD_DIR", str(held_dir))
    monkeypatch.setattr("subprocess.run", fake_run)

    gateway_run._surface_gateway_startup_guard(
        Platform.SMS,
        "sms_missing_webhook_url",
        SMS_MISSING_WEBHOOK,
    )

    assert len(calls) == 1
    cmd = calls[0]["cmd"]
    assert "--dedup-key" in cmd
    assert cmd[cmd.index("--dedup-key") + 1] == "gateway-startup-missing-env-SMS_WEBHOOK_URL"
    assert cmd[cmd.index("--category") + 1] == "tech"
    assert cmd[cmd.index("--agent") + 1] == "grant"
    assert "infra-broken" in [cmd[i + 1] for i, part in enumerate(cmd[:-1]) if part == "--tag"]
    assert "Gateway platform `sms` refused to start at boot" in calls[0]["body"]
    assert "SMS_WEBHOOK_URL is required for Twilio signature validation" in calls[0]["body"]
    assert "Set SMS_WEBHOOK_URL to the public Twilio webhook URL" in calls[0]["body"]

    notice = held_dir / "gateway-sms-sms_webhook_url-misconfig.md"
    assert notice.exists()
    notice_text = notice.read_text(encoding="utf-8")
    assert "Gateway sms is down: SMS_WEBHOOK_URL is missing" in notice_text
    assert "gateway-startup-missing-env-SMS_WEBHOOK_URL" in notice_text


def test_startup_guard_ignores_unrelated_fatal_errors(tmp_path, monkeypatch):
    held_dir = tmp_path / "held"

    def fail_run(*args, **kwargs):  # pragma: no cover
        raise AssertionError("subprocess.run should not be called")

    monkeypatch.setenv("HERMES_CRON_HELD_DIR", str(held_dir))
    monkeypatch.setattr("subprocess.run", fail_run)

    gateway_run._surface_gateway_startup_guard(
        Platform.TELEGRAM,
        "telegram_missing_token",
        "TELEGRAM_BOT_TOKEN is missing",
    )

    assert not held_dir.exists()
