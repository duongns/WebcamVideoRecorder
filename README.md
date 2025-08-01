# Video Recorder - Ứng dụng quay video đơn hàng

## Giới thiệu

Video Recorder là một ứng dụng Python được thiết kế để quay video với webcam, đặc biệt tối ưu cho việc ghi lại quá trình xử lý đơn hàng. Ứng dụng có giao diện thân thiện với người dùng và nhiều tính năng hữu ích.

## Tính năng chính

### 🎥 Quay video chất lượng cao
- Hỗ trợ độ phân giải lên đến Full HD (1920x1080)
- Tự động tối ưu FPS (25fps) cho video mượt mà
- Codec MP4 tương thích với mọi thiết bị

### 🎬 Preview real-time
- Xem trước video trong thời gian thực
- Hiển thị overlay khi đang quay
- Giao diện trực quan và dễ sử dụng

### 📝 Tùy chỉnh nội dung
- Thêm tiêu đề tùy chỉnh cho từng video
- Timestamp tự động trên video
- Overlay thông tin góc màn hình

### 💾 Quản lý file thông minh
- Tự động tạo tên file với timestamp
- Chọn thư mục lưu trữ tùy ý
- Mặc định lưu trong thư mục Videos của người dùng

### 🔧 Tối ưu hiệu suất
- Multi-threading cho capture và recording
- Buffer frame queue để tránh lag
- Xử lý lỗi camera robust

## Yêu cầu hệ thống

### Python và thư viện
```
Python 3.7+
opencv-python (cv2)
tkinter (built-in)
PIL (Pillow)
```

### Phần cứng
- Webcam (khuyến nghị Rapoo hoặc tương tự)
- Windows 10/11 (tối ưu cho DirectShow)
- RAM: tối thiểu 4GB
- Ổ cứng: dung lượng trống tùy theo thời lượng video

## Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/yourusername/video-recorder.git
cd video-recorder
```

### 2. Cài đặt dependencies
```bash
pip install opencv-python pillow
```

### 3. Chạy ứng dụng
```bash
python recvideo.py
```

## Cách sử dụng

### Bước 1: Khởi động
- Chạy `recvideo.py`
- Ứng dụng sẽ tự động tìm và kết nối webcam
- Preview sẽ hiển thị trong cửa sổ chính

### Bước 2: Cấu hình
- Nhập tiêu đề cho video trong ô "Tiêu đề video"
- (Tùy chọn) Chọn thư mục lưu khác bằng nút "Chọn thư mục lưu"

### Bước 3: Quay video
- Nhấn "Bắt đầu quay" để bắt đầu
- Video sẽ có overlay timestamp và tiêu đề
- Nhấn "Kết thúc" để dừng và lưu video

## Cấu trúc dự án

```
video-recorder/
│
├── recvideo.py          # File chính của ứng dụng
├── webcam.ico           # Icon cho ứng dụng (tùy chọn)
├── README.md            # File hướng dẫn này
└── requirements.txt     # Danh sách dependencies
```

## Tính năng kỹ thuật

### Camera Initialization
- Tự động detect webcam với các backend khác nhau
- Tối ưu buffer size để giảm latency
- Hỗ trợ MJPEG format cho webcam chuyên nghiệp

### Video Processing
- Frame capture và recording chạy song song
- Queue-based frame buffering
- Automatic frame rate adjustment

### Error Handling
- Robust camera connection handling
- Graceful degradation khi có lỗi
- Auto-recovery mechanisms

## Troubleshooting

### Không tìm thấy webcam
- Kiểm tra webcam đã được cắm và driver đã cài đặt
- Thử thay đổi `camera_index` trong code (mặc định là 2)
- Đảm bảo không có ứng dụng nào khác đang sử dụng webcam

### Video không mượt
- Kiểm tra CPU usage
- Thử giảm độ phân giải trong code
- Đảm bảo đủ dung lượng ổ cứng

### File video bị lỗi
- Kiểm tra quyền ghi trong thư mục đích
- Thử codec khác (avc1 thay vì mp4v)
- Đảm bảo đóng ứng dụng đúng cách

## Customization

### Thay đổi độ phân giải
Trong hàm `initialize_camera()`:
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Thay 1920
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Thay 1080
```

### Thay đổi FPS
Trong hàm `start_recording()`:
```python
target_fps = 30.0  # Thay 25.0
```

### Tùy chỉnh overlay
Chỉnh sửa hàm `add_overlays()` để thay đổi:
- Vị trí text
- Font size
- Màu sắc
- Nội dung hiển thị

## Đóng góp

Mọi đóng góp đều được chào đón! Hãy:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Phiên bản

- **v1.0.0** - Release đầu tiên với đầy đủ tính năng cơ bản

## Tác giả

[Nguyễn Sơn Dương] - [duongns84@gmail.com]

## License

Dự án này được phân phối under MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Acknowledgments

- OpenCV community cho thư viện xử lý video mạnh mẽ
- Python Tkinter documentation
- Cộng đồng lập trình viên Việt Nam

---

⭐ Nếu dự án này hữu ích, hãy cho một star để ủng hộ nhé!