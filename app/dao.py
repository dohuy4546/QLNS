from app.models import TaiKhoanNhanVien, LoaiTaiKhoan

import hashlib


def get_tk_nhan_vien_by_id(user_id):
    return TaiKhoanNhanVien.query.get(user_id)


def auth_user(username, password, loaitaikhoan):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    print(loaitaikhoan)
    if loaitaikhoan == LoaiTaiKhoan.ADMIN:
        return TaiKhoanNhanVien.query.filter(TaiKhoanNhanVien.username.__eq__(username.strip()),
                                             TaiKhoanNhanVien.password.__eq__(password),
                                             TaiKhoanNhanVien.user_role.__eq__(LoaiTaiKhoan.ADMIN)).first()

    if loaitaikhoan == LoaiTaiKhoan.KHACHHANG:
        pass
