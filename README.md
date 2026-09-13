# CHỦ ĐỀ 3 - XỬ LÝ ẢNH

Bộ mã nguồn hoàn chỉnh gồm 2 ứng dụng desktop bằng **Python + PySide6 + OpenCV + NumPy**.

## 1. Cấu trúc

```text
ChuDe3_XuLyAnh_PySide6/
├── common/
│   ├── image_utils.py
│   └── widgets.py
├── project1_mini_photoshop/
│   ├── main.py
│   ├── processing.py
│   └── histogram_canvas.py
├── project2_document_digitization/
│   ├── main.py
│   ├── document_processing.py
│   └── pdf_export.py
├── requirements.txt
└── README.md
```

## 2. Cài đặt

Khuyến nghị Python 3.10+.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

## 3. Chạy Project 1 - Mini Photoshop

```bash
python project1_mini_photoshop/main.py
```

Chức năng chính:

- Mở/lưu ảnh JPG/PNG/BMP/TIFF.
- Brightness: công thức `g = f + beta`, xử lý an toàn float32 -> clip -> uint8.
- Contrast: `g = alpha * (f - 127.5) + 127.5`.
- Blur: Gaussian / Mean / Median.
- Histogram Gray/RGB, thay đổi số bins.
- Histogram Equalization trên kênh Y (chức năng mở rộng).
- Before/After, thống kê min/max/mean/std/dynamic range.
- Undo/Redo/Reset.

## 4. Chạy Project 2 - Số hóa tài liệu

```bash
python project2_document_digitization/main.py
```

Pipeline:

```text
Ảnh chụp tài liệu
-> phát hiện tờ giấy + perspective correction (tùy chọn)
-> grayscale
-> khử nền/chiếu sáng không đều (tùy chọn)
-> Adaptive Threshold (Mean/Gaussian)
-> Morphology (None/Opening/Closing)
-> Preview
-> Save image / Export PDF nhiều trang
```

Phần "loại bỏ nền" triển khai cả hai hướng:

1. Tách tờ giấy khỏi nền bên ngoài bằng contour + biến đổi phối cảnh.
2. Khử nền/ánh sáng không đều trên bề mặt giấy bằng ước lượng nền morphology.

PDF hỗ trợ Auto hoặc A4, Portrait/Landscape, margin.

## 5. Quy ước xử lý ảnh

- Ảnh màu lõi xử lý: `numpy.ndarray`, BGR, `uint8`.
- Phép toán cường độ: `uint8 -> float32 -> transform -> clip [0,255] -> uint8`.
- GUI không chứa công thức xử lý; GUI chỉ gọi các hàm trong module processing.

## 6. Gợi ý kiểm thử

Project 1: tối thiểu 10 ảnh, nên có ảnh tối/sáng/contrast thấp/nhiễu/chi tiết cao.

Project 2: tối thiểu 100 ảnh, nên chia các nhóm: ánh sáng đều, không đều, bóng đổ, giấy vàng, nền bàn, chữ mờ, nhiễu.

## 7. Lưu ý

- Không có một bộ tham số Adaptive Threshold tối ưu cho mọi tài liệu. Cần dùng GUI để thay `block size`, `C`, background kernel và morphology rồi đánh giá.
- Tự động tìm biên tờ giấy có thể thất bại nếu biên giấy không rõ hoặc giấy gần cùng màu với nền. Khi đó ứng dụng tự dùng ảnh gốc để tiếp tục pipeline.
