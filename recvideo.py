import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import threading
import datetime
import os
from PIL import Image, ImageTk
import time
import queue
import sys

class VideoRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quay Video Đơn Hàng")
        self.root.geometry("700x550")
        
        # Biến trạng thái
        self.cap = None
        self.out = None
        self.recording = False
        self.preview_running = False
        self.current_frame = None
        self.video_thread = None
        self.record_thread = None
        
        # Queue để đồng bộ frames giữa capture và record
        self.frame_queue = queue.Queue(maxsize=10)  # Buffer 10 frames
        
        # Tạo thư mục Videos nếu chưa tồn tại
        self.videos_dir = os.path.join(os.path.expanduser("~"), "Videos")
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir)
        
        self.setup_ui()
        self.initialize_camera()
        
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Frame cho title input
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        ttk.Label(title_frame, text="Tiêu đề video:").grid(row=0, column=0, padx=(0, 10))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=50)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Frame cho video preview
        video_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        video_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(expand=True)
        
        # Frame cho các nút điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="Bắt đầu quay", command=self.start_recording)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Kết thúc", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.browse_btn = ttk.Button(control_frame, text="Chọn thư mục lưu", command=self.browse_folder)
        self.browse_btn.pack(side=tk.LEFT)
        
        # Frame cho thông tin trạng thái
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        ttk.Label(status_frame, text="Trạng thái:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        
        # Hiển thị đường dẫn lưu video
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="Thư mục lưu:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar()
        self.path_var.set(self.videos_dir)
        ttk.Label(path_frame, textvariable=self.path_var, foreground="gray").grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
    def initialize_camera(self):
        """Khởi tạo webcam với cấu hình tối ưu cho Rapoo"""
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        camera_index = 2  # Chỉ sử dụng webcam
        
        for backend in backends:
            try:
                print(f"Thử camera index {camera_index} với backend {backend}")
                cap = cv2.VideoCapture(camera_index, backend)
                
                if cap.isOpened():
                    # Cấu hình buffer để giảm độ trễ
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Đợi một chút để camera khởi tạo
                    time.sleep(1)
                    
                    # Thử đọc frame nhiều lần
                    for attempt in range(10):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            self.cap = cap
                            
                            # Lấy thông tin camera hiện tại
                            current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            
                            print(f"webcam tìm thấy: {current_width}x{current_height}")
                            
                            # Cấu hình camera cho FullHD nếu có thể
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                            
                            # Cấu hình FPS - thử 25 FPS trước cho ổn định
                            self.cap.set(cv2.CAP_PROP_FPS, 25)
                            
                            # Cấu hình thêm cho webcam Rapoo
                            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
                            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            
                            # Kiểm tra độ phân giải đã set
                            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
                            
                            print(f"Cấu hình thực tế: {actual_width}x{actual_height} @ {actual_fps} FPS")
                            
                            # Bắt đầu luồng hiển thị preview
                            self.start_preview()
                            self.status_var.set(f"webcam kết nối ({actual_width}x{actual_height} @ {actual_fps:.1f}fps)")
                            return
                        time.sleep(0.1)
                    
                    cap.release()
                
            except Exception as e:
                print(f"Lỗi với webcam: {e}")
                if 'cap' in locals():
                    cap.release()
                continue
        
        # Nếu không tìm thấy webcam
        messagebox.showerror("Lỗi", "Không tìm thấy webcam!")
        self.status_var.set("Không có webcam")
        
    def start_preview(self):
        """Bắt đầu hiển thị preview với frame capture riêng biệt"""
        self.preview_running = True
        
        # Thread để capture frame từ camera
        def capture_frames():
            consecutive_failures = 0
            max_failures = 20
            
            while self.preview_running and self.cap and self.cap.isOpened():
                try:
                    ret, frame = self.cap.read()
                    
                    if ret and frame is not None and frame.size > 0:
                        consecutive_failures = 0
                        self.current_frame = frame.copy()
                        
                        # Nếu đang recording, thêm frame vào queue
                        if self.recording:
                            try:
                                # Non-blocking put, bỏ qua nếu queue đầy
                                self.frame_queue.put((time.time(), frame.copy()), block=False)
                            except queue.Full:
                                # Bỏ frame cũ nhất nếu queue đầy
                                try:
                                    self.frame_queue.get_nowait()
                                    self.frame_queue.put((time.time(), frame.copy()), block=False)
                                except queue.Empty:
                                    pass
                        
                        # Hiển thị preview (ít tần suất hơn để tiết kiệm CPU)
                        if consecutive_failures == 0:  # Chỉ update preview khi không có lỗi
                            display_frame = frame.copy()
                            if self.recording:
                                display_frame = self.add_overlays(display_frame)
                            
                            try:
                                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                                frame_resized = cv2.resize(frame_rgb, (640, 360))
                                
                                img = Image.fromarray(frame_resized)
                                imgtk = ImageTk.PhotoImage(image=img)
                                
                                self.root.after(0, self.update_video_label, imgtk)
                                
                            except Exception as e:
                                print(f"Lỗi xử lý preview: {e}")
                    else:
                        consecutive_failures += 1
                        print(f"Không đọc được frame, lần thử {consecutive_failures}")
                        
                    if consecutive_failures > max_failures:
                        print("Quá nhiều lỗi liên tiếp, dừng capture")
                        break
                        
                except Exception as e:
                    print(f"Lỗi trong capture: {e}")
                    consecutive_failures += 1
                    if consecutive_failures > max_failures:
                        break
                
                # Điều chỉnh delay dựa trên trạng thái
                if self.recording:
                    time.sleep(0.02)  # 50 FPS capture khi recording
                else:
                    time.sleep(0.033)  # 30 FPS khi chỉ preview
            
            print("Capture thread đã dừng")
        
        self.video_thread = threading.Thread(target=capture_frames, daemon=True)
        self.video_thread.start()
        
    def update_video_label(self, imgtk):
        """Cập nhật video label trong main thread"""
        try:
            if self.video_label.winfo_exists():
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk
        except Exception as e:
            print(f"Lỗi cập nhật video label: {e}")
        
    def add_overlays(self, frame):
        """Thêm timestamp và title lên frame"""
        # Timestamp ở góc trên trái
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, timestamp, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        
        # Title ở góc dưới phải
        title = self.title_var.get()
        if title:
            text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = frame.shape[1] - text_size[0] - 30
            text_y = frame.shape[0] - 30
            
            cv2.putText(frame, title, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, title, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        
        return frame
        
    def start_recording(self):
        """Bắt đầu quay video"""
        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("Lỗi", "Camera không được kết nối!")
            return
            
        if not self.title_var.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tiêu đề video!")
            return
        
        # Tạo tên file video
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        title_safe = "".join(c for c in self.title_var.get() if c.isalnum() or c in (' ', '_', '-')).strip()
        filename = f"{timestamp}_{title_safe}.mp4"
        self.video_path = os.path.join(self.path_var.get(), filename)
        
        # Lấy độ phân giải thực tế của camera
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (actual_width, actual_height)
        
        # Sử dụng FPS cố định 25 cho ổn định
        target_fps = 25.0
        
        print(f"Ghi video với độ phân giải: {frame_size}, FPS: {target_fps}")
        
        # Khởi tạo VideoWriter với codec mp4v
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.out = cv2.VideoWriter(self.video_path, fourcc, target_fps, frame_size)
        
        if not self.out.isOpened():
            # Thử lại với codec avc1 nếu mp4v không hoạt động
            print("mp4v không hoạt động, thử avc1...")
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            self.out = cv2.VideoWriter(self.video_path, fourcc, target_fps, frame_size)
            
            if not self.out.isOpened():
                messagebox.showerror("Lỗi", "Không thể tạo file video!")
                return
        
        # Clear frame queue trước khi bắt đầu
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        self.recording = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.title_entry.config(state=tk.DISABLED)
        
        self.status_var.set("Đang quay video...")
        
        # Bắt đầu luồng ghi video
        self.record_thread = threading.Thread(target=self.record_video, daemon=True)
        self.record_thread.start()
        
    def record_video(self):
        """Ghi video từ frame queue với timing chính xác"""
        frame_count = 0
        target_fps = 25.0
        frame_interval = 1.0 / target_fps
        start_time = time.time()
        next_frame_time = start_time
        
        print(f"Bắt đầu ghi video với FPS: {target_fps}")
        
        while self.recording:
            try:
                current_time = time.time()
                
                # Chờ đến thời điểm ghi frame tiếp theo
                if current_time < next_frame_time:
                    time.sleep(next_frame_time - current_time)
                
                # Lấy frame mới nhất từ queue
                frame_data = None
                frame_timestamp = None
                
                # Lấy frame mới nhất, bỏ qua các frame cũ
                frames_skipped = 0
                while not self.frame_queue.empty():
                    try:
                        frame_timestamp, frame_data = self.frame_queue.get_nowait()
                        frames_skipped += 1
                    except queue.Empty:
                        break
                
                if frames_skipped > 1:
                    print(f"Bỏ qua {frames_skipped-1} frame cũ")
                
                if frame_data is not None:
                    # Thêm overlays
                    frame_with_overlays = self.add_overlays(frame_data)
                    
                    # Ghi frame
                    if self.out and self.out.isOpened():
                        success = self.out.write(frame_with_overlays)
                        if success:
                            frame_count += 1
                            if frame_count % 100 == 0:  # Log mỗi 100 frame
                                elapsed = time.time() - start_time
                                actual_fps = frame_count / elapsed
                                print(f"Đã ghi {frame_count} frames, FPS thực tế: {actual_fps:.2f}")
                        else:
                            print(f"Không thể ghi frame {frame_count}")
                    
                    # Cập nhật thời gian frame tiếp theo
                    next_frame_time += frame_interval
                    
                    # Điều chỉnh nếu bị trễ quá nhiều
                    if next_frame_time < current_time - frame_interval:
                        next_frame_time = current_time + frame_interval
                        
                else:
                    # Không có frame mới, chờ một chút
                    time.sleep(0.005)
                    
            except Exception as e:
                print(f"Lỗi trong quá trình ghi frame {frame_count}: {e}")
                break
        
        elapsed_total = time.time() - start_time
        actual_avg_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        print(f"Kết thúc ghi video: {frame_count} frames trong {elapsed_total:.2f}s, FPS trung bình: {actual_avg_fps:.2f}")
            
    def stop_recording(self):
        """Dừng quay video"""
        print("Đang dừng quay video...")
        self.recording = False
        
        # Đợi thread ghi video kết thúc
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            print("Đang chờ thread ghi video kết thúc...")
            self.record_thread.join(timeout=5)  # Tăng timeout lên 5 giây
        
        # Clear frame queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        # Đảm bảo tất cả frame được ghi xong
        time.sleep(0.5)
        
        if self.out:
            print("Đang đóng file video...")
            try:
                self.out.release()
                print("Đã đóng file video thành công")
            except Exception as e:
                print(f"Lỗi khi đóng file video: {e}")
            finally:
                self.out = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.title_entry.config(state=tk.NORMAL)
        
        self.status_var.set("Đã lưu video")
        
        # Kiểm tra xem file có tồn tại và có kích thước hợp lý không
        if os.path.exists(self.video_path):
            file_size = os.path.getsize(self.video_path)
            if file_size > 0:
                messagebox.showinfo("Thành công", f"Video đã được lưu tại:\n{self.video_path}\nKích thước: {file_size/1024/1024:.1f} MB")
            else:
                messagebox.showerror("Lỗi", "File video được tạo nhưng có kích thước 0 bytes!")
        else:
            messagebox.showerror("Lỗi", "Không thể tạo file video!")
        
    def browse_folder(self):
        """Chọn thư mục lưu video"""
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
            
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        print("Đang đóng ứng dụng...")
        
        # Dừng recording nếu đang quay
        if self.recording:
            self.stop_recording()
        
        # Dừng preview
        self.preview_running = False
        
        # Đợi thread preview kết thúc
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=3)
        
        # Giải phóng camera
        if self.cap:
            self.cap.release()
        
        # Giải phóng video writer
        if self.out:
            self.out.release()
            
        cv2.destroyAllWindows()
        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Thay icon bằng ảnh webcam.ico
    try:
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), "webcam.ico")
        icon_img = ImageTk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_img)
    except Exception as e:
        print(f"Không thể đặt icon: {e}")
        
    app = VideoRecorderApp(root)
    
    # Xử lý sự kiện đóng cửa sổ
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()