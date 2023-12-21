from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app import app, db
from app.models import Sach, TheLoai, Sach_TheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien
from flask_login import logout_user, current_user
from flask import redirect

admin = Admin(app=app, name='QUẢN LÝ NHÀ SÁCH', template_mode='bootstrap4')


class SachView(ModelView):
    column_display_pk = True
    can_create = True
    column_list = ['id', 'tensach', 'gia', 'anhbia', 'soluongtonkho']
    can_export = True
    column_searchable_list = ['tensach']
    column_filters = ['gia', 'tensach']
    column_editable_list = ['id', 'tensach', 'gia', 'anhbia', 'soluongtonkho']
    details_modal = True
    edit_modal = True
    form_columns = ['id', 'tensach', 'gia', 'anhbia', 'soluongtonkho']

class TheLoaiView(ModelView):
    column_list = ['id', 'tentheloai']
    can_export = True
    column_searchable_list = ['tentheloai']
    column_filters = ['tentheloai']
    column_editable_list = ['tentheloai']
    details_modal = True
    edit_modal = True

class Sach_TheLoaiView(ModelView):
    column_list = ['id', 'sach_id', 'theloai_id']
    form_columns = ['sachs', 'theloais']
    can_export = True


admin.add_view(SachView(Sach, db.session))
admin.add_view(TheLoaiView(TheLoai, db.session))
admin.add_view(Sach_TheLoaiView(Sach_TheLoai, db.session))
