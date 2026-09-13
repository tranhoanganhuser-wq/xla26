# CHỦ ĐỀ 3 - XỬ LÝ ẢNH

Bộ mã nguồn gồm 2 ứng dụng desktop bằng **Python + PySide6 + OpenCV + NumPy**.
Tên thư mục và file được đặt ngắn gọn, dễ đọc theo cách nhóm sinh viên Việt Nam thường dùng.

## 1. Cấu trúc thư mục

```text
ChuDe3_XuLyAnh/
├── xulychung/
│   ├── xulyanh.py
│   └── giaodien.py
├── project1_miniphotoshop/
│   ├── main.py
│   ├── xulyanh.py
│   └── histogram.py
├── project2_sohoatailieu/
│   ├── main.py
│   ├── xulytailieu.py
│   └── xuatpdf.py
├── kiemthu/
│   └── kiemthu_nhanh.py
├── requirements.txt
└── README.md
```

## 2. Ý nghĩa các file

### `xulychung/`
- `xulyanh.py`: đọc ảnh, lưu ảnh, chuyển ảnh OpenCV sang QImage và hiển thị ảnh lên GUI.
- `giaodien.py`: các thành phần giao diện dùng chung cho hai project.

### `project1_miniphotoshop/`
- `main.py`: giao diện chính của Mini Photoshop.
- `xulyanh.py`: Brightness, Contrast, Blur, Histogram, Histogram Equalization và thống kê ảnh.
- `histogram.py`: phần vẽ Histogram trên GUI.

### `project2_sohoatailieu/`
- `main.py`: giao diện chính của ứng dụng số hóa tài liệu.
- `xulytailieu.py`: phát hiện tờ giấy, perspective transform, khử nền, Adaptive Threshold và Morphology.
- `xuatpdf.py`: xuất một hoặc nhiều trang ảnh thành PDF.

### `kiemthu/`
- `kiemthu_nhanh.py`: kiểm tra nhanh thuật toán lõi mà không cần mở GUI.

## 3. Cài đặt

Khuyến nghị Python 3.10+.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

## 4. Chạy Project 1 - Mini Photoshop

```bash
python project1_miniphotoshop/main.py
```

Chức năng chính:
- Mở/lưu ảnh JPG, PNG, BMP, TIFF.
- Brightness.
- Contrast.
- Gaussian / Mean / Median Blur.
- Histogram Gray/RGB và thay đổi số bins.
- Histogram Equalization mở rộng.
- Before/After, thống kê ảnh.
- Undo/Redo/Reset.

## 5. Chạy Project 2 - Số hóa tài liệu

```bash
python project2_sohoatailieu/main.py
```

Pipeline:

```text
Ảnh chụp tài liệu
-> phát hiện tờ giấy + chỉnh phối cảnh
-> grayscale
-> khử nền/ánh sáng không đều
-> Adaptive Threshold
-> Morphology
-> Preview
-> Save / Export PDF
```

## 6. Kiểm thử nhanh

```bash
python kiemthu/kiemthu_nhanh.py
```

## 7. Quy ước xử lý ảnh

- Ảnh màu trong lõi xử lý: `numpy.ndarray`, BGR, `uint8`.
- Phép toán cường độ: `uint8 -> float32 -> transform -> clip [0,255] -> uint8`.
- GUI chỉ gọi hàm xử lý; công thức xử lý được tách riêng trong các file `xulyanh.py` và `xulytailieu.py`.
