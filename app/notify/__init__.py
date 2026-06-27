"""TaTa notify — Phase 4: báo người được giao qua Email + Zalo + Teams (V3b.1).

Mỗi kênh là 1 adapter (NotifyChannel): có cấu hình env → gửi thật, không thì dry-run
(log, để verify offline). NotifyService định tuyến theo kênh người đó đăng ký.
"""
from .channels import (NotifyChannel, EmailSMTPChannel, ZaloBridgeChannel,
                       TeamsGraphChannel, DryRunChannel)
from .service import NotifyService

__all__ = ["NotifyChannel", "EmailSMTPChannel", "ZaloBridgeChannel",
           "TeamsGraphChannel", "DryRunChannel", "NotifyService"]
