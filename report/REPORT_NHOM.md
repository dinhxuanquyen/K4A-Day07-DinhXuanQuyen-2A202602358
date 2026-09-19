# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** MegaLive
**Thành viên:** Hà Huy Nhất (2A202602401), Đinh Xuân Quyền (2A202602358), Ngụy Quang Hùng (2A202602998), Nguyễn Văn Việt(2A202602904)
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán...) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ, chính sách và quy định dành cho sinh viên/trường đại học Công Nghệ - ĐHQGHN (UET).

**Tại sao nhóm chọn chủ đề này?**

> Nhóm chọn chủ đề này vì dữ liệu phù hợp ràng buộc của lớp L3A: các câu hỏi đều xoay quanh học phí, học bổng, điểm rèn luyện, thủ tục chính sách, trao đổi sinh viên và tuyển dụng trong bối cảnh đại học. Bộ tài liệu có cấu trúc tương đối rõ, có metadata `audience`, `category`, `department`, giúp kiểm thử cả retrieval ngữ nghĩa lẫn lọc metadata.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu                                                                   | Nguồn (Source URL)                                                                                        | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán                                                                                                                                     |
| - | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | Quy định học bổng sinh viên                                                  | https://handbook.uet.vnu.edu.vn/hoc-bong                                                                   | 2026-09-19 / not-stated  | 2140        | `doc_id=hoc-bong`, `audience=student`, `department=academic-affairs`, `category=scholarship`, `language=vi`                                  |
| 2 | Quy định học phí                                                              | https://handbook.uet.vnu.edu.vn/hoc-phi                                                                    | 2026-09-19 / not-stated  | 2312        | `doc_id=hoc-phi`, `audience=student`, `department=acadamic-affairs`, `category=tuition`, `language=vi`                                       |
| 3 | UET Job Fair 2026                                                                 | https://vieclam.uet.vnu.edu.vn/ngay-hoi-viec-lam-truong-dai-hoc-cong-nghe-uet-job-fair-2026-ht058595484436 | 2026-09-19 / not-stated  | 28296       | `doc_id=ngay-hoi-viec-lam`, `audience=student`, `department=acadamic-event`, `category=event`, `language=vi`                                 |
| 4 | Hướng dẫn thủ tục hồ sơ miễn giảm học phí cho sinh viên khóa QH-2026 | https://uet.edu.vn/huong-dan-thu-tuc-ho-so-mien-giam-hoc-phi-cho-sinh-vien-khoa-qh-2026/                   | 2026-09-19 / not-stated  | 7135        | `doc_id=thu-tuc-mien-giam-hoc-phi`, `audience=student`, `department=acadamic-procedure`, `category=administrative procedures`, `language=vi` |
| 5 | Chương trình trao đổi sinh viên tại Đại học Kanazawa, Nhật Bản        | https://uet.edu.vn/chuong-trinh-trao-doi-sinh-vien-tai-dai-hoc-kanazawa-nhat-ban-3/                        | 2026-09-19 / not-stated  | 6925        | `doc_id=trao-doi-sinh-vien-kanazawa`, `audience=student`, `department=acadamic-affairs`, `category=student exchange`, `language=vi`          |
| 6 | Tuyển dụng giảng viên, trợ giảng cho các Khoa, Viện thuộc Trường       | https://uet.edu.vn/tuyen-dung-giang-vien-tro-giang-cho-cac-khoa-vien-thuoc-truong/                         | 2026-09-19 / not-stated  | 4500        | `doc_id=tuyen-dung`, `audience=lecturer`, `department=acadamic-procedure`, `category=recruitment`, `language=vi`                             |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [X] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [X] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu       | Ví dụ giá trị                           | Tại sao hữu ích cho truy xuất (retrieval)?                                                                  |
| -------------------- | ----------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `doc_id`           | string      | `hoc-phi`                                 | Định danh tài liệu gốc, dùng để truy vết chunk và xóa toàn bộ chunk của một tài liệu.          |
| `title`            | string      | `Quy định học phí`                    | Giúp đọc kết quả top-k nhanh hơn và đối chiếu với gold answer.                                       |
| `source_url`       | string      | `https://handbook.uet.vnu.edu.vn/hoc-phi` | Cho phép kiểm tra nguồn và provenance của câu trả lời.                                                  |
| `retrieved_at`     | date/string | `2026-09-19`                              | Biết thời điểm nhóm thu thập tài liệu, hữu ích khi quy định thay đổi.                             |
| `document_version` | string      | `not-stated`                              | Ghi nhận phiên bản/ngày hiệu lực nếu nguồn có nêu; nếu không có thì minh bạch là`not-stated`. |
| `audience`         | string      | `student`, `lecturer`                   | Cho phép lọc tài liệu dành cho sinh viên hoặc giảng viên trước khi search.                           |
| `department`       | string      | `academic-affairs`                        | Hỗ trợ phân loại theo phòng ban/mảng nghiệp vụ.                                                         |
| `category`         | string      | `tuition`, `scholarship`                | Lọc hoặc phân tích lỗi theo chủ đề tài liệu.                                                          |
| `language`         | string      | `vi`                                      | Đảm bảo query tiếng Việt được so với corpus tiếng Việt.                                              |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu chính với `chunk_size=500`:

| Tài liệu                       | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                                                    |
| -------------------------------- | ---------------------------------- | ----------------- | --------------------- | ---------------------------------------------------------------------------------- |
| `hoc-phi.md`                   | FixedSizeChunker (`fixed_size`)  | 6                 | 427.0                 | Trung bình; có overlap nhưng vẫn có thể cắt giữa ý.                       |
| `hoc-phi.md`                   | SentenceChunker (`by_sentences`) | 10                | 228.2                 | Tốt ở mức câu, nhưng đôi khi chunk ngắn và thiếu bối cảnh.             |
| `hoc-phi.md`                   | RecursiveChunker (`recursive`)   | 6                 | 383.7                 | Tốt hơn vì ưu tiên đoạn/dòng/câu trước khi cắt nhỏ.                   |
| `hoc-bong.md`                  | FixedSizeChunker (`fixed_size`)  | 5                 | 468.0                 | Khá ổn vì tài liệu ngắn, nhưng vẫn có rủi ro cắt ngang mục.            |
| `hoc-bong.md`                  | SentenceChunker (`by_sentences`) | 8                 | 265.0                 | Dễ đọc, phù hợp với câu hỏi điểm rèn luyện cụ thể.                   |
| `hoc-bong.md`                  | RecursiveChunker (`recursive`)   | 6                 | 355.0                 | Cân bằng giữa độ dài chunk và tính mạch lạc.                             |
| `thu-tuc-mien-giam-hoc-phi.md` | FixedSizeChunker (`fixed_size`)  | 16                | 492.8                 | Dễ tạo chunk đều nhưng cắt bảng/hồ sơ giữa chừng.                       |
| `thu-tuc-mien-giam-hoc-phi.md` | SentenceChunker (`by_sentences`) | 18                | 393.9                 | Giữ câu tốt nhưng danh sách hồ sơ dài có thể tách rời tiêu đề.      |
| `thu-tuc-mien-giam-hoc-phi.md` | RecursiveChunker (`recursive`)   | 17                | 417.1                 | Phù hợp nhất trong baseline vì giữ được khối văn bản theo đoạn/dòng. |

### Chiến lược của từng thành viên

**Thành viên 1 — Hà Huy Nhất**

- **Loại chiến lược:** FixedSizeChunker + Gemini embedding.
- **Mô tả & lý do chọn cho chủ đề này:** Dùng `FixedSizeChunker(chunk_size=500, overlap=50)` để có baseline ổn định, dễ tái lập và dễ so sánh với các chiến lược khác. Overlap 50 ký tự giúp giảm mất ngữ cảnh ở ranh giới chunk, nhưng kết quả cho thấy một số câu trả lời đúng nằm ở top-2/top-3 vì chunk bị cắt chưa theo đúng ranh giới mục.
- **Code snippet (nếu custom):**

```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

**Thành viên 2 — Đinh Xuân Quyền**

- **Loại chiến lược:** SentenceChunker + OpenAI embedding.
- **Mô tả & lý do chọn:** Thành viên này dùng `SentenceChunker` để giữ nguyên ranh giới câu, phù hợp với các câu hỏi có đáp án ngắn và trực tiếp như “Cảnh cáo tối đa loại Trung bình” hoặc “Xuất sắc: 90 - 100 điểm”. Kết quả truy xuất đạt 5/5 câu có chunk liên quan; các câu hỏi về học phí, kỷ luật, điểm rèn luyện và ưu tiên sinh viên khuyết tật đều được trả lời đúng từ top-k.
- **Code snippet (nếu custom):**

```python
chunker = SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Ngụy Quang Hùng**

- **Loại chiến lược:** Recursive chunking cho câu hỏi chính sách ngắn + Gemini embedding.
- **Mô tả & lý do chọn:** Thành viên này dùng `RecursiveChunker`, trong đó retrieval tập trung vào các câu trả lời ngắn, rõ ràng như “Hệ Chuẩn thu theo tín chỉ”, “Cảnh cáo tối đa loại Trung bình”, “Xuất sắc: 90 - 100 điểm”. Cách này phù hợp với bộ câu hỏi benchmark vì phần lớn đáp án nằm trong một hoặc vài câu liên tiếp.
- **Code snippet (nếu custom):**

```python
recursive_chunker = RecursiveChunker(chunk_size=300)
```

**Thành viên 4 — Nguyễn Văn Việt**

- **Loại chiến lược:** HeadingChunker + metadata/source-aware RAG.
- **Mô tả & lý do chọn:** Thành viên này dùng `HeadingChunker` để giữ nội dung theo các heading/mục của tài liệu, phù hợp với văn bản quy định có cấu trúc như “Học phí”, “Điểm rèn luyện”, “Kỷ luật”, “Đối tượng đặc thù”. Thành viên này cũng bổ sung nguồn/metadata trong prompt để câu trả lời có thể truy vết, và kết quả benchmark đạt 5/5 câu có chunk liên quan trong top-3.
- **Code snippet (nếu custom):**

```python
chunker = HeadingChunker()
```

### So Sánh Giữa Các Thành Viên

| Thành viên       | Chiến lược (Strategy)                                | Điểm truy xuất (/10) | Điểm mạnh                                                                                               | Điểm yếu                                                                                                      |
| ------------------ | ------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Hà Huy Nhất      | FixedSize,`chunk_size=500`, `overlap=50` +  Gemini | 9/10                    | Dễ triển khai, ổn định, 5/5 câu có chunk liên quan trong top-3.                                    | Một số câu đúng nằm ở top-2/top-3 vì cắt chưa theo cấu trúc mục.                                    |
| Đinh Xuân Quyền | SentenceChunker, OpenAI                                 | 9/10                    | Giữ nguyên câu chứa đáp án, rất tốt với các câu hỏi có câu trả lời ngắn và trực tiếp. | Có thể thiếu tiêu đề/mục cha nếu một câu cần thêm bối cảnh từ heading.                            |
| Ngụy Quang Hùng  | Recursive Chunking + Gemini                            | 10/10                   | Phù hợp với câu hỏi ngắn, nhiều đáp án nằm trực tiếp trong một câu hoặc một mục nhỏ.    | Một số mô tả chiến lược trong report còn chung, chưa tách rõ cấu hình chunking cuối cùng.         |
| Nguyễn Văn Việt | HeadingChunker + metadata/source-aware prompt           | 10/10                   | Giữ tốt cấu trúc mục của tài liệu quy định, có truy vết nguồn tốt.                           | Phụ thuộc chất lượng heading; nếu tài liệu crawl bẩn hoặc thiếu heading thì cần làm sạch trước. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Nhóm đánh giá `HeadingChunker` và `RecursiveChunker` là phù hợp nhất với tài liệu quy định đại học. Các tài liệu như `hoc-bong`, `hoc-phi`, `thu-tuc-mien-giam-hoc-phi` có cấu trúc theo mục, nên giữ nguyên khối dưới cùng tiêu đề hoặc đoạn giúp chunk vừa có đáp án vừa có ngữ cảnh. `SentenceChunker` cũng hiệu quả với câu hỏi có đáp án ngắn, còn fixed size là baseline dễ tái lập nhưng đôi khi đưa chunk đúng xuống top-2/top-3.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query)                                                                               | Câu trả lời chuẩn (Gold Answer)                                                                                         | Chunk nào chứa thông tin?                                                                                 |
| - | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 1 | Sinh viên hệ Chuẩn phải đóng học phí theo hình thức nào?                             | Hệ Chuẩn thu học phí theo tín chỉ; mức thu thay đổi từng năm theo Nghị định của Chính phủ.                 | `hoc-phi`, phần “1. Học phí học lần đầu”.                                                         |
| 2 | Khi nào sinh viên bị kỷ luật Cảnh cáo thì Điểm rèn luyện tối đa là bao nhiêu?   | Khi bị kỷ luật Cảnh cáo, điểm rèn luyện tối đa là loại Trung bình.                                            | `hoc-bong`, phần “3. Lưu ý quan trọng về Kỷ luật”.                                                |
| 3 | Sinh viên người dân tộc thiểu số thuộc hộ nghèo được miễn giảm học phí ra sao? | Sinh viên dân tộc thiểu số thuộc hộ nghèo/cận nghèo thuộc diện miễn 100% học phí theo tài liệu`hoc-phi`. | `hoc-phi`, phần “Miễn 100% Học phí”; `thu-tuc-mien-giam-hoc-phi`, phần đối tượng và hồ sơ. |
| 4 | Để đạt điểm rèn luyện loại xuất sắc cần bao nhiêu điểm?                          | Cần đạt từ 90 đến 100 điểm.                                                                                         | `hoc-bong`, phần “2. Phân loại kết quả”.                                                            |
| 5 | Sinh viên khuyết tật có được ưu tiên điểm rèn luyện không?                        | Có. Sinh viên khuyết tật/hoàn cảnh đặc biệt có cơ chế cộng điểm ưu tiên sự nỗ lực.                      | `hoc-bong`, phần “4. Đối tượng đặc thù”.                                                         |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi                                                           | Chiến lược tốt nhất cho câu này     | Có chunk liên quan trong top-3? | Ghi chú                                                                                                              |
| - | ------------------------------------------------------------------- | ------------------------------------------ | --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 1 | Sinh viên hệ Chuẩn phải đóng học phí theo hình thức nào? | FixedSize / Recursive / Heading đều tốt | Có                               | `hoc-phi` thường lên top-1; đáp án ngắn và nằm gần đầu tài liệu.                                      |
| 2 | Kỷ luật Cảnh cáo thì ĐRL tối đa bao nhiêu?                 | HeadingChunker hoặc SentenceChunker       | Có                               | Câu trả lời nằm trong mục kỷ luật và cũng là một câu rõ ràng.                                           |
| 3 | Sinh viên DTTS hộ nghèo được miễn giảm học phí ra sao?    | Recursive hoặc HeadingChunker             | Có                               | FixedSize có lúc đưa chunk giảm 70% lên top-1, nhưng top-2 vẫn chứa đáp án miễn 100%.                    |
| 4 | Đạt điểm rèn luyện loại xuất sắc cần bao nhiêu điểm?   | SentenceChunker hoặc Recursive            | Có                               | Đáp án nằm trong một câu rõ ràng: “Xuất sắc: 90 - 100 điểm”.                                            |
| 5 | Sinh viên khuyết tật có được ưu tiên ĐRL không?          | HeadingChunker hoặc SentenceChunker       | Có                               | Heading giữ mục “Đối tượng đặc thù”; Sentence giữ đúng câu “Có cơ chế cộng điểm ưu tiên...”. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có. Vì corpus có cả tài liệu dành cho `audience=student` và `audience=lecturer`, nhóm dùng `metadata_filter={"audience": "student"}` cho các câu hỏi chính sách sinh viên để tránh tài liệu tuyển dụng giảng viên chen vào top-k. Lọc metadata đặc biệt hữu ích với câu 1, 3 và 5 vì đều hỏi quyền lợi/quy định dành cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> - Cùng một bộ tài liệu nhưng embedding backend và chiến lược chunking làm kết quả khác nhau rõ rệt; mock embedding chỉ phù hợp cho test, không phù hợp đánh giá retrieval thực tế.
> - Fixed size là baseline dễ chạy nhưng không hiểu cấu trúc tài liệu, trong khi `RecursiveChunker` và `HeadingChunker` giữ mục quy định tốt hơn.
> - Data cleaning rất quan trọng: `ngay-hoi-viec-lam.md` tạo nhiều chunk nhiễu, dễ chiếm top-k nếu dùng embedding yếu hoặc không lọc metadata.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng data `university-uet`, các chiến lược đều đạt 5/5 câu có chunk liên quan trong top-3 khi dùng embedding thật, nhưng chất lượng top-1 khác nhau. `HeadingChunker` giữ được cấu trúc mục, `SentenceChunker` tốt với đáp án ngắn, còn fixed size cần overlap và đôi khi vẫn đẩy chunk chứa gold answer xuống top-2/top-3.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ làm sạch mạnh hơn tài liệu `ngay-hoi-viec-lam.md`, loại bỏ danh sách việc làm quá dài không phục vụ benchmark chính sách sinh viên. Nhóm cũng sẽ chuẩn hóa lại một số metadata bị viết sai như `acadamic` thành `academic`, đồng thời thêm metadata `section_heading` cho từng chunk để lọc theo mục như “Học phí”, “Điểm rèn luyện”, “Kỷ luật”.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10                |
| Thiết kế chiến lược (Strategy Design)   | 15 / 15                |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10                |
| Thuyết trình (Demo)                        | 5 / 5                  |
| **Tổng phần nhóm**                  | **40 / 40**      |
