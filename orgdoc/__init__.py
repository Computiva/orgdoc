from argparse import ArgumentParser
import subprocess
import json
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

def verify_signatures(directory, relative_path):
    path = os.path.sep.join(directory + [relative_path])
    without_signature = list()
    for key in os.listdir(os.path.sep.join(directory + ["pubkeys"])):
        if key.endswith(".pubkey.pem"):
            username = key[:-len(".pubkey.pem")]
            signature_path = os.path.sep.join(directory + ["signatures", "%s.%s.bin" % (relative_path, username)])
            if not os.path.isfile(signature_path):
                without_signature.append(username)
            else:
                pubkey_path = os.path.sep.join(directory + ["pubkeys", key])
                procw, procr = os.popen2(["openssl", "dgst", "-sha1", "-verify", pubkey_path, "-signature", signature_path, path])
                if procr.read() != "Verified OK\n":
                    without_signature.append(username)
    return without_signature

def verify_file(directory, relative_path):
    without_signature = verify_signatures(directory, relative_path)
    if without_signature:
        print "\033[31m%s\033[m" % relative_path
        for username in without_signature:
            print "\033[31m    - %s\033[m" % username
    else:
        print "\033[32m%s\033[m" % relative_path

def verify_dir(directory, relative_path):
    for child in os.listdir(os.path.sep.join(directory + [relative_path])):
        child_relative_path = os.path.sep.join([relative_path, child])
        if not child.startswith(".") and not child.endswith(".privkey.pem") and child_relative_path != "./signatures":
            path = os.path.sep.join(directory + [child_relative_path])
            if os.path.isfile(path):
                verify_file(directory, child_relative_path)
            if os.path.isdir(path):
                verify_dir(directory, child_relative_path)

def get_default_username():
    config_path = os.path.expanduser("~/.orgdoc")
    config = dict()
    if os.path.isfile(config_path):
        config.update(json.load(open(config_path)))
    try:
        return config.get("username", os.getlogin())
    except OSError:
        return config.get("username", "user")

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
        open(privkey_path, "w").close()
        os.chmod(privkey_path, 0b110000000)
        subprocess.call(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-pkeyopt", "rsa_keygen_pubexp:3", "-out", privkey_path])
        os.popen2(["openssl", "pkey", "-in", privkey_path, "-out", pubkey_path, "-pubout"])
    relative_path = os.path.relpath(path, start=os.path.sep.join(directory))
    signature_path = os.path.sep.join(directory + ["signatures", relative_path])
    os.popen2(["mkdir", "-p", os.path.dirname(signature_path)])
    os.popen2(["openssl", "dgst", "-sha1", "-sign", privkey_path, "-out", "%s.%s.bin" % (signature_path, username), path])

def verify():
    arguments_parser = ArgumentParser(description="Verify repository signatures.")
    arguments_parser.add_argument("-p", "--path", default=".", help="path to document or directory")
    arguments = arguments_parser.parse_args()
    path = vars(arguments)["path"]
    directory = get_directory(".")
    if os.path.isfile(path):
        verify_file(directory, path)
    if os.path.isdir(path):
        verify_dir(directory, path)
