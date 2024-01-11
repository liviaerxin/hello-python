from email.message import EmailMessage
from email.utils import make_msgid
import smtplib

# from urllib import request
# request.urlretrieve("https://www.w3schools.com/html/pic_trulli.jpg", "pic_trulli.jpg")

smtp_server = "example.com"
port = 465
sender_email = "sender@example.com"
password = "password"

receiver_email = "receiver@example.com"

images = [
    "pic_trulli.jpg",
    "pic_trulli.jpg",
    "pic_trulli.jpg",
    "pic_trulli.jpg",
]
cids = [make_msgid() for _ in images]

message = EmailMessage()
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = receiver_email

body = ""
for cid in cids:
    body += """\
        <p>
            <img src="cid:{cid}" alt="Logo" width="600" height="400"><br>
        </p>
        """.format(
        cid=cid[1:-1],
    )

message.set_content(
    """\
<html>
    <h1>Hello world! I'm sending images in email</h1>
    <body>
    {body}
    </body>
</html>
""".format(
        body=body,
    ),
    subtype="html",
)

for image, cid in zip(images, cids):
    with open(image, "rb") as fp:
        message.add_related(fp.read(), maintype="image", subtype="jpg", cid=cid)

with smtplib.SMTP_SSL(smtp_server, port) as s:
    # s.set_debuglevel(1)
    # s.ehlo()
    s.login(sender_email, password)
    s.send_message(message)
