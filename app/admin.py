from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app import app, db
from app.models import Sach, TheLoai, Sach_TheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien
from flask_login import logout_user, current_user
from flask import redirect

admin = Admin(app=app, name='QUẢN LÝ NHÀ SÁCH', template_mode='bootstrap4')


class SachView(ModelView):
    column_list = ['id', 'tensach', 'gia', 'anhbia', 'soluongtonkho']
    can_export = True
    column_searchable_list = ['tensach']
    column_filters = ['gia', 'tensach']
    column_editable_list = ['tensach', 'gia', 'anhbia', 'soluongtonkho']
    details_modal = True
    edit_modal = True

admin.add_view(SachView(Sach, db.session))