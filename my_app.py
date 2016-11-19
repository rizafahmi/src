import base64
import boto3
import calendar
import io

from datetime import datetime, timedelta
from flask import Flask, request, render_template
from PIL import Image

app = Flask(__name__)
s3 = boto3.resource('s3')
BUCKET_NAME = 'zappa-playground'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        new_file_b64 = request.form['b64file']
        if new_file_b64:
            new_file = base64.b64decode(new_file_b64)

            img = Image.open(io.BytesIO(new_file))
            img.thumbnail((200, 200))

            future = datetime.utcnow() + timedelta(days=10)
            timestamp = str(calendar.timegm(future.timetuple()))
            filename = "thumb.%s.jpg" % timestamp

            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            s3_object = s3.Object(BUCKET_NAME, filename)
            resp = s3_object.put(
                    Body=img_bytes.getvalue(),
                    ContentType='image/jpeg'
                    )

            if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
                object_acl = s3_object.Acl()
                response = object_acl.put(
                        ACL='public-read'
                        )

                object_url = "https://{0}.s3.amazonaws.com/{1}".format(BUCKET_NAME, filename)
                return object_url, 200
            else:
                return "Something went wrong :(", 400

    return render_template('upload.html')

@app.route('/')
def index():
    return "Hello, Harry!"


if __name__ == '__main__':
    app.run()
