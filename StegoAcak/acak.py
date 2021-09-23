import base64
import argparse
import io
import PIL.Image as Image

def bacaKunci(kunci):
    A = []
    for i in kunci:
        A.append(format(ord(i), '08b'))
    return A

def stegoing(gambar, key):
    kunci = bacaKunci(key)
    pixel = iter(gambar)

    for i in range(len(kunci)):
        gambar = [value for value in pixel.__next__()[:3] +
                                pixel.__next__()[:3] +
                                pixel.__next__()[:3]]
        for j in range(0, 8):
            if (kunci[i][j] == '0' and gambar[j]% 2 != 0):
                gambar[j] -= 1
            elif (kunci[i][j] == '1' and gambar[j] % 2 == 0):
                if(gambar[j] != 0):
                    gambar[j] -= 1
                else:
                    gambar[j] += 1
        #Dikasih flag di akhir apakah message sudah habis atau belum
        #1 kalau habis, 0 kalau masih ada
        if (i == len(kunci) - 1):
            if (gambar[-1] % 2 == 0):
                if(gambar[-1] != 0):
                    gambar[-1] -= 1
                else:
                    gambar[-1] += 1
        else:
            if (gambar[-1] % 2 != 0):
                gambar[-1] -= 1
        
        gambar = tuple(gambar)
        yield gambar[0:3]
        yield gambar[3:6]
        yield gambar[6:9]

def encrypt(file, kunci):
    img = Image.open(file, 'r')
    if (len(kunci) == 0):
        raise ValueError('Data is empty')
    
    imgbaru = img.copy()
    w = imgbaru.size[0]
    (x, y) = (0, 0)
 
    for pixel in stegoing(imgbaru.getdata(), kunci):
        imgbaru.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1
    imgbaru.save('stegonya.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("file_input", help='Input Plain File')
    parser.add_argument("kunci", help='Input Plain File')
    args = parser.parse_args()
    encrypt(args.file_input, args.kunci)