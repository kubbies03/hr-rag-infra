# Changelog — HR RAG Chatbot

## Tối ưu hiệu năng & sửa lỗi

### `app/core/config.py`
- `CHUNK_SIZE`: 1000 → **500** — chunk nhỏ hơn, retrieval chính xác hơn
- `CHUNK_OVERLAP`: 150 → **75** — giữ tỷ lệ 15%
- `RETRIEVAL_CANDIDATE_K`: 10 → **5** — reranker xử lý ít cặp hơn, nhanh hơn
- `RETRIEVER_TOP_K`: 3 → **2** — context truyền vào Gemini ngắn hơn
- `MAX_CONVERSATION_HISTORY`: 3 → **1** — prompt ngắn hơn, Gemini phản hồi nhanh hơn
- `GEMINI_CHAT_MODEL`: hardcode → đọc từ env `GEMINI_CHAT_MODEL` (dễ đổi không cần restart)

---

### `.env`
- Thêm `GEMINI_CHAT_MODEL=gemini-2.5-flash` — dễ đổi model không cần sửa code
- Thêm `ANONYMIZED_TELEMETRY=False` — tắt ChromaDB telemetry spam log

---

### `app/main.py`
- Thêm log startup: `Device: CUDA — <tên GPU>` hoặc `Device: CPU (CUDA not available)` — biết ngay GPU có hoạt động không khi khởi động

---

### `app/services/rag_service.py`
- Thêm `[TIMING]` log từng bước: `intent_classify`, `retrieval`, `gemini`, `total_pipeline` — debug bottleneck dễ hơn

---

### `app/services/intent_service.py`
- **Bỏ hoàn toàn Gemini `classify()`** trong `classify_intent` — tiết kiệm ~10s/request cho câu không khớp regex
- **Đổi fallback từ `out_of_scope` → `document_qa`** — câu hỏi không rõ intent sẽ được RAG tìm kiếm thay vì bị chặn
- Thêm `OUT_OF_SCOPE_KEYWORDS` — chỉ trả `out_of_scope` khi câu hỏi rõ ràng ngoài lề (thời tiết, ẩm thực, giải trí...)
- Thêm regex vào `DOCUMENT_KEYWORDS`: cơ cấu, cấp bậc, chức danh, sơ đồ tổ chức, thăng chức, đào tạo, tuyển dụng, hợp đồng, phòng ban

---

### `app/services/reranker_service.py`
- `device="cuda"` — đã có sẵn, xác nhận dùng GPU

### `app/services/embedding_service.py`
- `device="cuda"`, `torch_dtype=float16` — đã có sẵn, xác nhận dùng GPU

---

### `app/prompts/answer_prompt.txt`
- Fallback message: `"Sorry, there is no information..."` → **`"Xin lỗi, tôi không tìm thấy thông tin phù hợp trong hệ thống."`** — trả lời tiếng Việt nhất quán

---

### `app/data/intent_examples.json` *(file mới)*
- Tạo mới với **79 examples** tiếng Việt cho k-NN intent classifier:
  - `document_qa`: 44 examples — chính sách, quy trình, cơ cấu, hợp đồng, đào tạo...
  - `employee_status`: 20 examples — trạng thái, chấm công, nghỉ phép...
  - `out_of_scope`: 15 examples — thời tiết, ẩm thực, giải trí...

---

## Hướng dẫn sau khi re-ingest

Sau khi thay đổi `CHUNK_SIZE`, cần xóa ChromaDB và ingest lại:
```powershell
# 1. Dừng server
# 2. Xóa chroma data
Remove-Item -Recurse -Force "data/chroma"
# 3. Khởi động lại server
# 4. Gọi ingest-all
curl -X POST http://localhost:8000/api/documents/ingest-all -H "X-API-Key: demo_admin_001"
```

## Yêu cầu môi trường

PyTorch phải cài với CUDA để dùng GPU:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
Verify: `python -c "import torch; print(torch.cuda.is_available())"`
