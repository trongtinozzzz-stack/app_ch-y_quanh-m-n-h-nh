# Hướng dẫn sử dụng & Tải lên Chrome Extension 🎀

## 1. Cài đặt trực tiếp vào Google Chrome (Dùng ngay lập tức)

1. Mở trình duyệt **Google Chrome** (hoặc Edge / Brave / Cốc Cốc / Opera).
2. Truy cập vào đường dẫn: `chrome://extensions/`
3. Bật công tắc **Chế độ dành cho nhà phát triển** (Developer mode) ở góc trên bên phải.
4. Bấm nút **Tải tiện ích đã giải nén** (Load unpacked) ở góc trên bên trái.
5. Chọn thư mục `extension` trong dự án của bạn:
   ```
   d:\app_chạy_quanh màn hình\extension
   ```
6. Bé Anya sẽ xuất hiện ngay lập tức trên mọi trang web bạn mở! 🎉

---

## 2. Đóng gói thành 1 file ZIP để tải lên Google Web Store hoặc gửi bạn bè

Chỉ cần chạy file:
```
pack_extension.bat
```
Script sẽ tự động nén toàn bộ thư mục `extension` thành file:
```
desktop-pet-extension.zip
```

---

## 3. Cách tải lên Google Chrome Web Store Developer Dashboard

1. Truy cập [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole).
2. Đăng nhập tài khoản Google Developer.
3. Bấm **Add new item** (Thêm mục mới).
4. Kéo thả file `desktop-pet-extension.zip` vào để tải lên.
5. Điền mô tả, chụp ảnh màn hình và gửi xét duyệt!
