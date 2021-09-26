from math import sqrt,log10
from subprocess import call,STDOUT
import base64
import argparse
import io
import os
import PIL.Image as Image
import prima
import numpy as np
import cv2
import shutil

#python acak.py encrypt ./lena.bmp 1leomaumakan
#python acak.py decrypt ./stegonya.png

def pisahteks(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

def frame_extract(video):
    temp_folder = 'temp'
    try:
        os.mkdir(temp_folder)
    except OSError:
        remove(temp_folder)
        os.mkdir(temp_folder)

    vidcap = cv2.VideoCapture("citra/"+str(video))
    count = 0

    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1

def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path):
        os.remove(path)  # buang filenya
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("File {} tidak ditemukan.".format(path))

def bacaPesan(pesan):
    A = []
    for i in pesan:
        A.append(format(ord(i), '08b'))
    return A

def pbb(a,b):
    if(b==0):
        return a
    else:
        return pbb(b,a%b)

def prng(banyak_frame, panjang_pesan, kunci):
    xo = 0
    for i in range (len(kunci)):
        xo += ord(kunci[i])
    xo %= banyak_frame
    found = False
    faktor = round(banyak_frame**(0.5))

    #Pembangkit bilangan acak pendekatan RSA
    p = prima.driver(faktor)
    q = prima.driver(faktor)
    r = (p-1)*(q-1)
    while(found == False):
        e = 2
        while(e < 10 and found == False):
            if(pbb(e,r) == 1):
                found = True
            else:
                e += 1
    hasil = []
    for i in range (panjang_pesan):
        #print(hasil)
        #print("i =",i)
        if(i == 0):
            kandidat = xo
        else:
            kandidat = (hasil[i-1]**e)%r
        while((kandidat in hasil) or kandidat<=0):
            kandidat += hasil[-1]
            kandidat %= banyak_frame
        #print("kandidat", kandidat)
        hasil.append(kandidat)
    return hasil

def stegoing(kode, gambar, key):
    pesan = bacaPesan(str(kode) + key)
    pixel = iter(gambar)

    for i in range(len(pesan)):
        gambar = [value for value in pixel.__next__()[:3] +
                                pixel.__next__()[:3] +
                                pixel.__next__()[:3]]
        #Sisipkan kode acak/sekuensial pada pixel 0,0
        #awalgambar = gambar[seed[0]]
        #print(gambar)
        for j in range(0, 8):
            if (pesan[i][j] == '0' and gambar[j]% 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                #print("gambar[j]=",gambar[j])
                gambar[j] -= 1
            elif (pesan[i][j] == '1' and gambar[j] % 2 == 0):
                if(gambar[j] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    gambar[j] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    gambar[j] += 1
        #Dikasih flag di akhir apakah message sudah habis atau belum
        #[bit ke 1-8 (isi pesan), bit ke-9 (flag baca pesan)]
        #FLAG: 1 kalau habis, 0 kalau masih ada
        if (i == len(pesan) - 1):
            if (gambar[-1] % 2 == 0):
                if(gambar[-1] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    gambar[-1] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    gambar[-1] += 1
        else:
            if (gambar[-1] % 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                gambar[-1] -= 1
        
        gambar = tuple(gambar)
        yield gambar[0:3]
        yield gambar[3:6]
        yield gambar[6:9]

def encrypt(file, pesan, kunci):
    print("Mulai ekstraksi")
    panjang_pesan = 90
    pesannya =  pisahteks(pesan,panjang_pesan)
    print(pesannya[0])
    DIR = 'temp'
    jumlah_frame = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
    kode = "a" #kode acak
    seedgambar = prng(jumlah_frame, len(pesannya), kunci)
    iterator = 0
    for teks in pesannya:
        print("Encrypt teks ke", iterator)
        img2 = Image.open(str(DIR) +"/" + str(seedgambar[iterator]) + ".png", 'r')
        img = img2.getdata()
        if (len(teks) == 0):
            raise ValueError('citra is empty')
        
        imgbaru = img2.copy()
        panjang = imgbaru.size[0]
        lebar = imgbaru.size[1]
        (x, y) = (0, 0)

        for pixel in stegoing(kode, img, teks):
            imgbaru.putpixel((x, y), pixel)
            if (x == lebar - 1):
                x = 0
                y += 1
            else:
                x += 1
        imgbaru.save(str(DIR) +"/" + str(seedgambar[iterator]) + ".png", compress_level = 0)
        iterator += 1
    #print("Nilai PSNR adalah:",psnr(cv2.imread(file),cv2.imread("stegonya.png")))

def psnr(imageawal,imageakhir):
    rms = np.mean((imageawal - imageakhir) ** 2)
    return 20*log10(255/rms)

def decrypt(file, kunci):
    img = Image.open(file, 'r')
    pesan = ''

    imagenya = []
    imagenya = listgambar(img.getcitra())

    xo = 0
    for i in range (len(kunci)):
        xo += ord(kunci[i])
    found = False
    selesai = False
    faktor = round(len(imagenya)**(0.5))

    #Pembangkit bilangan acak pendekatan RSA
    p = prima.driver(faktor)
    q = prima.driver(faktor)
    r = (p-1)*(q-1)
    while(found == False):
        e = 2
        while(e < 10 and found == False):
            if(pbb(e,r) == 1):
                found = True
            else:
                e += 1

    gambar = imagenya[0]

    # string of binary citra
    teksbinary = ''
    for i in gambar[:8]:
        if (i % 2 == 0):
            teksbinary += '0'
        else:
            teksbinary += '1'
    kode = chr(int(teksbinary, 2))

    if (kode == "a"):
        hasil = [0]
        k = 0
        while(True):
            if(k == 0):
                kandidat = xo
            else:
                kandidat = (hasil[k]**e)%r
            while(kandidat in hasil):
                kandidat += hasil[-1]
                kandidat %= len(imagenya)
            hasil.append(kandidat)
            gambar = imagenya[hasil[k+1]]
            # string of binary citra
            teksbinary = ''

            for i in gambar[:8]:
                if (i % 2 == 0):
                    teksbinary += '0'
                else:
                    teksbinary += '1'
            pesan += chr(int(teksbinary, 2))
            if (gambar[-1] % 2 != 0):
                return pesan
            else:
                k += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,)
    subparsers = parser.add_subparsers(dest="command")

    encrypt_parser = subparsers.add_parser(
        "encrypt", help=encrypt.__doc__
    )
    encrypt_parser.add_argument("file_input", help='Input Plain File')
    encrypt_parser.add_argument("pesan", help='Input Plain File')
    encrypt_parser.add_argument("kunci", help='Masukkan kuncinya')

    decrypt_parser = subparsers.add_parser(
        "decrypt", help=decrypt.__doc__
    )
    decrypt_parser.add_argument("file_input", help='Input Plain File')
    decrypt_parser.add_argument("kunci", help='Masukkan kuncinya')
    #parser.add_argument("command", help='Input command encrypt/decrypt')
    args = parser.parse_args()
    if(args.command == "encrypt"):
        file_name = args.file_input
        try:
            open("citra/" + file_name)
        except IOError:
            print("Maaf! File tidak ada")
            exit()
        print("Extract Videonya...")
        frame_extract(str(file_name))
        print("Extract Video Selesai")

        print("Extract audionya...")
        call(["ffmpeg", "-i", "citra/" + str(file_name), "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)
        print("Extract Audio Selesai")
        
        encrypt(args.file_input, args.pesan, args.kunci)

        print("Merging Gambarnya...")
        call(["ffmpeg", "-i", "temp/%d.png" , "-vcodec", "png", "temp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)
        print("Merging gambar selesai")
        
        print("Gabung Video dan Audionya")
        call(["ffmpeg", "-i", "temp/video.mov", "-i", "temp/audio.mp3", "-codec", "copy","citra/enc-" + str(file_name)+".avi", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)

    elif(args.command == "decrypt"):
        print(decrypt(args.file_input, args.kunci))