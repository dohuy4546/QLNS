from app.models import GioHang, Sach, TheLoai, Sach_TheLoai, TaiKhoanKhachHang, LoaiTaiKhoan, TheLoai, TaiKhoanNhanVien, \
    GioHang_Sach, HoaDon, DiaChi, SDT, ChiTietHoaDon
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
    sachs = sachs.order_by(Sach.ngayphathanh.desc())
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


def get_tk_khach_hang_by_id(user_id):
    return TaiKhoanKhachHang.query.get(user_id)


def auth_user(username, password, loaitaikhoan, email):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    if loaitaikhoan == LoaiTaiKhoan.ADMIN or loaitaikhoan == LoaiTaiKhoan.NHANVIEN:
        return TaiKhoanNhanVien.query.filter(TaiKhoanNhanVien.username.__eq__(username.strip()),
                                             TaiKhoanNhanVien.password.__eq__(password),
                                             TaiKhoanNhanVien.user_role.__eq__(loaitaikhoan)).first()

    if loaitaikhoan == LoaiTaiKhoan.KHACHHANG:
        tk = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.email.__eq__(email),
                                            TaiKhoanKhachHang.password.__eq__(password)).first()
        if tk:
            return tk
        else:
            return "Tài khoản hoặc mật khẩu sai! Vui lòng nhập lại"


def dangkytaikhoankhachhang(name, email, username, password):
    tk = TaiKhoanKhachHang(name=name, email=email, username=username,
                           password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()),
                           user_role=LoaiTaiKhoan.KHACHHANG)
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


def get_gio_hang(khachhang_id):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).all()
    gioHang = {}
    for g in giohang:
        sach = Sach.query.filter(Sach.id.__eq__(g.sach_id)).first()
        gioHang[sach.id] = {
            "sach_id": sach.id,
            "tensach": sach.tensach,
            "gia": sach.gia,
            "soluong": g.soluong,
            "anhbia": sach.anhbia
        }
    return gioHang


def get_total_gio_hang(khachhang_id):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).all()
    amount = 0
    quantity = 0
    for g in giohang:
        soluong = g.soluong
        sach = Sach.query.filter(Sach.id.__eq__(g.sach_id)).first()
        gia = sach.gia
        amount += gia * soluong
        quantity += soluong
    return {
        "total_amount": amount,
        "total_quantity": quantity
    }


def add_gio_hang(khachhang_id, sach_id):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).filter(
        GioHang_Sach.sach_id.__eq__(sach_id)).first()
    if giohang:
        giohang.soluong += 1
        db.session.commit()
    else:
        giohang_sach = GioHang_Sach(giohang_id=khachhang_id, sach_id=sach_id, soluong=1)
        db.session.add(giohang_sach)
        db.session.commit()


def update_gio_hang(khachhang_id, sach_id, soluong):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).filter(
        GioHang_Sach.sach_id.__eq__(sach_id)).first()
    giohang.soluong = soluong
    db.session.commit()

def delete_sach_gio_hang(khachhang_id, sach_id):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).filter(
        GioHang_Sach.sach_id.__eq__(sach_id)).first()
    db.session.delete(giohang)
    db.session.commit()

def check_hang_ton_kho(sach_id, soluong):
    sach = Sach.query.get(sach_id)
    if sach.soluongtonkho >= soluong:
        return True
    return False

def lap_hoa_don(id, taikhoankhachhang_id, diachi, sdt):
    giohang = get_total_gio_hang(taikhoankhachhang_id)
    checkdiachi = DiaChi.query.filter(DiaChi.diachi.__eq__(diachi)).filter(DiaChi.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()
    checksdt = SDT.query.filter(SDT.sdt.__eq__(sdt)).filter(SDT.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()

    if checkdiachi is None:
        diachi = DiaChi(diachi=diachi, taikhoankhachhang_id=taikhoankhachhang_id)
        db.session.add(diachi)
    else:
        diachi = checkdiachi
    if checksdt is None:
        sdt = SDT(sdt=sdt, taikhoankhachhang_id=taikhoankhachhang_id)
        db.session.add(sdt)
    else:
        sdt = checksdt
    db.session.commit()

    hoadon = HoaDon(id=id, taikhoankhachhang_id=taikhoankhachhang_id, diachi=diachi, sdt=sdt, tongsoluong=giohang['total_quantity'], tongtien=giohang['total_amount'])
    db.session.add(hoadon)
    db.session.commit()
    gioHang = get_gio_hang(taikhoankhachhang_id)
    for g in gioHang.values():
        chitiethoadon = ChiTietHoaDon(hoadon_id=id, sach_id=g['sach_id'], soluong=g['soluong'])
        sach = Sach.query.get(g['sach_id'])
        sach.soluongtonkho -= g['soluong']
        db.session.add(chitiethoadon)
        db.session.commit()
    gioHang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(taikhoankhachhang_id)).all()
    for g in gioHang:
        db.session.delete(g)
    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        pass
