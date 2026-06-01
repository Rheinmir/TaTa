# AGENT.md
## Rules of Play for TaTa (Team Automated Task Agent)

### 1. Luật của Dự án (Core Laws)
* **KHÔNG BAO GIỜ ghi vào `raw/`:** Thư mục `raw/` chỉ chứa tài liệu nguyên bản do con người cung cấp. Agent tuyệt đối không ghi, sửa, hay xóa nội dung trong đó.
* **LUÔN cập nhật `wiki/index.md`:** Mỗi khi thêm hoặc xóa một trang wiki, bắt buộc phải cập nhật chỉ mục trong `wiki/index.md`.
* **LUÔN ghi chép vào `wiki/log.md`:** Cập nhật nhật ký vận hành sau mỗi thao tác (ingest, query, lint, v.v.).
* **Sử dụng `[[wikilinks]]`:** Luôn dùng liên kết wiki (ví dụ: `[[AGENT-business]]`) để kết nối các trang tri thức liên quan.
* **Quy hoạch thư mục wiki:** Tất cả các file wiki phải sống trong `wiki/concepts/`, `wiki/entities/`, hoặc `wiki/sources/`. Không được đặt trực tiếp dưới thư mục root `wiki/`.
* **Wiki chỉ tạo SAU KHI commit:** Tuyệt đối không tạo file wiki khái niệm/thực thể mới khi đang lên kế hoạch (plan), chỉ tạo sau khi code tương ứng đã được commit và kiểm chứng.

---

### 2. Các Thao Tác Chính (Operations & Skills)

| Thao tác | Khi nào sử dụng | Skill file |
|----------|-----------------|------------|
| `ingest` | File mới xuất hiện trong `raw/` | `llmwiki/skills/wiki-loop/ingest.md` |
| `query` | Người dùng hỏi cần tổng hợp từ wiki | `llmwiki/skills/wiki-loop/query.md` |
| `lint` | Định kỳ hoặc khi wiki trông cũ | `llmwiki/skills/wiki-loop/lint.md` |
| `propose` | Yêu cầu tính năng hoặc thay đổi | `skills/dev-loop/propose.md` |
| `impact-check` | Trước khi sửa shared code | `skills/dev-loop/impact-check.md` |
| `safe-change` | Sửa code nhiều nơi gọi | `skills/dev-loop/safe-change.md` |
| `verify-before-commit` | Trước mỗi commit | `skills/dev-loop/verify-before-commit.md` |

---

### 3. Luật Gọi (Execution Guidelines)
1. **File mới trong `raw/`** $\rightarrow$ Gọi `ingest` ngay để đồng hóa tri thức.
2. **Yêu cầu tính năng mới / thay đổi kiến trúc** $\rightarrow$ Gọi `propose` trước, sau đó DỪNG lại chờ người dùng duyệt.
3. **Sửa đổi code dùng chung (shared code)** $\rightarrow$ Gọi `impact-check` để đánh giá tác động trước, sau đó thực hiện `safe-change`.
4. **Trước khi commit code** $\rightarrow$ Gọi `verify-before-commit` để đảm bảo không xảy ra hồi quy lỗi (regression).
