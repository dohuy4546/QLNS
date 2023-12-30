from app.models import GioHang, Sach, TheLoai, Sach_TheLoai, TaiKhoanKhachHang, LoaiTaiKhoan, TheLoai, TaiKhoanNhanVien
from app import app, db

import hashlib


def get_sach(kw, theloai_id, page=None, page_size=None, min_price=None, max_price=None):
    sachs = Sach.query

    if kw:
        sachs = sachs.filter(Sach.tensach.contains(kw))

    if theloai_id:
        sachs = sachs.filter(Sach.id.__eq__(Sach_TheLoai.sach_id)).filter(Sach_TheLoai.theloai_id.__eq__(theloai_id))
    if min_price:
        sachs = sachs.filter(Sach.gia >= min_price)
    if max_price:
        sachs = sachs.filter(Sach.gia <= max_price)
    if page:
        page = int(page)
        if page_size is None:
            page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size
        sachs = sachs.slice(start, start + page_size)
    return sachs.all()


def get_soluongsach():
    return Sach.query.count()


def get_sachtheloai():
    return Sach_TheLoai.query.all()

def get_tk_nhan_vien_by_id(user_id):
    return TaiKhoanNhanVien.query.get(user_id)


def auth_user(username, password, loaitaikhoan):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(loaitaikhoan)
    if loaitaikhoan == LoaiTaiKhoan.ADMIN or loaitaikhoan == LoaiTaiKhoan.NHANVIEN:
        return TaiKhoanNhanVien.query.filter(TaiKhoanNhanVien.username.__eq__(username.strip()),
                                             TaiKhoanNhanVien.password.__eq__(password),
                                             TaiKhoanNhanVien.user_role.__eq__(loaitaikhoan)).first()

    if loaitaikhoan == LoaiTaiKhoan.KHACHHANG:
        pass


def dangkytaikhoankhachhang(name, email, username, password):
    tk = TaiKhoanKhachHang(name=name, email=email, username=username, password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()))
    giohang = GioHang(taikhoankhachhang=tk)
    db.session.add(tk)
    db.session.commit()
    db.session.add(giohang)
    db.session.commit()

def checktaikhoan(email, username):
    emailcheck = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.email.__eq__(email)).all()
    usernamecheck = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.username.__eq__(username)).all()
    msg = "Tài khoản đã tồn tại!"
    if emailcheck:
        return msg
    if usernamecheck:
        return msg
    return None
def get_the_loai(id=None):
    if id:
        return TheLoai.query.get(id)
    return TheLoai.query.all()

if __name__ == '__main__':
    with app.app_context():
        theloai = get_the_loai(1)
        print(theloai.tentheloai)



