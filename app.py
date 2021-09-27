from flask import *
from cipher import rc4
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["UPLOAD_FOLDER"]='dump'

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/rc4')
def rc4_page():
    return render_template("rc4.html")

@app.route('/rc4/encrypt')
def rc4_encrypt():
    plaintext = request.args.get("text")
    key = request.args.get("key")
    return rc4.encrypt_text(plaintext, key)

@app.route('/rc4/decrypt')
def rc4_decrypt():
    ciphertext = request.args.get("text")
    key = request.args.get("key")
    return rc4.decrypt_text(ciphertext, key)

@app.route('/rc4/file_encrypt', methods=["POST"])
def rc4_encrypt_file():
    if request.method == 'POST':
        key = request.form.get("key")
        f = request.files['file']
        f.save("dump/input")
        f = open(f"dump/input", "rb")
        plain = f.read();
        cipher = rc4.encrypt(plain, key)
        print(cipher)
        open("dump/output", "wb").write(cipher)
        return render_template("rc4.html", file_encrypt=True)
    return 

@app.route('/rc4/file_decrypt', methods=["POST"])
def rc4_decrypt_file():
    if request.method == 'POST':
        key = request.form.get("key")
        f = request.files['file']
        f.save("dump/input")
        f = open(f"dump/input", "rb")
        plain = f.read();
        cipher = rc4.encrypt(plain, key)
        print(cipher)
        open("dump/output", "wb").write(cipher)
        return render_template("rc4.html", file_decrypt=True)
    return 

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(current_app.root_path + "/" + app.config["UPLOAD_FOLDER"])
    return send_from_directory(path, filename=filename)


@app.route('/stegano')
def stegano_page():
    return render_template("stegano.html")



if __name__ == "__main__":
    app.run(debug=True)