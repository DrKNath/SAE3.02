import random
from sympy import isprime, mod_inverse
import math

class crypto: 
    def __init__(self, bits=8):
        self.bits = bits
        self.public_key, self.private_key = self.gen_key()
    
    @property
    def public(self):
        """Exposer uniquement la clé publique en lecture seule"""
        return self.public_key
    
    @property
    def prive(self):
        """Exposer uniquement la clé privée en lecture seule"""
        return self.private_key
    
    def gen_prime(self, bits: int = None):
        if bits is None:
            bits = self.bits
        while True: 
            n = random.getrandbits(bits)
            if isprime(n):
                break
        return n
    
    def gen_key(self):
        p = self.gen_prime()
        q = self.gen_prime()
        phi = (p-1) * (q-1)
        n = p * q
        e = 65537
        if phi % e == 0:
            e = 3
        while phi % e == 0:
            e += 2
        d = mod_inverse(e, phi)
        public_key = (e, n)
        private_key = (d, n)
        return public_key, private_key
    
    def encrypt(self, message: str, pub_key=None):
        if pub_key is None:
            pub_key = self.public_key
        e, n = pub_key
        encrypted = [pow(ord(c), e, n) for c in message]
        # Convertir la liste en string avec des virgules
        return ','.join(map(str, encrypted))
    
    def decrypt(self, cipher_str: str):
        # Convertir la string en liste de nombres
        cipher = [int(x) for x in cipher_str.split(',')]
        d, n = self.private_key
        decrypted = ''.join(chr(pow(v, d, n)) for v in cipher)
        return decrypted