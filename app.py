from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from functools import wraps
from datetime import date, datetime
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "kulopustaka-secret-key-change-me"
)


# =========================================================
# DATABASE
# =========================================================

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "kulopustaka")
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("logged_in"):
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# GLOBAL VARIABLES UNTUK TEMPLATE
# =========================================================

@app.context_processor
def inject_globals():

    return {
        "current_year": datetime.now().year,
        "today": date.today(),
        "current_date": date.today()
    }


# =========================================================
# INDEX
# =========================================================

@app.route("/")
def index():

    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "admin" and password == "KuloPustaka123":

            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("dashboard"))

        flash("Username atau password salah.", "danger")

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    db = get_db()
    cur = db.cursor(dictionary=True)

    # -----------------------------------------------------
    # STATISTIK BUKU
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM books
    """)

    total_books = cur.fetchone()["total"]


    cur.execute("""
        SELECT COALESCE(SUM(stock), 0) AS available
        FROM books
    """)

    available_books = cur.fetchone()["available"]


    # -----------------------------------------------------
    # STATISTIK PEMINJAMAN
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM loans
        WHERE status = 'Dipinjam'
    """)

    borrowed_books = cur.fetchone()["total"]


    cur.execute("""
        SELECT COUNT(*) AS total
        FROM loans
        WHERE status = 'Dipinjam'
        AND due_date < CURDATE()
    """)

    overdue_books = cur.fetchone()["total"]


    # -----------------------------------------------------
    # STATISTIK PEMINJAM
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM borrowers
    """)

    total_borrowers = cur.fetchone()["total"]


    # -----------------------------------------------------
    # BUKU TAMU - JUMLAH HARI INI
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM guestbook
        WHERE visit_date = CURDATE()
    """)

    today_visitors = cur.fetchone()["total"]


    # -----------------------------------------------------
    # PEMINJAMAN TERBARU
    # -----------------------------------------------------

    cur.execute("""
        SELECT
            l.id,
            b.title,
            br.name,
            br.member_code,
            l.loan_date,
            l.due_date,
            l.return_date,
            l.status
        FROM loans l
        JOIN books b
            ON b.id = l.book_id
        JOIN borrowers br
            ON br.id = l.borrower_id
        ORDER BY l.id DESC
        LIMIT 8
    """)

    recent = cur.fetchall()


    # -----------------------------------------------------
    # BUKU TAMU TERBARU
    # -----------------------------------------------------

    cur.execute("""
        SELECT
            id,
            name,
            origin,
            purpose,
            visit_date,
            entry_time,
            exit_time,
            note
        FROM guestbook
        ORDER BY visit_date DESC, entry_time DESC, id DESC
        LIMIT 5
    """)

    recent_guests = cur.fetchall()


    cur.close()
    db.close()


    # -----------------------------------------------------
    # KIRIM DATA KE DASHBOARD
    # -----------------------------------------------------

    stats = {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "overdue_books": overdue_books,
        "total_borrowers": total_borrowers,
        "today_visitors": today_visitors
    }


    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent,
        recent_guests=recent_guests
    )


# =========================================================
# DATA BUKU
# =========================================================

@app.route("/buku")
@login_required
def books():

    q = request.args.get("q", "").strip()

    db = get_db()
    cur = db.cursor(dictionary=True)

    if q:

        cur.execute("""
            SELECT *
            FROM books
            WHERE title LIKE %s
            OR author LIKE %s
            OR category LIKE %s
            ORDER BY id DESC
        """, (
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        ))

    else:

        cur.execute("""
            SELECT *
            FROM books
            ORDER BY id DESC
        """)

    data = cur.fetchall()

    cur.close()
    db.close()

    return render_template(
        "books.html",
        books=data,
        q=q
    )


# =========================================================
# TAMBAH BUKU
# =========================================================

@app.route("/buku/tambah", methods=["POST"])
@login_required
def add_book():

    data = request.form

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO books
        (
            code,
            title,
            author,
            publisher,
            year,
            category,
            stock
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["code"],
        data["title"],
        data["author"],
        data["publisher"],
        data["year"] or None,
        data["category"],
        data["stock"]
    ))

    db.commit()

    cur.close()
    db.close()

    flash("Buku berhasil ditambahkan.", "success")

    return redirect(url_for("books"))


# =========================================================
# EDIT BUKU
# =========================================================

@app.route("/buku/edit/<int:id>", methods=["POST"])
@login_required
def edit_book(id):

    data = request.form

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE books
        SET
            code=%s,
            title=%s,
            author=%s,
            publisher=%s,
            year=%s,
            category=%s,
            stock=%s
        WHERE id=%s
    """, (
        data["code"],
        data["title"],
        data["author"],
        data["publisher"],
        data["year"] or None,
        data["category"],
        data["stock"],
        id
    ))

    db.commit()

    cur.close()
    db.close()

    flash("Data buku berhasil diperbarui.", "success")

    return redirect(url_for("books"))


# =========================================================
# HAPUS BUKU
# =========================================================

@app.route("/buku/hapus/<int:id>", methods=["POST"])
@login_required
def delete_book(id):

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "DELETE FROM books WHERE id=%s",
        (id,)
    )

    db.commit()

    cur.close()
    db.close()

    flash("Buku berhasil dihapus.", "success")

    return redirect(url_for("books"))


# =========================================================
# DATA PEMINJAM
# =========================================================

@app.route("/peminjam")
@login_required
def borrowers():

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            br.*,
            COUNT(l.id) AS active_loans
        FROM borrowers br
        LEFT JOIN loans l
            ON br.id = l.borrower_id
            AND l.status = 'Dipinjam'
        GROUP BY br.id
        ORDER BY br.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    db.close()

    return render_template(
        "borrowers.html",
        borrowers=data
    )


# =========================================================
# TAMBAH PEMINJAM
# =========================================================

@app.route("/peminjam/tambah", methods=["POST"])
@login_required
def add_borrower():

    data = request.form

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO borrowers
        (
            member_code,
            name,
            phone,
            address
        )
        VALUES (%s,%s,%s,%s)
    """, (
        data["member_code"],
        data["name"],
        data["phone"],
        data["address"]
    ))

    db.commit()

    cur.close()
    db.close()

    flash("Peminjam berhasil ditambahkan.", "success")

    return redirect(url_for("borrowers"))


# =========================================================
# HAPUS PEMINJAM
# =========================================================

@app.route("/peminjam/hapus/<int:id>", methods=["POST"])
@login_required
def delete_borrower(id):

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM loans WHERE borrower_id=%s",
        (id,)
    )

    if cur.fetchone()[0]:

        flash(
            "Peminjam tidak dapat dihapus karena memiliki riwayat transaksi.",
            "danger"
        )

    else:

        cur.execute(
            "DELETE FROM borrowers WHERE id=%s",
            (id,)
        )

        db.commit()

        flash(
            "Peminjam berhasil dihapus.",
            "success"
        )

    cur.close()
    db.close()

    return redirect(url_for("borrowers"))


# =========================================================
# PEMINJAMAN
# =========================================================

@app.route("/peminjaman")
@login_required
def loans():

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            l.*,
            b.title,
            br.name,
            br.member_code
        FROM loans l
        JOIN books b
            ON b.id = l.book_id
        JOIN borrowers br
            ON br.id = l.borrower_id
        ORDER BY l.id DESC
    """)

    data = cur.fetchall()


    cur.execute("""
        SELECT
            id,
            title,
            stock
        FROM books
        WHERE stock > 0
        ORDER BY title
    """)

    books_data = cur.fetchall()


    cur.execute("""
        SELECT
            id,
            name,
            member_code
        FROM borrowers
        ORDER BY name
    """)

    borrowers_data = cur.fetchall()


    cur.close()
    db.close()

    return render_template(
        "loans.html",
        loans=data,
        books=books_data,
        borrowers=borrowers_data
    )


# =========================================================
# TAMBAH PEMINJAMAN
# =========================================================

@app.route("/peminjaman/tambah", methods=["POST"])
@login_required
def add_loan():

    data = request.form

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT stock FROM books WHERE id=%s FOR UPDATE",
        (data["book_id"],)
    )

    book = cur.fetchone()


    if not book or book["stock"] <= 0:

        db.rollback()

        cur.close()
        db.close()

        flash(
            "Stok buku tidak tersedia.",
            "danger"
        )

        return redirect(url_for("loans"))


    cur.execute("""
        INSERT INTO loans
        (
            book_id,
            borrower_id,
            loan_date,
            due_date,
            status
        )
        VALUES (%s,%s,%s,%s,'Dipinjam')
    """, (
        data["book_id"],
        data["borrower_id"],
        data["loan_date"],
        data["due_date"]
    ))


    cur.execute(
        "UPDATE books SET stock=stock-1 WHERE id=%s",
        (data["book_id"],)
    )


    db.commit()

    cur.close()
    db.close()

    flash(
        "Peminjaman berhasil dicatat.",
        "success"
    )

    return redirect(url_for("loans"))


# =========================================================
# PENGEMBALIAN
# =========================================================

@app.route("/pengembalian/<int:id>", methods=["POST"])
@login_required
def return_loan(id):

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM loans
        WHERE id=%s
        AND status='Dipinjam'
    """, (id,))

    loan = cur.fetchone()


    if not loan:

        flash(
            "Transaksi tidak ditemukan atau sudah dikembalikan.",
            "danger"
        )

    else:

        cur.execute("""
            UPDATE loans
            SET
                return_date=%s,
                status='Dikembalikan'
            WHERE id=%s
        """, (
            date.today(),
            id
        ))


        cur.execute(
            "UPDATE books SET stock=stock+1 WHERE id=%s",
            (loan["book_id"],)
        )


        db.commit()

        flash(
            "Buku berhasil dikembalikan.",
            "success"
        )


    cur.close()
    db.close()

    return redirect(url_for("loans"))


# =========================================================
# RIWAYAT
# =========================================================

@app.route("/riwayat")
@login_required
def history():

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            l.*,
            b.title,
            br.name,
            br.member_code
        FROM loans l
        JOIN books b
            ON b.id = l.book_id
        JOIN borrowers br
            ON br.id = l.borrower_id
        ORDER BY l.id DESC
    """)

    data = cur.fetchall()

    cur.close()
    db.close()

    return render_template(
        "history.html",
        loans=data
    )


# =========================================================
# LAPORAN
# =========================================================

@app.route("/laporan")
@login_required
def reports():

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            DATE_FORMAT(loan_date,'%Y-%m') AS month,
            COUNT(*) AS total
        FROM loans
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)

    monthly = cur.fetchall()


    cur.execute("""
        SELECT
            b.title,
            COUNT(*) AS total
        FROM loans l
        JOIN books b
            ON b.id = l.book_id
        GROUP BY b.id
        ORDER BY total DESC
        LIMIT 10
    """)

    popular = cur.fetchall()


    cur.close()
    db.close()

    return render_template(
        "reports.html",
        monthly=monthly,
        popular=popular
    )


# =========================================================
# BUKU TAMU
# =========================================================

@app.route("/buku-tamu")
@login_required
def guestbook():

    q = request.args.get("q", "").strip()
    visit_date = request.args.get("visit_date", "").strip()

    db = get_db()
    cur = db.cursor(dictionary=True)


    query = """
        SELECT *
        FROM guestbook
        WHERE 1=1
    """

    params = []


    if q:

        query += """
            AND (
                name LIKE %s
                OR origin LIKE %s
                OR purpose LIKE %s
            )
        """

        keyword = f"%{q}%"

        params.extend([
            keyword,
            keyword,
            keyword
        ])


    if visit_date:

        query += """
            AND visit_date = %s
        """

        params.append(visit_date)


    query += """
        ORDER BY
            visit_date DESC,
            entry_time DESC,
            id DESC
    """


    cur.execute(
        query,
        tuple(params)
    )

    data = cur.fetchall()


    # -----------------------------------------------------
    # TAMU HARI INI
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM guestbook
        WHERE visit_date = CURDATE()
    """)

    today_visitors = cur.fetchone()["total"]


    # -----------------------------------------------------
    # TOTAL TAMU
    # -----------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM guestbook
    """)

    total_visitors = cur.fetchone()["total"]


    cur.close()
    db.close()


    return render_template(
        "guestbook.html",
        guests=data,
        q=q,
        visit_date=visit_date,
        today_visitors=today_visitors,
        total_visitors=total_visitors
    )


# =========================================================
# TAMBAH BUKU TAMU
# =========================================================

@app.route("/buku-tamu/tambah", methods=["POST"])
@login_required
def add_guest():

    data = request.form

    db = get_db()
    cur = db.cursor()


    cur.execute("""
        INSERT INTO guestbook
        (
            name,
            origin,
            purpose,
            visit_date,
            entry_time,
            exit_time,
            note
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["name"],
        data["origin"],
        data["purpose"],
        data["visit_date"],
        data["entry_time"],
        data.get("exit_time") or None,
        data["note"]
    ))


    db.commit()

    cur.close()
    db.close()


    flash(
        "Data tamu berhasil ditambahkan.",
        "success"
    )

    return redirect(url_for("guestbook"))


# =========================================================
# EDIT BUKU TAMU
# =========================================================

@app.route("/buku-tamu/edit/<int:id>", methods=["POST"])
@login_required
def edit_guest(id):

    data = request.form

    db = get_db()
    cur = db.cursor()


    cur.execute("""
        UPDATE guestbook
        SET
            name=%s,
            origin=%s,
            purpose=%s,
            visit_date=%s,
            entry_time=%s,
            exit_time=%s,
            note=%s
        WHERE id=%s
    """, (
        data["name"],
        data["origin"],
        data["purpose"],
        data["visit_date"],
        data["entry_time"],
        data.get("exit_time") or None,
        data["note"],
        id
    ))


    db.commit()

    cur.close()
    db.close()


    flash(
        "Data tamu berhasil diperbarui.",
        "success"
    )

    return redirect(url_for("guestbook"))


# =========================================================
# HAPUS BUKU TAMU
# =========================================================

@app.route("/buku-tamu/hapus/<int:id>", methods=["POST"])
@login_required
def delete_guest(id):

    db = get_db()
    cur = db.cursor()


    cur.execute(
        "DELETE FROM guestbook WHERE id=%s",
        (id,)
    )


    db.commit()

    cur.close()
    db.close()


    flash(
        "Data tamu berhasil dihapus.",
        "success"
    )

    return redirect(url_for("guestbook"))


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )