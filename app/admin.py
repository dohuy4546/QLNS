from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app import app, db
from app.models import Sach, TheLoai, Sach_TheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien, LoaiTaiKhoan
from flask_login import logout_user, current_user
from flask import redirect

admin = Admin(app=app, name='QUẢN LÝ NHÀ SÁCH', template_mode='bootstrap4')


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedAdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN

class SachView(AuthenticatedAdmin):
    column_display_pk = True
    can_create = True
    column_list = ['id', 'tensach', 'gia', 'soluongtonkho', 'nhaxuatban', 'sach_theloai1']
    column_labels = {
        'id': 'ID',
        'tensach': 'Tên sách',
        'gia': 'Giá',
        'soluongtonkho': 'Số lượng tồn kho',
        'tacgia': 'Tác giả',
        'sach_theloai1': 'Thể loại',
        'mota': 'Mô tả',
        'ngayphathanh': 'Ngày phát hành',
        'nhaxuatban': 'Nhà xuất bản',
        'anhbia': 'Ảnh bìa'
    }
    can_export = True
    column_searchable_list = ['tensach']
    column_filters = ['gia', 'tensach']
    column_editable_list = ['id', 'tensach', 'gia', 'anhbia', 'soluongtonkho']
    details_modal = True
    edit_modal = True
    form_columns = ['id', 'tensach', 'tacgia', 'nhaxuatban', 'ngayphathanh', 'gia', 'anhbia', 'soluongtonkho', 'mota']


class TheLoaiView(AuthenticatedAdmin):
    column_list = ['id', 'tentheloai', 'ngaykhoitao']
    can_export = True
    column_searchable_list = ['tentheloai']
    column_filters = ['tentheloai']
    column_editable_list = ['tentheloai']
    form_columns = ['tentheloai', 'ngaykhoitao']
    details_modal = True
    edit_modal = True


class Sach_TheLoaiView(AuthenticatedAdmin):
    column_list = ['id', 'sach_id', 'theloai_id']
    can_export = True


class NhanVienView(AuthenticatedAdmin):
    column_list = ['id', 'CCCD', 'hoten', 'gioitinh', 'taikhoannhanvien']
    form_columns = ['CCCD', 'hoten', 'gioitinh']


class LogoutView(AuthenticatedAdminBaseView):
    @expose("/")
    def index(self):
        logout_user()

        return redirect('/admin')


admin.add_view(SachView(Sach, db.session, name='Sách'))
admin.add_view(TheLoaiView(TheLoai, db.session))
admin.add_view(Sach_TheLoaiView(Sach_TheLoai, db.session))
admin.add_view((AuthenticatedAdmin(TaiKhoanNhanVien, db.session)))
admin.add_view((NhanVienView(NhanVien, db.session)))
admin.add_view(LogoutView(name='Đăng xuất'))