# web_phishing — Phishing Detector

Một bộ công cụ phát hiện phishing dựa trên trích xuất hơn 80 đặc trưng từ URL cùng với kiến trúc Cascade + Stacking (Logistic Regression + XGBoost/LightGBM/CatBoost/Neural Network + Meta-Learner).

**Ngôn ngữ**: Python

---

**Mục tiêu**: Hỗ trợ phân tích URL để xác định khả năng phishing bằng mô hình học máy đã huấn luyện, cung cấp cả giao diện tương tác (Streamlit) và các script để chuẩn bị dữ liệu, huấn luyện và đánh giá mô hình.

**Tính năng chính**
- **Phân tích đơn lẻ**: Kiểm tra 1 URL và trả về dự đoán cùng nhiều trực quan hóa.
- **Phân tích hàng loạt**: Upload file CSV chứa cột `url` để phân tích nhiều URL cùng lúc.
- **Pipeline mô hình**: Cascade filter (LR) + stacking ensemble (XGBoost, LightGBM, CatBoost, NN) + meta-learner.
- **80+ feature extraction**: Chuẩn hóa về {-1, 0, 1} cho độ ổn định.

**Yêu cầu**
- Python 3.8+
- Các thư viện được liệt kê trong `requirements.txt`.

---

**Cài đặt nhanh**
1. Tạo môi trường ảo (khuyến nghị):

```bash
python -m venv .venv
source .venv/Scripts/activate  # trên Windows (Git Bash)
pip install -r requirements.txt
```

2. (Tùy chọn) Đặt các biến môi trường hoặc cấu hình nếu cần.

---

**Chạy ứng dụng Streamlit (giao diện)**

Ứng dụng chính nằm trong thư mục `app/`. Để chạy local:

```bash
streamlit run app/Home.py
```

Trang chính sẽ hiển thị các lựa chọn: phân tích đơn lẻ (`1_Single_URL.py`), phân tích hàng loạt (`2_Batch_Analysis.py`) và trang thông tin (`3_About.py`).

---

**Cấu trúc dự án (tóm tắt)**
- `app/` : Streamlit UI và styles.
	- `Home.py` : Entry point cho app.
	- `components.py` : Header / Footer và các component UI.
	- `styles.py` : CSS tùy chỉnh.
	- `pages/` : Các trang con (Single URL, Batch, About).
- `src/` : Mã lõi cho hệ thống.
	- `config.py` : Các hằng số và đường dẫn mô hình.
	- `constants.py` : Tập các từ khóa, TLD đáng ngờ, domain tin cậy, ...
	- `features.py` : Hàm trích xuất và chuẩn hóa 80+ features.
	- `predictor.py` : Lớp `PhishingPredictor` để load mô hình và dự đoán.
	- `utils.py` : Các tiện ích (entropy, ssl, dns, ...).
- `data/` : Dữ liệu thô và dữ liệu xử lý sẵn.
	- `raw/` : CSV thô (ví dụ `Phishing URLs.csv`, `URL dataset.csv`).
	- `processed/` : Dữ liệu features đã xử lý (ví dụ `Combined_Normalized_Features.csv`).
- `models/` : Mô hình đã huấn luyện (ví dụ `neural_network.h5`, các file `.pkl` khi có).
- `scripts/` : Các script thao tác dữ liệu và huấn luyện.
	- `prepare_data.py` : Trích xuất features từ file raw.
	- `train_models.py` : Huấn luyện cascade + stacking models.
	- `evaluate.py` : Đánh giá các model trên tập test.

---

**Sử dụng mô hình từ code**
- Để dùng trực tiếp từ mã (không qua UI), import `PhishingPredictor` từ `src/predictor.py`:

```python
from src.predictor import PhishingPredictor
predictor = PhishingPredictor(model_dir='models/')
result = predictor.predict('https://example.com')
```

`predict()` trả về thông tin về xác suất, nhãn và mức độ rủi ro (risk level).

---

**Scripts chính**
- `scripts/prepare_data.py` : Đọc file CSV thô, trích xuất features bằng `src.features.extract_features`, lưu kết quả vào `data/processed`.
- `scripts/train_models.py` : Huấn luyện pipeline (chuẩn hóa, LR cascade, resampling, stacking, NN), lưu model vào `models/`.
- `scripts/evaluate.py` : Chạy dự đoán trên tập test và in các metrics (accuracy, precision, recall, f1, ROC AUC).

---

**Ghi chú cho nhà phát triển**
- File cấu hình mặc định: `src/config.py` (thay đổi thresholds hoặc đường dẫn tại đây).
- Nếu muốn phân tích nội dung trang (page content), bật `ANALYZE_CONTENT = True` trong `src/config.py` (cẩn thận với timeout và crawling).
- Một số chức năng (ví dụ: kiểm tra SSL chi tiết) yêu cầu quyền mạng và có thể thất bại trên môi trường bị chặn.

---

**Troubleshooting nhanh**
- Nếu thiếu model pickle (`.pkl`) hoặc file `feature_names.pkl`, khởi tạo lại bằng `scripts/train_models.py`.
- Lỗi import: đảm bảo thư mục gốc được thêm vào `PYTHONPATH` hoặc chạy từ root repository.

---

**License & Credits**
Repository hiện chưa chứa file license; thêm `LICENSE` nếu muốn công khai với một giấy phép cụ thể.

---

Nếu bạn muốn, tôi có thể:
- Thêm một file `CONTRIBUTING.md` ngắn;
- Tạo script Docker/Compose để chạy app;
- Hoặc commit và tạo branch cho README này.
