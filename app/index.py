from flask import redirect, render_template, request, session, jsonify
from flask_login import login_user
from app import app, login, dao, utils
from app.models import LoaiTaiKhoan

@app.route("/")
def trang_chu():
    return render_template('index.html')

@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def get_user(user_id):
    return dao.get_tk_nhan_vien_by_id(user_id)

# @app.context_processor
# def common_response():
#     return {
#         'theloai': dao.get_the_loai(),
#         'giohang': dao.get_gio_hang()
#     }

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)