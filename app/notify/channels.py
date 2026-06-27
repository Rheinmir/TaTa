"""Kênh thông báo — adapter: có cấu hình env → gửi thật; không → dry-run (log).

EmailSMTPChannel  : SMTP (SMTP_HOST/PORT/USER/PASS/FROM). [hoặc đổi sang MS Graph sau]
ZaloBridgeChannel : POST {to,text} tới zca-bridge outbound (BRIDGE_OUTBOUND_URL).
TeamsGraphChannel : MS Graph (TEAMS_GRAPH_* ) — hiện stub→dry-run, cắm Graph ở bước sau.
DryRunChannel     : luôn dry-run, dùng cho test (ghi lại các lần gửi).
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Notify")


class NotifyChannel:
    name = "channel"

    @property
    def configured(self):
        return False

    def send(self, target, subject, body):
        """Trả {channel, target, status, detail}."""
        if not target:
            return {"channel": self.name, "target": target, "status": "skip", "detail": "no target"}
        if not self.configured:
            logger.info("…(dry-run %s → %s) %s", self.name, target, subject)
            return {"channel": self.name, "target": target, "status": "dry-run", "detail": subject}
        try:
            self._send(target, subject, body)
            return {"channel": self.name, "target": target, "status": "sent", "detail": ""}
        except Exception as e:  # noqa: BLE001
            logger.warning("Gửi %s → %s lỗi: %s", self.name, target, e)
            return {"channel": self.name, "target": target, "status": "error", "detail": str(e)}

    def _send(self, target, subject, body):
        raise NotImplementedError


class EmailSMTPChannel(NotifyChannel):
    name = "email"

    def __init__(self):
        self.host = os.environ.get("SMTP_HOST")
        self.port = int(os.environ.get("SMTP_PORT", "587"))
        self.user = os.environ.get("SMTP_USER")
        self.pwd = os.environ.get("SMTP_PASS")
        self.sender = os.environ.get("SMTP_FROM", self.user or "tata@local")

    @property
    def configured(self):
        return bool(self.host)

    def _send(self, target, subject, body):
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = target
        with smtplib.SMTP(self.host, self.port, timeout=20) as s:
            s.starttls()
            if self.user:
                s.login(self.user, self.pwd)
            s.sendmail(self.sender, [target], msg.as_string())


class ZaloBridgeChannel(NotifyChannel):
    name = "zalo"

    def __init__(self):
        self.url = os.environ.get("BRIDGE_OUTBOUND_URL")  # endpoint gửi outbound của zca-bridge
        self.token = os.environ.get("BRIDGE_OUTBOUND_TOKEN")

    @property
    def configured(self):
        return bool(self.url)

    def _send(self, target, subject, body):
        import requests
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        r = requests.post(self.url, json={"to": target, "text": f"{subject}\n{body}"},
                          headers=headers, timeout=15)
        r.raise_for_status()


class TeamsGraphChannel(NotifyChannel):
    name = "teams"

    def __init__(self):
        self.tenant = os.environ.get("TEAMS_GRAPH_TENANT")
        self.client_id = os.environ.get("TEAMS_GRAPH_CLIENT_ID")
        self.secret = os.environ.get("TEAMS_GRAPH_SECRET")

    @property
    def configured(self):
        return bool(self.tenant and self.client_id and self.secret)

    def _send(self, target, subject, body):
        # TODO: MS Graph (chat/message) — cần app reg + token. Hiện chưa cấu hình → dry-run.
        raise NotImplementedError("Teams Graph chưa hiện thực — cấu hình TEAMS_GRAPH_* để bật.")


class DryRunChannel(NotifyChannel):
    """Cho test: luôn dry-run, lưu lại các lần gửi vào self.sent."""

    def __init__(self, name):
        self.name = name
        self.sent = []

    @property
    def configured(self):
        return False

    def send(self, target, subject, body):
        res = super().send(target, subject, body)
        if res["status"] != "skip":
            self.sent.append(res)
        return res
