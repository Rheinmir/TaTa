"""ChannelFilter — lọc kênh 2 chiều (V3a.2: 'bỏ kênh này' hoặc 'chỉ kênh này').

mode='allow'  → CHỈ nhận kênh trong danh sách (allowlist).
mode='block'  → LOẠI kênh trong danh sách (blocklist).
mode=None     → nhận tất cả.
Khớp theo tên kênh đầy đủ hoặc tiền tố (vd 'Zalo nhóm' khớp 'Zalo nhóm A').
"""


class ChannelFilter:
    def __init__(self, mode=None, channels=None):
        assert mode in (None, "allow", "block"), "mode phải là None|allow|block"
        self.mode = mode
        self.channels = [c.strip() for c in (channels or []) if c.strip()]

    def _match(self, channel):
        ch = (channel or "").strip()
        return any(ch == c or ch.startswith(c) for c in self.channels)

    def allows(self, channel):
        if self.mode == "allow":
            return self._match(channel)
        if self.mode == "block":
            return not self._match(channel)
        return True

    @classmethod
    def from_config(cls, cfg):
        """cfg = {'mode': 'allow'|'block'|None, 'channels': [...]}"""
        cfg = cfg or {}
        return cls(cfg.get("mode"), cfg.get("channels"))
