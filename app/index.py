import math
import random
import string

from flask import redirect, render_template, request, session, jsonify, url_for
from flask_login import login_user
from app import app, login, dao, utils
from app.models import LoaiTaiKhoan

@app.route("/")
def trang_chu():
    kw = request.args.get('kw')
    theloai_id = request.args.get('theloai')
    page = request.args.get('page')
    price_filter = request.form.get('priceRange')
    sachs = {}
    page_size = app.config['PAGE_SIZE']
    if page is None:
        page = 1
    if kw:
        sach = dao.get_sach(kw, theloai_id, page)
        num = len(dao.get_sach(kw, theloai_id))
        return render_template('timkiem.html', sach=sach, pages=math.ceil(num/page_size), page=page, kw=kw)
    if theloai_id is None:
        theloai = dao.get_the_loai()
        """
        sachs = {
            "1": [{
                "sach_id": "1",
                "tensach": "home"
            },
                {
                "sach_id": "2",
                "tensach": "123"
                }
            ],
            "2": [{

            }]
        }
        """
        for t in theloai:
            sach = dao.get_sach(kw, t.id, page, 5)  # sach = nhiều sách của 1 thể loại
            sachs[t.id] = []
            for s in sach:
                sachs[t.id].append({
                    "id": s.id,
                    "tensach": s.tensach,
                    "gia": s.gia,
                    "anhbia": s.anhbia
                })
        return render_template('index.html', sach=sachs)
    sach = dao.get_sach(kw, theloai_id, page)
    sachs = {}
    sachs[theloai_id] = []
    for s in sach:
        sachs[theloai_id].append({
            "id": s.id,
            "tensach": s.tensach,
            "gia": s.gia,
            "anhbia": s.anhbia
        })
    theloai = dao.get_the_loai(theloai_id)
    num = len(dao.get_sach(kw=None, theloai_id=theloai_id))


    return render_template('theloai.html', sach=sachs, t=theloai, pages=math.ceil(num/page_size), page=page)


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')

@app.route('/dangnhap', methods=['get', 'post'])
def dangnhap():
    msg = request.args.get('msg', '')
    if request.method == "GET":
        if msg != '':
            return render_template('dangnhap.html', msg=msg)
    return render_template('dangnhap.html')
@app.route('/otp', methods=['get', 'post'])
def otp():
    email = session['email']
    username = session['name']
    password = session['password']
    name = session['name']
    otp = session['otp']

    if request.method == "GET":
        utils.send_mail(email, otp)
        return render_template("otp.html")
    if request.method == "POST":
        input_otp = request.form.get('input_otp')
        otp = str(otp)
        print(type(otp))
        print(type(input_otp))
        if otp == input_otp:
            #dao.dangkytaikhoankhachhang(name, email, username, password)
            return redirect(url_for('dangnhap', msg="Tài khoản đã được dăng ký thành công!"))
        else:
            return  render_template("otp.html", msg="Nhập sai mã otp")
@app.route('/dangky', methods=['get', 'post'])
def dangky():
    if request.method == "GET":
        return render_template('dangky.html')
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        msg = dao.checktaikhoan(email, username)
        if msg:
            return render_template("dangky.html", msg=msg)
        #dao.dangkytaikhoankhachhang(name, email, username, password)
        random_number = random.randint(10000, 99999)
        session['otp'] = random_number
        session['name'] = name
        session['email'] = email
        session['username'] = username
        session['password'] = password
        return redirect('/otp')

@login.user_loader
def get_user(user_id):
    return dao.get_tk_nhan_vien_by_id(user_id)


@app.context_processor
def common_response():
    return {
        'theloai': dao.get_the_loai()
    }


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
