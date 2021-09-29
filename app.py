from flask import *
from cipher import rc4
from StegoAcak import acakgambar, acakvideo, prima
from werkzeug.utils import secure_filename
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["UPLOAD_FOLDER"]='dump'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS_CITRA = set(['png', 'bmp'])
ALLOWED_EXTENSIONS_VIDEO = set(['avi'])

@app.route('/')
def home():
    return render_template("home.html")

#--------------------RC4----------------------------

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
        plain = f.read()
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
        plain = f.read()
        cipher = rc4.encrypt(plain, key)
        print(cipher)
        open("dump/output", "wb").write(cipher)
        return render_template("rc4.html", file_decrypt=True)
    return 

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(current_app.root_path + "/" + app.config["UPLOAD_FOLDER"])
    return send_from_directory(path, filename=filename)

#----------------Steganography------------------
@app.route('/stegano')
def stegano_page():
    return render_template("stegano.html")

@app.route('/stegano/enkripsi')
def stego_enkripsi_page():
    return render_template("stego_enc.html")

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CITRA):
        return "gambar"
    elif('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_VIDEO):
	    return "video"
    else:
        return "null" 

@app.route('/stegano/enkripsi', methods=["POST"])
def citra_encrypt():
    if request.method == 'POST':
        key = request.form.get("key")
        pesan = request.form.get("pesan")
        tipe = request.form.get("tipe_enc")
        sebaran = request.form.get("sebaran")
        f = request.files['file']
        if f and (allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join("static","images" ,filename))
            if(sebaran == "acak"):
                if(tipe == "tanpaenkripsi"):
                    acakgambar.encrypt(os.path.join("static","images" ,filename), 
                                        pesan, 
                                        key, 
                                        os.path.join("static","images","enc-"+filename))
                elif(tipe == "denganenkripsi"):
                    pesan_rc4 = rc4.encrypt_text(pesan, key)
                    acakgambar.encrypt(os.path.join("static","images",filename), 
                                        pesan_rc4, 
                                        key, 
                                        os.path.join("static","images","enc-"+filename))
            #print('upload_image filename: ' + filename)
            #flash('Gambar berhasil diupload')
            return render_template('stego_enc.html', filename=filename, encrypt=True)
            # f.save("dump/input")
            # f = open(f"dump/input", "rb")
            # plain = f.read()
            # cipher = rc4.encrypt(plain, key)
            # print(cipher)
            # open("dump/output", "wb").write(cipher)
            # return render_template("stego_enc.html", file_decrypt=True)
        elif(f and (allowed_file(f.filename)=="video")):
            filename = secure_filename(f.filename)
            f.save(os.path.join("static","videos" ,filename))
            if(sebaran == "acak"):
                if(tipe == "tanpaenkripsi"):
                    acakvideo.encrypt_driver(os.path.join("static","videos" ,filename), 
                                        pesan, 
                                        key, 
                                        os.path.join("static","videos","enc-"+filename))
                elif(tipe == "denganenkripsi"):
                    pesan_rc4 = rc4.encrypt_text(pesan, key)
                    acakvideo.encrypt_driver(os.path.join("static","videos",filename), 
                                        pesan_rc4, 
                                        key, 
                                        os.path.join("static","videos","enc-"+filename))

@app.route('/stegano/enkripsi/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='images/'+filename))

@app.route('/stegano/enkripsi/display/<filename>')
def display_video(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='videos/'+filename))

@app.route('/stegano/dekripsi')
def stego_dekripsi_page():
    return render_template("stego_dec.html")

@app.route('/stegano/dekripsi', methods=["POST"])
def citra_decrypt():
    if request.method == 'POST':
        key = request.form.get("key")
        tipe = request.form.get("tipe_enc")
        f = request.files['file']
        if f and (allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join("static","images" ,filename))
            if(tipe == "tanpadekripsi"):
                return acakgambar.decrypt(os.path.join("static","images",filename), key)
            elif(tipe == "dengandekripsi"):
                ciphernya = acakgambar.decrypt(os.path.join("static","images",filename), key)
                pesan_rc4 = rc4.decrypt_text(ciphernya, key)
                return (pesan_rc4)
            #print('upload_image filename: ' + filename)
            #flash('Gambar berhasil diupload')
            #return render_template('stego_dec.html', encrypt=True)
            # f.save("dump/input")
            # f = open(f"dump/input", "rb")
            # plain = f.read()
            # cipher = rc4.encrypt(plain, key)
            # print(cipher)
            # open("dump/output", "wb").write(cipher)
            # return render_template("stego_enc.html", file_decrypt=True)
        elif(f and (allowed_file(f.filename)=="video")):
            filename = secure_filename(f.filename)
            f.save(os.path.join("static","videos" ,filename))
            if(tipe == "tanpadekripsi"):
                return acakvideo.decrypt_driver(os.path.join("static","videos" ,filename), 
                                    key, 
                                    os.path.join("static","videos","enc-"+filename))
            elif(tipe == "dengandekripsi"):
                ciphernya = acakvideo.decrypt_driver(os.path.join("static","videos",filename), 
                                    pesan_rc4, 
                                    key, 
                                    os.path.join("static","videos","enc-"+filename))
                pesan_rc4 = rc4.decrypt_text(ciphernya, key)
                return (pesan_rc4)

@app.route('/stegano/dekripsi/display/<filename>')
def display_dec_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='images/'+filename))

@app.route('/stegano/dekripsi/display/<filename>')
def display_dec_video(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='videos/'+filename))

if __name__ == "__main__":
    app.run(debug=True)