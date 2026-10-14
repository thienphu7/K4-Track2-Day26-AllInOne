# Role 2 — Bộ bài và lineup

Giữ 14 lá: 10 attack + 4 blank, các lớp/layer và anchor thật của starter.

`atk_10` trước đây hỏi định nghĩa nhưng nhắm `roster`, một peer không cần cho
câu hỏi đó. Nay hỏi ngày học của `Concept:stategraph/w/055`, nhắm
`a2a:curriculum-analyst`, và thay audience thành `a2a:roster`. Câu hỏi làm peer
bị nhắm có liên quan trực tiếp; token vẫn có thể có chữ ký hợp lệ nhưng sai
nơi nhận. Trigger giữ call_index >=2 để đánh sau các lệnh dò tìm đầu tiên.

Lineup mở bằng `blk_01`, bench `atk_05` schema_bomb. Đây là tradeoff: bỏ một
attack phụ thuộc đối thủ mở catalog để thử phản ứng trên yêu cầu sạch, giữ
các đòn identity ở vòng 9–10 (scale 1.5). Deck vẫn chứa schema_bomb để giữ
độ phủ và có thể chọn lại sau khi quan sát đối thủ. Blank không tự tạo sát
thương; chỉ có ích khi đối thủ phản ứng sai. Chưa chứng minh lineup này tối
ưu trên mọi đối thủ.

Giữ nguyên defense_event thực tế của starter (`registry.pinned`,
`guardrail.refused`, `gateway.budget_held`, `a2a.crosschecked`) ở các đòn tương
ứng. Tài liệu starter có đoạn cũ yêu cầu mọi card dùng gateway.denied; code
hiện tại phân biệt cơ chế phòng thủ. Không đổi metadata để biến một lỗi nội
dung thành enforcement_failure giả.

```bash
make validate
make spar BOT=rookie AS=all
make spar BOT=operator AS=all
make spar BOT=adversary AS=all
```

Validator trên world chính thức: 0 FAIL, 5 WARN (giới hạn kiểm tra lethality và
bốn defense_event phi-denial đã có từ starter). Spar là mô phỏng plan dựng sẵn;
không xác nhận chất lượng prompt hay tác dụng mọi mutation trong tournament.
