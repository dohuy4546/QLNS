from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
import enum

class LoaiTaiKhoan(enum.Enum):
    NHANVIEN = 1
    KHACHHANG = 2
    ADMIN = 3

class TaiKhoan(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(LoaiTaiKhoan))

    def __str__(self):
        self.name

class KhachHang(TaiKhoan):
    email = Column(String(100), nullable=False, primary_key=True)
    diachi = Column(String(1000), nullable=True)
    sdt = Column(String(10), nullable=True)
    hoten = Column(String(100), nullable=True)

class TheLoai(db.Model):
    id = Column(Integer, primary_key=True)
    tentheloai = Column(String(100), nullable=False)

    def __str__(self):
        return self.tentheloai

class Sach(db.Model):
    id = Column(String(10), primary_key=True)
    tensach = Column(String(100), nullable=False)
    gia = Column(Float, default=0)
    image = Column(String(100))
    soluongtonkho = Column(Integer)
    sach_theloai = relationship('Sach_TheLoai', backref='sach', lazy=True)
    def __str__(self):
        return self.tensach

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

class Sach_TheLoai(BaseModel):
    sach_id = Column(String(10), ForeignKey(Sach.id), nullable=False)
    theloai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)