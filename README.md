# KuloPustaka — Sistem Peminjaman Buku Perpustakaan Desa Kulo

## Fitur
- 1 akun internal kantor (tanpa registrasi anggota)
- Dashboard statistik
- CRUD buku
- CRUD peminjam
- Pencatatan peminjaman
- Pengembalian otomatis menambah stok
- Riwayat transaksi
- Laporan dan cetak
- Responsive
- HTML, CSS, JS, dan gambar dipisahkan

## 1. Install
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Database
Buka XAMPP → MySQL → phpMyAdmin, lalu import `database.sql`.

Jika MySQL memakai password, set environment:
```powershell
$env:DB_PASSWORD="password_mysql"
```

## 3. Jalankan
```bash
python app.py
```
Buka `http://127.0.0.1:5000`

## Login awal
Username: `admin`
Password: `KuloPustaka123`

Untuk keamanan, ganti username/password di `app.py` sebelum hosting publik dan ganti `SECRET_KEY`.
