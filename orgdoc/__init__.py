from argparse import ArgumentParser
import os

def sign():
    arguments_parser = ArgumentParser(description="Sign organization documents.")
    arguments_parser.add_argument("path", help="path to document")
    arguments = arguments_parser.parse_args()
    path = vars(arguments)["path"]
    directory = os.path.dirname(os.path.abspath(path)).split(os.path.sep)
    while directory:
        pubkeys_path = os.path.sep.join(directory + ["pubkeys"])
        if os.path.isdir(pubkeys_path):
            break
        directory = directory[:-1]
    privkey_path = os.path.sep.join(directory + ["pubkeys", "%s.privkey.pem" % os.getlogin()])
    if not os.path.isfile(privkey_path):
        pubkey_path = os.path.sep.join(directory + ["pubkeys", "%s.pubkey.pem" % os.getlogin()])
        os.popen2(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-pkeyopt", "rsa_keygen_pubexp:3", "-out", privkey_path])
        os.popen2(["openssl", "pkey", "-in", privkey_path, "-out", pubkey_path, "-pubout"])
    relative_path = os.path.relpath(path, start=os.path.sep.join(directory))
    signature_path = os.path.sep.join(directory + ["signatures", relative_path])
    os.popen2(["mkdir", "-p", os.path.dirname(signature_path)])
    os.popen2(["openssl", "dgst", "-sha1", "-sign", privkey_path, "-out", "%s.%s.bin" % (signature_path, os.getlogin()), path])

def verify():
    raise NotImplementedError("Feature not implemented yet!")
