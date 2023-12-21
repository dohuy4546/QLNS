from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
import enum


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class LoaiTaiKhoan(enum.Enum):
    NHANVIEN = 1
    KHACHHANG = 2
    ADMIN = 3


class TaiKhoan(db.Model, UserMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(LoaiTaiKhoan))

    def __str__(self):
        self.username


class TaiKhoanKhachHang(TaiKhoan):
    email = Column(String(100), primary_key=True)
    diachi = Column(String(1000), nullable=True)
    sdt = Column(String(10), nullable=True)
    hoten = Column(String(100), nullable=True)


class NhanVien(BaseModel):
    CCCD = Column(String(20), nullable=False, unique=True)
    hoten = Column(String(100), nullable=False)
    gioitinh = Column(Boolean, nullable=False)
    taikhoannhanvien = relationship("TaiKhoanNhanVien", back_populates="nhanvien", uselist=False)

    def __str__(self):
        return self.hoten


class TaiKhoanNhanVien(TaiKhoan):
    nhanvien_id = Column(Integer, ForeignKey(NhanVien.id), unique=True, nullable=False)
    nhanvien = relationship("NhanVien", back_populates="taikhoannhanvien", uselist=False)


class TheLoai(BaseModel):
    __tablename__ = 'theloai'
    tentheloai = Column(String(100), nullable=False, unique=True)
    sach_theloai = relationship('Sach_TheLoai', backref='theloai', lazy=True)
    def __str__(self):
        return self.tentheloai


class Sach(db.Model):
    __tablename__='sach'
    id = Column(String(10), primary_key=True, nullable=False)
    tensach = Column(String(100), nullable=False, unique=True)
    gia = Column(Float, default=0)
    anhbia = Column(String(100))
    soluongtonkho = Column(Integer)
    sach_theloai = relationship('Sach_TheLoai', backref='sach', lazy=True)

    def __str__(self):
        return self.tensach


class Sach_TheLoai(BaseModel):
    __tablename__='sach_theloai'
    sach_id = Column(String(10), ForeignKey(Sach.id), nullable=False)
    theloai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    sachs = relationship('Sach', backref='sach_theloai1', lazy=True)
    theloais = relationship('TheLoai', backref='sach_theloai2', lazy=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # sach1 = Sach(id='VH1234', tensach='Van hoc truyen thong Viet Nam', gia=100000, soluongtonkho=200)
        # db.session.add(sach1)
        # db.session.commit()
