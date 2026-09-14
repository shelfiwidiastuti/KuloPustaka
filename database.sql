CREATE DATABASE IF NOT EXISTS kulopustaka
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE kulopustaka;

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    publisher VARCHAR(150),
    year YEAR NULL,
    category VARCHAR(100),
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrowers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    borrower_id INT NOT NULL,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status ENUM('Dipinjam','Dikembalikan') NOT NULL DEFAULT 'Dipinjam',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);

INSERT IGNORE INTO books (code,title,author,publisher,year,category,stock) VALUES
('BK-001','Laskar Pelangi','Andrea Hirata','Bentang Pustaka',2005,'Novel',5),
('BK-002','Bumi','Tere Liye','Gramedia',2014,'Novel',4),
('BK-003','Atomic Habits','James Clear','Avery',2018,'Pengembangan Diri',3);

INSERT IGNORE INTO borrowers (member_code,name,phone,address) VALUES
('AG-001','Contoh Peminjam','081234567890','Desa Kulo');
