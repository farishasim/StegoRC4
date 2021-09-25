import base64
import argparse
import io
import PIL.Image as Image
import prima

#python acak.py encrypt ./lena.bmp 1leomaumakan
#python acak.py decrypt ./stegonya.png
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

def listgambar(image):
    L = []
    z1 = image.size[0]
    z2 = image.size[1]
    pixel = iter(image)
    
    iterator = 0

    for i in range (round((z1*z2)/3)):
        image = [value for value in pixel.__next__()[:3] +
                                    pixel.__next__()[:3] +
                                    pixel.__next__()[:3]]
        L.append(image)
    return L

def prng(senarai, pesan, kunci):
    xo = 0
    for i in range (len(kunci)):
        xo += ord(kunci[i])
    found = False
    faktor = round(len(senarai)**(0.5))

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
    hasil = [0]
    for i in range (len(pesan)):
        if(i == 0):
            kandidat = xo
        else:
            kandidat = (hasil[i]**e)%r
        while(kandidat in hasil):
            kandidat += hasil[-1]
            kandidat %= len(senarai)
        hasil.append(kandidat)
    return hasil

def stegoing(kode, gambar, seed, key):
    pesan = bacaPesan(str(kode) + key)
    #pixel = iter(gambar)

    #Sisipkan kode acak/sekuensial pada pixel 0,0
    #awalgambar = gambar[seed[0]]

    for i in range(len(pesan)):
        tempgambar = gambar[seed[i]]
        for j in range(0, 8):
            if (pesan[i][j] == '0' and tempgambar[j]% 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                tempgambar[j] -= 1
            elif (pesan[i][j] == '1' and tempgambar[j] % 2 == 0):
                if(tempgambar[j] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    tempgambar[j] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    tempgambar[j] += 1
        #Dikasih flag di akhir apakah message sudah habis atau belum
        #[bit ke 1-8 (isi pesan), bit ke-9 (flag baca pesan)]
        #FLAG: 1 kalau habis, 0 kalau masih ada
        if (i == len(pesan) - 1):
            if (tempgambar[-1] % 2 == 0):
                if(tempgambar[-1] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    tempgambar[-1] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    tempgambar[-1] += 1
        else:
            if (tempgambar[-1] % 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                tempgambar[-1] -= 1
        
        tempgambar = tuple(tempgambar)
        yield tempgambar[0:3]
        yield tempgambar[3:6]
        yield tempgambar[6:9]

def encrypt(file, pesan, kunci):
    kode = "a" #kode acak
    img = Image.open(file, 'r')
    if (len(pesan) == 0):
        raise ValueError('Data is empty')
    
    imgbaru = img.copy()
    panjang = imgbaru.size[0]
    lebar = imgbaru.size[1]
    (x, y) = (0, 0)
    
    imagenya = []
    imagenya = listgambar(imgbaru.getdata())
    seedgambar = prng(imagenya, pesan, kunci)

    #Iterasi seed pada key
    pixel_seed = 0

    for pixel in stegoing(kode, imagenya, seedgambar, pesan):
        if(pixel_seed % 3 == 0):
            x = (seedgambar[pixel_seed//3]*3)%panjang
            y = (seedgambar[pixel_seed//3]*3)//panjang
        imgbaru.putpixel((x, y), pixel)
        if (x == panjang - 1):
            x = 0
            y += 1
        else:
            x += 1
        pixel_seed += 1
    imgbaru.save('stegonya.png')

def decrypt(file, kunci):
    img = Image.open(file, 'r')
    pesan = ''

    imagenya = []
    imagenya = listgambar(img.getdata())

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

    # string of binary data
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
            # string of binary data
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
        encrypt(args.file_input, args.pesan, args.kunci)
    elif(args.command == "decrypt"):
        print(decrypt(args.file_input, args.kunci))