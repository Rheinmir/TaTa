"""Prompt trích việc — precision-first (V1.1: CHỈ việc giao rõ ràng).

Yêu cầu model: đọc CẢ cụm hội thoại, chỉ trích việc có người nhận + hành động cụ thể;
bỏ qua chào hỏi/hỏi han/tán gẫu/cảm thán; trả JSON đúng schema; nếu không có việc →
{"tasks": []}. Mỗi việc kèm confidence (0–1) + reason + câu gốc (source_quote).
"""

SYSTEM = (
    "Bạn là trợ lý trích CÔNG VIỆC (work task) từ hội thoại chat tiếng Việt của một đội nhóm. "
    "CHỈ trích việc thoả ĐỦ 3 yếu tố: (1) hành động cụ thể, (2) có người làm (ngầm hoặc hiện), "
    "(3) thuộc BỐI CẢNH CÔNG VIỆC — vận hành, kỹ thuật/dev, báo cáo, hỗ trợ khách/nội bộ, cơ sở vật chất, hành chính.\n"
    "TUYỆT ĐỐI KHÔNG trích (kể cả khi nghe như mệnh lệnh):\n"
    "- Chào hỏi, tán gẫu, hỏi thông tin, cảm thán, đùa, xác nhận chung ('ok','haha','được').\n"
    "- Chuyện GAME/giải trí: mở khoá nhân vật/thiên phú, meta, waifu, lên đồ, cày...\n"
    "- Việc CÁ NHÂN/đời sống riêng (đi ăn, người yêu, về quê...).\n"
    "- Câu TƯỜNG THUẬT ai đang làm gì ('đang ngâm cứu...', 'tôi đang làm...') — không phải GIAO việc.\n"
    "CALIBRATE confidence (đừng mặc định cao):\n"
    "- 0.85–1.0: rõ ràng đủ cả 3 yếu tố + đúng bối cảnh công việc.\n"
    "- 0.6–0.84: thiếu/nhập nhằng 1 yếu tố.\n"
    "- <0.6: mơ hồ hoặc nghi ngờ → ĐỪNG trích (thà bỏ sót còn hơn bắt sai).\n"
    "Chỉ trả JSON hợp lệ, không thêm chữ nào ngoài JSON."
)

SCHEMA_HINT = (
    '{"tasks": [{'
    '"title": "ngắn gọn", '
    '"description": "mô tả nội suy đầy đủ", '
    '"assignee_hint": "tên người được giao nếu chat có nhắc, else null", '
    '"due": "YYYY-MM-DD hoặc mô tả mốc nếu chat nói, else null", '
    '"priority": "Low|Medium|High", '
    '"confidence": 0.0, '
    '"reason": "vì sao đây là việc giao rõ ràng", '
    '"source_quote": "câu gốc trong chat"'
    '}]}'
)


def build_user_prompt(channel, messages):
    """messages: list dict {sender, text, ts}. Trả nội dung user prompt."""
    lines = [f"Kênh: {channel}", "Hội thoại:"]
    for m in messages:
        lines.append(f"- {m.get('sender','?')}: {m.get('text','')}")
    lines.append("")
    lines.append("Trích các việc giao rõ ràng. Trả JSON đúng schema sau (mảng rỗng nếu không có việc):")
    lines.append(SCHEMA_HINT)
    return "\n".join(lines)
