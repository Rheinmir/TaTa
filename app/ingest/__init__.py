"""TaTa ingest — Phase 1: đọc tin từ Chatwoot, lọc kênh 2 chiều, debounce theo hội thoại.

Đầu ra: 'batch hội thoại' (tenant + channel + conversation + messages) đã lắng,
sẵn sàng cho Phase 2 (AI extractor). Source trừu tượng để test offline (FakeSource)
và chạy thật (ChatwootSource).
"""
from .channel_filter import ChannelFilter
from .source import Message, MessageSource, FakeSource, ChatwootSource
from .pipeline import IngestPipeline, IngestStateStore

__all__ = [
    "ChannelFilter", "Message", "MessageSource", "FakeSource",
    "ChatwootSource", "IngestPipeline", "IngestStateStore",
]
