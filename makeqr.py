# Import QR Code library
import qrcode
import os
from app.models import User
from app import db

def main():
    for i in range(130, 137):
        users = list()
        for u in os.listdir('app/static/img/avatar/'+str(i)):
            if u != '.DS_Store':
                users.append(os.path.splitext(u)[0])

        for u in users:
            # Create qr code instance
            qr = qrcode.QRCode(
                version = 1,
                error_correction = qrcode.constants.ERROR_CORRECT_H,
                box_size = 10,
                border = 0,
            )

            # The data that you want to store
            data = u

            # Add data
            qr.add_data(data)
            qr.make(fit=True)

            # Create an image from the QR Code instance
            img = qr.make_image()
            img = img.resize((160, 160))

            # Save it somewhere, change the extension as needed:
            # img.save("image.png")
            # img.save("image.bmp")
            # img.save("image.jpeg")
            img.save('app/static/img/qr/'+data+'_qr.jpg')
