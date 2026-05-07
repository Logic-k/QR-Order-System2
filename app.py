import os
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, url_for

# Flask 애플리케이션 생성
app = Flask(__name__)

# 데이터베이스 파일 경로
DB_FILE = "app.db"

# 테이블 생성 (앱 실행 시 한 번 실행됨)
def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seat TEXT NOT NULL,
            drink TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '대기 중'
        )
    """)
    conn.commit()
    conn.close()

# 테이블 생성 실행
create_tables()

# 주문 페이지 (QR 스캔)
@app.route("/order", methods=["GET", "POST"])
def order():
    seat_number = request.args.get("seat", "1")

    if request.method == "POST":
        data = request.json
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (seat, drink) 
            VALUES (?, ?)
        """, (seat_number, data.get("drink")))
        conn.commit()
        conn.close()
        return redirect(url_for("order_complete", seat=seat_number))  # 주문 완료 후 리디렉트

    return render_template('order.html', seat_number=seat_number)

# ✅ 주문 완료 페이지 (애드핏 광고 배치)
@app.route("/order-complete")
def order_complete():
    seat_number = request.args.get("seat", "1")

    return render_template('order_complete.html', seat_number=seat_number)

# 관리자 페이지 (자리 형상화 UI)
@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders_raw = cursor.fetchall()
    conn.close()

    orders = {}
    for order in orders_raw:
        order_id, seat, drink, status = order
        if seat not in orders:
            orders[seat] = []
        orders[seat].append({"id": order_id, "drink": drink, "status": status})

    return render_template('admin.html', orders=orders)

# 개별 주문 삭제 API
@app.route("/delete-order", methods=["POST"])
def delete_order():
    order_id = request.json.get("id")
    if order_id:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "주문이 삭제되었습니다."})
    return jsonify({"error": "유효한 주문 ID가 없습니다."}), 400

# 층별 모든 주문 삭제 API
@app.route("/delete-floor-orders", methods=["POST"])
def delete_floor_orders():
    floor = request.json.get("floor")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if floor == 1:
        # 1층 좌석 삭제 (2층이 아닌 것)
        cursor.execute("DELETE FROM orders WHERE seat NOT LIKE '2층%'")
    elif floor == 2:
        # 2층 좌석 삭제
        cursor.execute("DELETE FROM orders WHERE seat LIKE '2층%'")
    conn.commit()
    conn.close()
    return jsonify({"message": f"{floor}층 모든 주문이 삭제되었습니다."})

#크롤러 허용 설정
@app.route("/robots.txt")
def robots():
	return "User-agent: *\nDisallow:", 200, {"Content-Type" : "text/plain"}

# Flask 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
