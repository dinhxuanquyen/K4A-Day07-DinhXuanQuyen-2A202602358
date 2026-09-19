# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đinh Xuân Quyền
**Nhóm:** Megalive
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Viết 1-2 câu:* Nó có nghĩa là hai vector nhúng (embedding) đang hướng về cùng một phía trong không gian đa chiều, thể hiện hai đoạn văn bản có ý nghĩa ngữ nghĩa (semantic meaning) rất giống nhau hoặc liên quan chặt chẽ với nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: Thời tiết hôm nay mưa to và có gió lớn.
- Câu B: Hôm nay trời mưa bão dữ dội.
- Tại sao tương đồng: Cả hai đều mô tả tình trạng thời tiết xấu, có mưa, chung một chủ đề ngữ nghĩa.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Tôi đang code thuật toán Python.
- Câu B: Quả táo này rất ngọt.
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (Công nghệ thông tin và Trái cây), không có điểm chung nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Viết 1-2 câu:* Cosine similarity chỉ quan tâm đến góc (hướng) giữa hai vector chứ không quan tâm đến độ lớn (magnitude). Nhờ vậy, một câu ngắn và một câu dài (nhưng có cùng ý nghĩa) vẫn cho độ tương tự cao, trong khi khoảng cách Euclid sẽ bị sai lệch nhiều do chênh lệch độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:* Số lượng = làm_tròn_lên((10,000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên (cụ thể: ceil(9900/400) = 25 chunks). Ta muốn độ chồng chéo nhiều hơn để tránh việc cắt ngang một ý tưởng hay một câu đang dang dở, giúp ngữ cảnh giữa các đoạn (chunk) được liền mạch và không bị mất mát thông tin ở phần giáp ranh.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Sử dụng regex `(?<=[.!?])\s+` (Lookbehind) để tách câu ngay tại khoảng trắng sau các dấu kết thúc câu mà không làm mất dấu câu đó. Xử lý ngoại lệ bằng `s.strip()` để bỏ khoảng trắng thừa và bỏ qua các câu trống, sau đó gộp lại theo `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Thuật toán đệ quy thử cắt theo từng separator. Base case là khi chuỗi đã ngắn hơn `chunk_size` hoặc hết separator. Nếu một phần (part) dài hơn `chunk_size`, nó sẽ tự động đệ quy cắt tiếp bằng các separator còn lại, cuối cùng gộp (merge) lại khéo léo để tối ưu dung lượng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Hỗ trợ lưu trữ trực tiếp vào danh sách `_store` trong RAM hoặc nạp vào ChromaDB. Hàm search tính Dot Product (tích vô hướng) giữa câu hỏi và các record, gán điểm (score) và sắp xếp giảm dần để trả về Top-K.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Lọc (filter) luôn được thực hiện TRƯỚC khi tính toán similarity để giảm không gian tìm kiếm và đảm bảo độ chính xác của điều kiện. Xóa document bằng cách tạo list comprehension mới chỉ chứa các record có `doc_id` khác với id truyền vào.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Cấu trúc prompt gồm phần Lệnh, Ngữ cảnh và Câu hỏi. Ngữ cảnh (context) được lấy từ hàm search của store, đem nối lại thành chuỗi rõ ràng với đánh dấu phân cách (VD: `--- Chunk X ---`) giúp LLM dễ đọc hiểu để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.2, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\DELL\Desktop\K4A-Day07-DinhXuanQuyen-2A202602358
plugins: anyio-4.15.1, langsmith-0.13.0, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.10s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                                          | Câu B                                                                        | Dự đoán | Điểm thực tế | Đúng? |
| ---- | --------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------- | ---------------- | ------- |
| 1    | Sinh viên phải nộp học phí qua tài khoản ngân hàng.    | Trường yêu cầu đóng tiền học bằng phương thức chuyển khoản.     | cao        | 0.667            | Đúng  |
| 2    | Sinh viên phải nộp học phí qua tài khoản ngân hàng.    | Thư viện trường mở cửa từ 8h sáng đến 5h chiều.                    | thấp      | 0.353            | Đúng  |
| 3    | Học bổng khuyến khích học tập dành cho sinh viên giỏi. | Sinh viên có thành tích học tập xuất sắc sẽ được xét học bổng. | cao        | 0.638            | Đúng  |
| 4    | Hỗ trợ miễn giảm học phí cho sinh viên hộ nghèo.       | Hỗ trợ miễn giảm học phí cho sinh viên dân tộc thiểu số.           | cao        | 0.757            | Đúng  |
| 5    | Chương trình trao đổi sinh viên tại trường Kanazawa.   | Hướng dẫn thủ tục đăng ký ở ký túc xá.                            | thấp      | 0.297            | Đúng  |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Cặp 4 bất ngờ nhất với điểm số cực cao (0.757) dù hai đối tượng hưởng chính sách (hộ nghèo và dân tộc thiểu số) hoàn toàn khác nhau. Điều này cho thấy Embeddings (OpenAI) nắm bắt rất mạnh bối cảnh chung là "chính sách hỗ trợ miễn giảm học phí", chứ không chỉ so khớp từ khóa. Embeddings thực sự biểu diễn được "ngữ nghĩa" đằng sau văn bản!

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query)                                                                               | Top-1 Chunk truy xuất được (tóm tắt)                                                            | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                        |
| - | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------ | --------------------------------- | ---------------------------------------------------------------------------- |
| 1 | Sinh viên hệ Chuẩn phải đóng học phí theo hình thức nào?                             | Quy định học phí Học phí & chính sách Học phí - Chế độ...                                | 0.712        | Có                               | Sinh viên hệ Chuẩn đóng học phí theo hình thức thu theo tín chỉ.  |
| 2 | Khi nào sinh viên bị kỷ luật Cảnh cáo thì Điểm rèn luyện tối đa là bao nhiêu?   | Kỷ luật Cảnh cáo: ĐRL tối đa loại Trung bình. Kỷ luật Đình chỉ: Không đánh giá...   | 0.478        | Có                               | Điểm rèn luyện tối đa loại Trung bình.                               |
| 3 | Sinh viên người dân tộc thiểu số thuộc hộ nghèo được miễn giảm học phí ra sao? | Sinh viên là người dân tộc thiểu số có cha mẹ hoặc ông bà...                             | 0.755        | Có                               | Được miễn giảm theo quy định của Thủ tướng, nộp đơn theo mẫu. |
| 4 | Để đạt điểm rèn luyện loại xuất sắc cần bao nhiêu điểm?                          | Điểm cơ sở: 70 điểm (dành cho SV không vi phạm quy chế), sau đó cộng/trừ điểm...      | 0.480        | Có                               | Cần từ 90 đến 100 điểm.                                                |
| 5 | Sinh viên khuyết tật có được ưu tiên điểm rèn luyện không?                        | Sinh viên khuyết tật, hoàn cảnh đặc biệt: Có cơ chế cộng điểm ưu tiên sự nỗ lực... | 0.570        | Có                               | Có, sinh viên khuyết tật được ưu tiên điểm rèn luyện.           |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (Kết quả xuất sắc khi dùng OpenAI!)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua quá trình làm việc nhóm, em nhận thấy việc lựa chọn chiến lược Chunking phù hợp với định dạng văn bản (ví dụ: dùng HeadingChunker cho văn bản có cấu trúc thay vì cắt đệ quy) giúp bảo toàn ngữ nghĩa tốt hơn hẳn. Đồng thời, việc sử dụng Metadata để lọc đối tượng (student/lecturer) trước khi search là chìa khóa để tránh hiện tượng AI bị "nhiễu" bởi các quy định không liên quan.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                |
| **Tổng phần cá nhân**                      | **60 / 60**      |
