import smtplib
from email.message import EmailMessage

def send_mail(mailto, otp):
    email_from = 'dohuy4547@gmail.com' #email người gửi
    email_to = mailto # email người nhận
    password = 'imha kzyy wzne oitx' # password phải sinh ra trong bảo vệ 2 lớp bảo mật của google
    subject = 'Email xác nhận tài khoản'
    body = 'Mã xác nhận của bạn là: ' + str(otp)
    em = EmailMessage()
    em['From'] = email_from
    em['To'] = email_to
    em['Subject'] = subject
    em.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()  # Định danh trong stmp server
        smtp.starttls()  # Thiết lập kết nối smtp trong chế độ TLS
        smtp.login(email_from, password)  # Đăng nhập vào tài khoản email sender
        smtp.send_message(em) # Gửi mail
        print('Check your email ;)')