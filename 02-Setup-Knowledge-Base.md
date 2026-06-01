# CONTEXT
Đã có mục tiêu và stack. Giờ phải dựng kho tri thức — nơi lưu mọi thứ dự án biết.

3 lớp:
- **`raw/`** — tài liệu gốc. Con người viết, bot KHÔNG BAO GIỜ đụng.
- **`wiki/`** — bot tự duy trì: khái niệm, thực thể, nguồn tham khảo.
- **`AGENT.md`** — luật chơi: cấu trúc, cách hoạt động, 3 thao tác chính (ăn, hỏi, dọn).

# PHẢI LÀM

**QUAN TRỌNG:** Đừng tạo file `.md` lung tung ở root. Chỉ được có `AGENT.md`, `README.md`, và file số (`01-*.md`, `02-*.md`).

1. Tạo thư mục ở root:
   - `skills/` — workflow nhiều bước bot tự chạy (vd: `propose`, `safe-change`).
   - `commands/` — lệnh người dùng gọi trực tiếp (vd: `scaffold-feature`).
   - `html/` — dashboard, báo cáo trực quan.

2. Tạo `raw/` — **nguyên liệu gốc**:
   - Con người bỏ tài liệu vào đây: spec, meeting notes, docs, ảnh, data.
   - Bot KHÔNG viết, KHÔNG sửa, KHÔNG xóa gì trong `raw/`.
   - Bot chỉ đọc `raw/` khi thực hiện thao tác `ingest`.

3. Tạo `wiki/` — **kho tri thức**. Chọn subfolder theo bảng:

   | Subfolder | Khi nào | Ví dụ |
   |-----------|---------|-------|
   | `concepts/` | Khái niệm trừu tượng, pattern, thuật ngữ domain | `rag.md`, `graph-memory.md` |
   | `entities/` | Cụ thể trong hệ thống: service, API, tool, component | `caveman.md`, `neo4j.md` |
   | `sources/` | Tài liệu tham khảo, quyết định kỹ thuật từ `raw/` | `why-neo4j.md`, `caveman-docs.md` |
   | `sources/draft/` | Proposal chưa làm (skill `propose` tạo) | `260425-new-approval-button-fe.md` |

   Mỗi file wiki phải theo format:
   ```
   # <Tiêu đề>
   **Type:** concept | entity | source
   **Tags:** tag1, tag2

   <1-3 câu mô tả>

   ## Notes
   <chi tiết, [[wikilinks]] tới entry liên quan>

   ## Origin
   - **Source:** raw/<filename> | wiki/sources/draft/<filename> | https://...
   - **Commit:** <hash>
   - **Date:** YYYY-MM-DD
   ```
   File không có `## Origin` = chưa xong.

4. Tạo `wiki/index.md`:
   ```
   # Wiki Index
   | File | Type | Summary |
   |------|------|---------|
   ```
   Thêm mỗi lần tạo/xóa file.

5. Tạo `wiki/log.md`:
   ```
   # Operation Log
   ## YYYY-MM-DD — <operation: ingest | query | lint | init> — <summary>
   - <detail>
   ```
   Ghi lần khởi tạo đầu tiên.

6. Tạo `AGENT.md` ở root:

   **Luật:**
   - KHÔNG BAO GIỜ ghi vào `raw/`
   - LUÔN cập nhật `wiki/index.md` khi thêm/xóa file wiki
   - LUÔN append `wiki/log.md` sau mỗi thao tác
   - Dùng `[[wikilinks]]` để link giữa các trang
   - File wiki sống trong `concepts/`, `entities/`, hoặc `sources/` — không được ở root `wiki/`
   - Wiki chỉ tạo SAU KHI code đã commit — không tạo lúc đang lên plan

   **3 thao tác chính** (đọc skill trước khi chạy):

   | Thao tác | Khi nào | Skill file |
   |----------|---------|------------|
   | `ingest` | File mới xuất hiện trong `raw/` | `llmwiki/skills/wiki-loop/ingest.md` |
   | `query` | Người dùng hỏi cần tổng hợp từ wiki | `llmwiki/skills/wiki-loop/query.md` |
   | `lint` | Định kỳ hoặc khi wiki trông cũ | `llmwiki/skills/wiki-loop/lint.md` |
   | `propose` | Yêu cầu tính năng hoặc thay đổi | `skills/dev-loop/propose.md` |
   | `impact-check` | Trước khi sửa shared code | `skills/dev-loop/impact-check.md` |
   | `safe-change` | Sửa code nhiều nơi gọi | `skills/dev-loop/safe-change.md` |
   | `verify-before-commit` | Trước mỗi commit | `skills/dev-loop/verify-before-commit.md` |

   **Luật gọi:**
   - File mới trong `raw/` → gọi `ingest` ngay
   - Yêu cầu tính năng → gọi `propose` trước, dừng, chờ duyệt
   - Sửa shared code → gọi `impact-check` rồi `safe-change`
   - Trước mỗi commit → gọi `verify-before-commit`

7. Quét root tìm file `.md` lạ (không phải `AGENT.md`, `README.md`, `01-*.md`, `02-*.md`...):
   - Nếu có: phân loại concept/entity/source, chuyển vào đúng subfolder `wiki/`, thêm vào `index.md`, ghi `log.md`.
   - Nếu không: bỏ qua.

# LÀM ĐI
Mỗi mục trên:
- Chưa có → tạo đúng như mô tả.
- Đã có → kiểm tra đúng format chưa. Thiếu gì thì sửa phần đó, đừng overwrite nội dung cũ.

Trả về checklist: ✅ (đúng rồi), 🔧 (tạo mới/sửa), ❌ (không tạo được + lý do).
