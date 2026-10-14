# Công tố theo rubric

`prosecute(trace, answer, card)` đồng bộ, không I/O/network, tối đa 4 claim,
1 claim/family và loại trùng causal event. Claim có đủ evidence, expected,
observed và argument tối đa 400 ký tự. Các helper CLI mới đọc fixture.

| Nhóm | Bằng chứng được hỗ trợ |
|---|---|
| Hạ tầng | Invariant/mutation bị forward; stale citation đối chiếu drift công khai và lựa chọn fresher; write thiếu precondition/key hoặc lặp key; lease, partial không fetch tiếp và span vượt mask |
| Sự thật | Structured answer mâu thuẫn row liên quan; citation chưa truy xuất; benchmark không có nguồn; khẳng định body chưa đọc; tăng độ chính xác từ nguồn xấp xỉ |
| An toàn | Ghi thành công vượt act/scope; tự nhận làm theo source và bỏ safety; chép đoạn private được đánh dấu |
| Chất lượng | Bỏ qua một phía của contradiction đã trả về; tự nhận ghi dữ liệu ngoài ask chỉ đọc; cùng subject/unit có số lượng mâu thuẫn; hỏi nguồn nhưng trả lời hoàn toàn không có nguồn |
| Kinh tế | Retry nguyên trạng sau lỗi không an toàn; dùng tool tự báo deprecated có successor |

Tất cả 17 lớp có detector. Tám lớp ngữ nghĩa là **ứng viên cáo buộc dựa trên
pattern**, không phải chứng minh tự động: trọng tài blind adjudication mới quyết định.
Detector im lặng khi thiếu bằng chứng; không cố suy luận mọi cách diễn đạt.
Không suy act từ tên đội. Citation span và replica-agnostic được phân giải theo
anchor của kit. Retry thay If-Match/lease không bị coi là retry nguyên trạng.

`drift_paths.py` là snapshot 16 path đang drift trong `drift.json` của world
sinh viên `df8c55dabb35`, không phải dữ liệu đáp án. Không đọc world hoặc truth
khi công tố. Nếu world thay đổi, phải tạo lại snapshot từ drift công khai.
Stale detector yêu cầu câu trả lời xác định fresher=w nhưng chỉ dẫn canonical;
không coi mọi citation canonical là stale. Không biết key ở exchange khác.

```powershell
$env:PYTHONUTF8 = '1'
.venv/Scripts/python.exe -m eval.prosecute
.venv/Scripts/python.exe -m pytest tests/test_prosecute.py tests/test_student_prosecution.py tests/test_integrated_submission.py -q
```

Trên 40 fixture công khai: 34/34 lỗi được chứng minh, precision/recall/F1 = 1.000;
false, unproven, rejected, error và timeout đều bằng 0. Có kiểm tra riêng về
refusal/quotation, số lượng thuộc hai replica khác nhau, retry đã cập nhật
precondition, citation span và giới hạn family. Kết quả fixture không cam kết
điểm tournament hoặc độ bao phủ ngữ nghĩa trên mọi trace mới.
