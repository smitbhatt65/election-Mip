import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "mihirsharma999@gmail.com"  # Enter your address
receiver_email = "smitbhatt65@gmail.com"  # Enter receiver address
password = input("Type your password and press enter: ")
message = """\
MIME-Version: 1.0
Content-type: text/html
Subject: verify token
<a href="/verify?token=token>click to verify the token</b>

"""



context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)