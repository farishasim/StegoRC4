class KeyStream():

    def __init__(self):
        self.N = 256
        self.key = [i for i in range(self.N)]
        self.i = 0
        self.j = 0
        self.counter = 0
        self.factor = 256

    def print(self):
        print(self.key)

    def reset(self):
        self.key = [i for i in range(self.N)]
        self.i = 0
        self.j = 0
        self.counter = 0

    def reset_index(self):
        self.i = 0
        self.j = 0

    def permute(self, K:str):
        j = 0
        for i in range(self.N):
            j = (j + self.key[i] + ord(K[i % len(K)])) % len(self.key)
            self.key[i], self.key[j] = self.key[j], self.key[i] 
        self.factor = 1 << (len(K) % 8) 

    def generate(self):
        self.i = (self.i + 1) % self.N  
        self.j = (self.j + self.key[self.i]) % self.N
        self.key[self.i], self.key[self.j] = self.key[self.j], self.key[self.i]
        t = (self.key[self.i] + self.key[self.j]) % self.N 

        self.counter += 1
        ctr = (self.counter // self.factor) % self.N

        return self.key[t] ^ ctr

def xor(a, b):
    # return a ^ b
    return (a & ~b) | (~a & b)

def bytes2str(bytearr:bytes) -> str:
    return "".join([chr(i) for i in bytearr])

def str2bytes(string:str) -> bytes:
    return [ord(i) for i in string]

def encrypt(plain:bytes, key:str) -> bytes:
    cipher = b''
    KS = KeyStream()
    KS.permute(key)
    for p in plain:
        k = KS.generate()
        c = p ^ k
        cipher += c.to_bytes(1, "little")
    return cipher

def encrypt_text(plaintext:str, key:str) -> str:
    result = bytes2str(encrypt(str2bytes(plaintext), key))
    print("plaintext:", plaintext)
    print("encrypted:", str2bytes(result))
    return result

def decrypt(cipher:bytes, key:str) -> bytes:
    plain = b''
    KS = KeyStream()
    KS.permute(key)
    for c in cipher:
        k = KS.generate()
        p = c ^ k
        plain += p.to_bytes(1, "little")
    return plain

def decrypt_text(ciphertext:str, key:str) -> str:
    return bytes2str(encrypt(str2bytes(ciphertext), key))

def printfile(filename:str, buffer:str):
    with open(filename, "wb") as file:
        file.write(buffer)

if __name__ == '__main__':
    openmode = "rb"
    filename = "dump/blue.png"

    plain = open(filename, openmode).read()
    key = "thisissecretkey"
    
    cipher = encrypt(plain, key)
    result = decrypt(cipher, key)

    printfile("dump/output", result)