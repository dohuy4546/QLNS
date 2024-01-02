import math
import random
import string
from datetime import datetime

from flask import redirect, render_template, request, session, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, login, dao, utils
from app.models import LoaiTaiKhoan, TaiKhoanNhanVien
from app.vnpay import vnpay


@app.route("/")
def trang_chu():
    # print(dao.get_gio_hang(current_user.id))
    # print(current_user.id)
    # cart = dao.get_total_gio_hang(current_user.id)
    # print(cart)
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
        return render_template('timkiem.html', sach=sach, pages=math.ceil(num / page_size), page=page, kw=kw)
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
                    "anhbia": s.anhbia,
                    "soluongtonkho": s.soluongtonkho
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
            "anhbia": s.anhbia,
            "soluongtonkho": s.soluongtonkho
        })
    theloai = dao.get_the_loai(theloai_id)
    num = len(dao.get_sach(kw=None, theloai_id=theloai_id))

    return render_template('theloai.html', sach=sachs, t=theloai, pages=math.ceil(num / page_size), page=page)


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.ADMIN, email=None)
    if user:
        login_user(user=user)
        session['user_role'] = "ADMIN"
    return redirect('/admin')




@app.route('/dangnhap', methods=['get', 'post'])
def dang_nhap():
    msg = request.args.get('msg', '')
    if request.method == "GET":
        if msg != '':
            return render_template('dangnhap.html', msg=msg)
        return render_template('dangnhap.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.args.get('next')
        user = dao.auth_user(username=None, password=password, loaitaikhoan=LoaiTaiKhoan.KHACHHANG, email=email)
        if type(user) is str:
            return render_template('dangnhap.html', msg=user)
        else:
            login_user(user=user)
            session['user_role'] = "KHACHHANG"

            print(next_page)
            if next_page:
                print("hello")
                return redirect(next_page)
            return redirect('/')


@app.route('/dangxuat')
def dang_xuat():
    logout_user()
    del session['user_role']
    return redirect('/')


@app.route('/otp', methods=['get', 'post'])
def otp():
    email = session['email']
    username = session['name']
    password = session['password']
    name = session['name']
    otp = session['otp']
    otp = str(otp)
    if request.method == "GET":
        msg = "Mã xác thực tài khoản của bạn là: " + otp
        subject = "Email xác nhận tài khoản"
        utils.send_mail(email, msg, subject)
        return render_template("otp.html")
    if request.method == "POST":
        input_otp = request.form.get('input_otp')

        if otp == input_otp:
            dao.dangkytaikhoankhachhang(name, email, username, password)
            del session['otp']
            del session['name']
            del session['email']
            del session['username']
            del session['password']
            return redirect(url_for('dang_nhap', msg="Tài khoản đã được dăng ký thành công!"))
        else:
            return render_template("otp.html", msg="Nhập sai mã otp")


@app.route('/dangky', methods=['get', 'post'])
def dang_ky():
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
        # dao.dangkytaikhoankhachhang(name, email, username, password)
        random_number = random.randint(10000, 99999)
        session['otp'] = random_number
        session['name'] = name
        session['email'] = email
        session['username'] = username
        session['password'] = password
        return redirect('/otp')


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    data = request.json

    sach_id = str(data.get("sach_id"))
    soluong = int(data.get("soluong"))
    khachhang_id = current_user.id
    dao.add_gio_hang(khachhang_id, sach_id, soluong)

    """
        {
            "1": {
                "id": "1",
                "name": "...",
                "price": 123,
                "quantity": 2
            },  "2": {
                "id": "2",
                "name": "...",
                "price": 1234,
                "quantity": 1
            }
        }
    """

    return jsonify(dao.get_total_gio_hang(current_user.id))

@app.route("/api/cart/<product_id>", methods=['put'])
def update_cart(product_id):
    cart = dao.get_gio_hang(current_user.id)
    if cart and product_id in cart:
        soluong = request.json.get('soluong')
        dao.update_gio_hang(current_user.id, product_id, soluong)
    return jsonify(dao.get_total_gio_hang(current_user.id))

@app.route("/api/cart/<product_id>", methods=['delete'])
def delete_cart(product_id):
    cart = dao.get_gio_hang(current_user.id)
    if cart and product_id in cart:
        dao.delete_sach_gio_hang(current_user.id, product_id)
    return jsonify(dao.get_total_gio_hang(current_user.id))

@app.route('/giohang')
def gio_hang():
    giohang = dao.get_gio_hang(current_user.id)
    msg = request.args.get('msg')
    return render_template("giohang.html", gioHang= giohang, msg=msg)

@app.route('/vnpay/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Process input data and build URL payment
        order_type = request.form['order_type']
        order_id = request.form['order_id']
        amount = float(request.form['amount'].replace(',', ''))
        order_desc = request.form['order_desc']
        bank_code = request.form['bank_code']
        language = request.form['language']
        ipaddr = request.remote_addr

        # Build URL Payment
        vnp = vnpay()  # Replace Vnpay() with the actual Vnpay object from your library
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'I7B7Y3V2'  # Replace with your TMN code
        vnp.requestData['vnp_Amount'] = int(amount * 100)
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = order_id
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type

        # Check language, default: vn
        if language and language != '':
            vnp.requestData['vnp_Locale'] = language
        else:
            vnp.requestData['vnp_Locale'] = 'vn'

        # Check bank_code, if bank_code is empty, the customer will select a bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData['vnp_BankCode'] = bank_code

        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = 'http://127.0.0.1:5000/payment_return'  # Replace with your return URL
        vnpay_payment_url = vnp.get_payment_url('https://sandbox.vnpayment.vn/paymentv2/vpcpay.html', 'FCSMFKVRWSMMEXPIZQAVFGPUXTGVYUGS')  # Replace with your payment URL and hash secret key
        print(vnpay_payment_url)

        # Redirect to VNPAY
        return redirect(vnpay_payment_url)
    else:
        giohang = dao.get_gio_hang(current_user.id)
        current_time = datetime.now()
        id = current_user.id
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        hoadon_id = str(id) + random_string
        return render_template("payment.html", title="Thanh toán", hoadon_id=hoadon_id)

@app.route('/payment_return', methods=['GET'])
def payment_return():
    vnp = vnpay()  # Thay thế Vnpay() bằng cách tạo đối tượng Vnpay từ thư viện của bạn

    inputData = request.args
    if inputData:
        vnp.responseData = dict(inputData)
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        if vnp.validate_response("FCSMFKVRWSMMEXPIZQAVFGPUXTGVYUGS"):  # Thay YOUR_HASH_SECRET_KEY bằng secret key của bạn
            if vnp_ResponseCode == "00":
                msg = ("Đơn hàng " + order_id + " của bạn đã được thanh toán thành công.\n" + "Đơn hàng sẽ được gửi đến "
                       + str(session['diachi']) + ".\n" + "Số điện thoại liên lạc của đơn hàng: "
                       + str(session['sdt']) + "\n" + "Cảm ơn vì đã đặt hàng. Chúng tôi sẽ làm việc nhanh nhất có thể.")
                khachhang = dao.get_tk_khach_hang_by_id(current_user.id)
                subject = "Xác nhận thông tin thanh toán đơn hàng"
                utils.send_mail(khachhang.email, msg, subject)
                dao.lap_hoa_don(id=order_id, taikhoankhachhang_id=current_user.id, diachi=session['diachi'], sdt=session['sdt'])
                del session['diachi']
                del session['sdt']
                return redirect(url_for("giohang", msg="Chúc mừng bạn đã đặt hàng thành công"))
            else:
                return render_template("payment_return.html", title="Kết quả thanh toán",
                                       result="Lỗi", order_id=order_id, amount=amount,
                                       order_desc=order_desc, vnp_TransactionNo=vnp_TransactionNo,
                                       vnp_ResponseCode=vnp_ResponseCode)
        else:
            return render_template("payment_return.html", title="Kết quả thanh toán",
                                   result="Lỗi", order_id=order_id, amount=amount,
                                   order_desc=order_desc, vnp_TransactionNo=vnp_TransactionNo,
                                   vnp_ResponseCode=vnp_ResponseCode, msg="Sai checksum")
    else:
        return render_template("payment_return.html", title="Kết quả thanh toán", result="")

@app.route('/checkthongtin', methods=['post'])
def check_thong_tin():
    giohang = dao.get_gio_hang(current_user.id)
    for g in giohang.values():
        check = dao.check_hang_ton_kho(g['sach_id'], g['soluong'])
        if check is False:
            msg = "Có vẻ đã có lỗi xảy ra. Sách " + str(g['tensach']) + " không đủ hàng tồn kho."
            return redirect(url_for("giohang", msg=msg))
    sdt = request.form.get('sdt')
    diachi = request.form.get('diachi')
    phuongthucthanhtoan = request.form.get('phuongthucthanhtoan')
    if phuongthucthanhtoan == "vnpay":
        session['sdt'] = sdt
        session['diachi'] = diachi
        return redirect("/vnpay/payment")
    elif phuongthucthanhtoan == "tienmat":
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        hoadon_id = str(current_user.id) + random_string
        khachhang = dao.get_tk_khach_hang_by_id(current_user.id)
        subject = "Xác nhận thông tin thanh toán đơn hàng"
        msg = ("Đơn hàng " + hoadon_id + " của bạn đã được thanh toán thành công.\n" + "Đơn hàng sẽ được gửi đến "
               + str(diachi) + ".\n" + "Số điện thoại liên lạc của đơn hàng: "
               + str(sdt) + "\n" + "Cảm ơn vì đã đặt hàng. Chúng tôi sẽ làm việc nhanh nhất có thể.")
        utils.send_mail(khachhang.email, msg, subject)
        dao.lap_hoa_don(id=hoadon_id, taikhoankhachhang_id=current_user.id, diachi=diachi, sdt=sdt)
        return redirect(url_for("giohang", msg="Chúc mừng bạn đã đặt hàng thành công"))

@app.route('/sach/<sach_id>')
def chi_tiet_san_pham(sach_id):
    print(sach_id)
    sach = dao.get_sach_by_id(sach_id)
    tacgia = dao.get_tac_gia_by_id(sach.tacgia_id)
    nhaxuatban = dao.get_nha_xuat_ban_by_id(sach.nhaxuatban_id)
    theloai = dao.get_the_loai_sach_by_sach_id(sach_id)
    binhluan = dao.get_binh_luan(sach_id)
    return render_template('chitietsanpham.html', sach=sach, tacgia=tacgia, nhaxuatban=nhaxuatban, theLoai=theloai, binhluan=binhluan)

@app.route('/api/binhluan', methods=['post'])
@login_required
def them_binh_luan():
    data = request.json
    sach_id = str(data.get("sach_id"))
    khachhang_id = current_user.id
    binhluan = str(data.get("binhluan"))
    check = dao.check_binh_luan(sach_id, khachhang_id)
    if check is True:
        dao.them_binh_luan(sach_id, khachhang_id, binhluan)
    return jsonify(check)

@login.user_loader
def get_user(user_id):
    user_role = session.get('user_role')
    if user_role == "ADMIN":
        return dao.get_tk_nhan_vien_by_id(user_id)
    elif user_role == "KHACHHANG":
        return dao.get_tk_khach_hang_by_id(user_id)
    # user = dao.get_tk_nhan_vien_by_id(user_id)
    # if user:
    #     return user
    # else:
    #     user = dao.get_tk_khach_hang_by_id(user_id)
    #     if user:
    #         return user


@app.context_processor
def common_response():
    if current_user.is_authenticated:
        return {
            'theloai': dao.get_the_loai(),
            'giohang': dao.get_total_gio_hang(current_user.id)
        }
    return {
        'theloai': dao.get_the_loai()
    }


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
