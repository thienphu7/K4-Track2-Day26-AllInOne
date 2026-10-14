# Role 1 — Phòng thủ

`gateway.py` là điểm thực thi cho MCP/A2A/DISCOVER, đồng bộ và không I/O.

- Chặn server/tool hoặc field mask không thuộc bảng `TOOL_SPECS`.
- Chuyển `slides.search` sang `slides.query`, chuyển mask tương ứng; thu hẹp catalog rộng.
- Định tuyến bằng header, giữ replica được chỉ định hợp lệ; không đoán canonical luôn mới hơn.
- Kiểm tra learner theo `ctx.act`, độc lập với quyền của `ctx.sub`.
- Kiểm tra read/write scope, lease sống từ context, If-Match, key ghi duy nhất.
- Chỉ cho ghi với provenance khớp trong vòng hiện tại; tiêu thụ provenance sau khi cho phép ghi.
- Kiểm tra card/skill/audience; card có chữ ký được xác minh bằng `verify_card`.
- Ánh xạ skill `role_of`/`who_enrolled` của roster sang wire tool `lookup_learner`.
- Từ chối header trùng tên sau khi chuẩn hóa chữ thường và anchor của learner khác.
- Khi có signed delegation, kiểm tra chữ ký, act, audience, expiry và replay.
- Giới hạn cửa sổ rate và dự toán chi phí; giữ 5 credit cho mỗi vòng còn lại.

Caller tin cậy phải đưa quan sát registry vào `note_card(server, card)` và
`note_provenance(anchor, etag)`. Compact card `{verified, skills}` chỉ dành cho
adapter tin cậy của harness, không lấy từ nội dung model hoặc command.
Gateway không thấy kết quả của lệnh đang quyết định; các mutation sau khi tool
chạy phải được kiểm tra tại phía nhận kết quả, không thể chặn bằng dấu hiệu
chỉ tồn tại trên outgoing command.

`guardrails.py` cung cấp kiểm tra grounding, tín hiệu injection, che fragment
riêng tư do caller cung cấp, che secret assignment và kiểm tra phương trình
số học đơn giản. `prepare_answer` kiểm tra citation, required fields, số học và
nội dung riêng tư, trả abstention khi không đủ bằng chứng an toàn. **Caller
lắp ráp ANSWER phải gọi helper này**; bộ kit không có callback ANSWER cho gateway.
Kiểm tra phương trình không chứng minh số liệu đúng với nguồn. Pattern injection
không thay thế việc đọc hiểu và không bảo đảm phát hiện mọi cách diễn đạt.

`strategy.py` và `telemetry.py` giữ nguyên helper có sẵn; gateway sử dụng helper
successor/catalog trong strategy. Telemetry chỉ phục vụ quan sát nội bộ.

```bash
.venv/bin/python -m pytest tests/test_student_defense.py -q
.venv/bin/python -m agent.gateway
make spar BOT=operator AS=defender
```

Spar dùng tool plan và ANSWER dựng sẵn, không chạy `prompt.md`/`prepare_answer`.
Chi phí dự toán có thể khác số hàng thực tế; `ctx.credits` là số dư có thẩm quyền.

Kết quả kiểm thử và ranh giới bàn giao: xem `agent/VALIDATION.md`.
