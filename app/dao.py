from app.models import GioHang, Sach, TheLoai, Sach_TheLoai, TaiKhoanKhachHang, LoaiTaiKhoan, TheLoai, TaiKhoanNhanVien, \
    GioHang_Sach, HoaDon, DiaChi, SDT, ChiTietHoaDon, TacGia, NhaXuatBan, BinhLuan
from app import app, db
from sqlalchemy import func
import hashlib


def get_sach(kw=None, theloai_id=None, page=None, page_size=None, min_price=None, max_price=None, order=None):
    sachs = Sach.query
    if kw:
        sachs = sachs.filter(Sach.tensach.contains(kw))
    if theloai_id:
        sachs = sachs.filter(Sach.id.__eq__(Sach_TheLoai.sach_id)).filter(Sach_TheLoai.theloai_id.__eq__(theloai_id))
    if min_price:
        sachs = sachs.filter(Sach.gia >= min_price)
    if max_price:
        sachs = sachs.filter(Sach.gia <= max_price)
    if order == None:
        sachs = sachs.order_by(Sach.ngayphathanh.desc())
    elif order:
        if order == 'best-selling':
            sachs = sachs.outerjoin(ChiTietHoaDon, ChiTietHoaDon.sach_id.__eq__(Sach.id)).group_by(Sach.id).order_by(
                func.sum(ChiTietHoaDon.soluong).desc())
        elif order == 'title-ascending':
            sachs = sachs.order_by(Sach.tensach.asc())
        elif order == 'title-descending':
            sachs = sachs.order_by(Sach.tensach.desc())
        elif order == 'price-ascending':
            sachs = sachs.order_by(Sach.gia.asc())
        elif order == 'price-descending':
            sachs = sachs.order_by(Sach.gia.desc())
        elif order == 'created-ascending':
            sachs = sachs.order_by(Sach.ngayphathanh.asc())
        elif order == 'created-descending':
            sachs = sachs.order_by(Sach.ngayphathanh.desc())
    if page:
        page = int(page)
        if page_size is None:
            page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size
        sachs = sachs.slice(start, start + page_size)
    return sachs.all()


def get_so_luong_sach():
    return Sach.query.count()


def get_so_luong_sach_theo_the_loai():
    return db.session.query(TheLoai.id, TheLoai.tentheloai,
                            func.count(Sach_TheLoai.sach_id)) \
        .join(Sach_TheLoai,
              Sach_TheLoai.theloai_id.__eq__(TheLoai.id), isouter=True) \
        .group_by(TheLoai.id).all()


def get_sach_the_loai():
    return Sach_TheLoai.query.all()


def get_sach_by_id(sach_id):
    return Sach.query.get(sach_id)


def get_the_loai_sach_by_sach_id(sach_id):
    sach_theloai = Sach_TheLoai.query.filter(Sach_TheLoai.sach_id.__eq__(sach_id)).all()
    theloai = []
    for s in sach_theloai:
        theloai.append(TheLoai.query.get(s.theloai_id))
    return theloai


# def demo(sach_id):
#     S =  db.session.query(Sach_TheLoai.theloai_id, TheLoai.tentheloai)\
#                     .join(TheLoai, Sach_TheLoai.theloai_id.__eq__(TheLoai.id))\
#                     .filter(Sach_TheLoai.sach_id.__eq__(sach_id))\
#                     .group_by(Sach_TheLoai.theloai_id, TheLoai.tentheloai).all()
#     for s in S:
#         print(s.tentheloai)
#     return S

def get_tac_gia_by_id(tacgia_id):
    return TacGia.query.get(tacgia_id)


def get_nha_xuat_ban_by_id(nhaxuatban_id):
    return NhaXuatBan.query.get(nhaxuatban_id)


def get_tk_nhan_vien_by_id(user_id):
    return TaiKhoanNhanVien.query.get(user_id)


def get_tk_khach_hang_by_id(user_id):
    return TaiKhoanKhachHang.query.get(user_id)


def get_tk_khach_hang_by_email(user_email):
    return TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.email.__eq__(user_email)).first()


def get_so_luong_tk_khach_hang():
    return TaiKhoanKhachHang.query.count()


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


def add_tk_khach_hang(name, email, username, password):
    tk = TaiKhoanKhachHang(name=name, email=email, username=username,
                           password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()),
                           user_role=LoaiTaiKhoan.KHACHHANG)
    giohang = GioHang(taikhoankhachhang=tk)
    db.session.add(tk)
    db.session.commit()
    db.session.add(giohang)
    db.session.commit()


def doi_mat_khau_tk_khach_hang(email, password):
    tk = get_tk_khach_hang_by_email(email)
    tk.password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    db.session.commit()


def check_tai_khoan(email, username):
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


def add_gio_hang(khachhang_id, sach_id, soluong=1):
    giohang = GioHang_Sach.query.filter(GioHang_Sach.giohang_id.__eq__(khachhang_id)).filter(
        GioHang_Sach.sach_id.__eq__(sach_id)).first()
    if giohang:
        giohang.soluong += soluong
        db.session.commit()
    else:
        giohang_sach = GioHang_Sach(giohang_id=khachhang_id, sach_id=sach_id, soluong=soluong)
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
    checkdiachi = DiaChi.query.filter(DiaChi.diachi.__eq__(diachi)).filter(
        DiaChi.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()
    checksdt = SDT.query.filter(SDT.sdt.__eq__(sdt)).filter(
        SDT.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()

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

    hoadon = HoaDon(id=id, taikhoankhachhang_id=taikhoankhachhang_id, diachi=diachi, sdt=sdt,
                    tongsoluong=giohang['total_quantity'], tongtien=giohang['total_amount'])
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


def check_binh_luan(sach_id, khachhang_id):
    hoadon = HoaDon.query.filter(HoaDon.taikhoankhachhang_id.__eq__(khachhang_id)).all()
    for h in hoadon:
        chitiethoadon = ChiTietHoaDon.query.filter(ChiTietHoaDon.hoadon_id.__eq__(h.id)).filter(
            ChiTietHoaDon.sach_id.__eq__(sach_id))
        if chitiethoadon:
            return True
    return False


def them_binh_luan(sach_id, khachhang_id, binhluan):
    binhluan = BinhLuan(sach_id=sach_id, taikhoankhachhang_id=khachhang_id, noidung=binhluan)
    db.session.add(binhluan)
    db.session.commit()


def get_binh_luan(sach_id, page=None, page_size=None):
    binhluan = BinhLuan.query.filter(BinhLuan.sach_id.__eq__(sach_id))
    if page:
        page = int(page)
        if page_size is None:
            page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size
        binhluan = binhluan.slice(start, start + page_size)
    binhluan = binhluan.all()
    binhLuan = {}
    for b in binhluan:
        khachhang = TaiKhoanKhachHang.query.get(b.taikhoankhachhang_id)
        binhLuan[b.id] = {
            "tenkhachhang": khachhang.name,
            "ngaybinhluan": b.ngaykhoitao,
            "noidung": b.noidung
        }
    return binhLuan

def get_so_luong_da_ban(sach_id):
    result = (
            db.session.query(func.sum(ChiTietHoaDon.soluong))
            .filter(ChiTietHoaDon.sach_id == sach_id)
            .first()
    )
    if result and result[0] is not None:
        total_quantity = result[0]
    else:
        total_quantity = 0
    return total_quantity

def revenue_stats(kw=None):
    query = db.session.query(Sach.id, Sach.tensach, func.sum(ChiTietHoaDon.soluong*Sach.gia))\
                      .join(ChiTietHoaDon, ChiTietHoaDon.sach_id==Sach.id)

    if kw:
        query = query.filter(Sach.tensach.contains(kw))

    return query.group_by(Sach.id).all()


def revenue_mon_stats(year=2024):
    query = db.session.query(func.extract('month', HoaDon.ngaykhoitao),
                             func.sum(ChiTietHoaDon.soluong*Sach.gia))\
                      .join(ChiTietHoaDon, ChiTietHoaDon.hoadon_id.__eq__(HoaDon.id))\
                      .join(Sach, Sach.id.__eq__(ChiTietHoaDon.sach_id))\
                      .filter(func.extract('year', HoaDon.ngaykhoitao).__eq__(year))\
                      .group_by(func.extract('month', HoaDon.ngaykhoitao))
    return query.all()

if __name__ == '__main__':
    with app.app_context():
        print(get_so_luong_da_ban('VH127'))
