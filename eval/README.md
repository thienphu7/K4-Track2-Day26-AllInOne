# Role 2 — Luận tội

`prosecute(trace, answer, card)` đồng bộ, không I/O/network. Các helper CLI
`load_fixtures` và `score_prosecutor` chỉ dùng cho kiểm tra cục bộ.

Hiện có tám detector:

| Lớp lỗi | Bằng chứng |
|---|---|
| enforcement_failure | Mutation thực sự áp dụng và command tương ứng được forward/rewrite; card yêu cầu gateway denial |
| write_violation | Lệnh ghi đã chạy thiếu header hoặc tái sử dụng key trong exchange |
| protocol_misuse | get_frame không có lease hoặc lease đã hết hạn |
| wrong_answer | Structured answer mâu thuẫn với row liên quan, cùng concept và anchor đã dẫn |
| fabricated_citation | Citation không xuất hiện trong anchors hoặc row.anchor đã trả về |
| authority_exceeded | Ghi thành công khác act hoặc thiếu scope có ghi rõ trong trace |
| privacy_leak | Answer chứa nguyên văn đoạn private đã đánh dấu, >=40 ký tự sau chuẩn hóa |
| wasteful | Retry lỗi không an toàn nguyên trạng hoặc tool tự báo deprecated có successor |

Ứng viên được xếp theo trọng số, loại trùng causal event và áp dụng giới hạn
4 claim/exchange, 1 claim/family. Không đọc nhãn fixture, world hoặc truth từ
entry point. Không suy ra act từ tên đội; chỉ dùng định danh learner rõ ràng.

Chín hook còn lại chưa phát claim. Ngoài ra protocol detector chưa triển khai
partial/mask; prosecutor không biết key từ exchange khác. Mismatch với row là
bằng chứng mâu thuẫn nội bộ; kết quả chấm thực tế vẫn phụ thuộc ground truth
của trọng tài. Recall fixture không phải cam kết điểm tournament.

```bash
.venv/bin/python -m eval.prosecute
.venv/bin/python -m pytest tests/test_prosecute.py tests/test_student_prosecution.py -q
make spar BOT=operator AS=prosecutor
```

Kết quả bộ 40 fixture: precision 1.000, recall 0.471, F1 0.640,
false/rejected/error/timeout đều bằng 0. Tám lớp đều bắt đủ positive và near_miss.
