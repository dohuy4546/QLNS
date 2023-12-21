from flask import Flask, render_template
from app import app, login


@app.route("/")
def trang_chu():
    return render_template('index.html')


@login.user_loader
def get_user(user_id):
    pass

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)