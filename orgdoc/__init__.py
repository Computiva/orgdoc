from argparse import ArgumentParser
import subprocess
import os

def get_directory(path):
    if os.path.isdir(path):
        directory = os.path.abspath(path).split(os.path.sep)
    else:
        directory = os.path.dirname(os.path.abspath(path)).split(os.path.sep)
    while directory:
        pubkeys_path = os.path.sep.join(directory + ["pubkeys"])
        if os.path.isdir(pubkeys_path):
            return directory
        directory = directory[:-1]

def verified_file(directory, relative_path):
    path = os.path.sep.join(directory + [relative_path])
    for key in os.listdir(os.path.sep.join(directory + ["pubkeys"])):
        if key.endswith(".pubkey.pem"):
            username = key[:-len(".pubkey.pem")]
            signature_path = os.path.sep.join(directory + ["signatures", "%s.%s.bin" % (relative_path, username)])
            if not os.path.isfile(signature_path):
                return False
            pubkey_path = os.path.sep.join(directory + ["pubkeys", key])
            procw, procr = os.popen2(["openssl", "dgst", "-sha1", "-verify", pubkey_path, "-signature", signature_path, path])
            if procr.read() != "Verified OK\n":
                return False
    return True

def verify_dir(directory, relative_path):
    for child in os.listdir(os.path.sep.join(directory + [relative_path])):
        child_relative_path = os.path.sep.join([relative_path, child])
        path = os.path.sep.join(directory + [child_relative_path])
        if os.path.isfile(path):
            if verified_file(directory, child_relative_path):
                print "\033[32m%s\033[m" % child_relative_path
            else:
                print "\033[31m%s\033[m" % child_relative_path
        if os.path.isdir(path):
            verify_dir(directory, os.path.sep.join([relative_path, child]))

def get_default_username():
    return os.getlogin()

def sign():
    arguments_parser = ArgumentParser(description="Sign organization documents.")
    arguments_parser.add_argument("path", help="path to document")
    arguments_parser.add_argument("-u", "--username", default=get_default_username(), help="username of signer")
    arguments = arguments_parser.parse_args()
    path = vars(arguments)["path"]
    username = vars(arguments)["username"]
    directory = get_directory(path)
    privkey_path = os.path.sep.join(directory + ["pubkeys", "%s.privkey.pem" % username])
    if not os.path.isfile(privkey_path):
        pubkey_path = os.path.sep.join(directory + ["pubkeys", "%s.pubkey.pem" % username])
        subprocess.call(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-pkeyopt", "rsa_keygen_pubexp:3", "-out", privkey_path])
        os.popen2(["openssl", "pkey", "-in", privkey_path, "-out", pubkey_path, "-pubout"])
    relative_path = os.path.relpath(path, start=os.path.sep.join(directory))
    signature_path = os.path.sep.join(directory + ["signatures", relative_path])
    os.popen2(["mkdir", "-p", os.path.dirname(signature_path)])
    os.popen2(["openssl", "dgst", "-sha1", "-sign", privkey_path, "-out", "%s.%s.bin" % (signature_path, username), path])

def verify():
    directory = get_directory(".")
    verify_dir(directory, ".")
