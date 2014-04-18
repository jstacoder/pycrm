import os
import getpass
from hashlib import new
from random import random
from functools import wraps


def login_required(view):
    @wraps
    def wrapper(*args, **kwargs)


def get_hex_digest(algo,salt,raw):
    if algo is None:
        algo = 'sha1'
    h = new(algo)
    h.update(salt+raw)
    return h.hexdigest()

def check_password(raw_pw,enc_pw):
    algo,salt,hsh = enc_pw.split('$')
    return hsh == get_hex_digest(algo,salt,raw_pw)

def get_salt(seed1=None,seed2=None,algo=None):
    if seed1 is None:
        seed1 = str(random())
    if seed2 is None:
        seed2 = str(random())
    return get_hex_digest(algo,seed1,seed2)[:5]

def encrypt_password(raw_pw,algo='sha1',seed1=None,seed2=None):
    salt = get_salt(seed1,seed2,algo)
    hsh = get_hex_digest(algo,salt,raw_pw)
    return '%s$%s$%s' % (algo,salt,hsh)


if __name__ == "__main__":
    tmp = os.system('clear')
    pw1 = encrypt_password(getpass.getpass("please enter first pw: "))
    pw2 = getpass.getpass("please enter second pw: ")
    print "The passwords you entered were",
    if not check_password(pw2,pw1):
        msg = 'not the same!'
    else:
        msg = 'the same.'
    print msg

