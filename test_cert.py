
import os
import re
import subprocess
import sys
from multiprocessing import Process
import time

def run_server_func(cert_num):
    os.system("python utils/test_ssl_server.py output/frankencert-{}.pem 4433".format(cert_num))


def test_openssl(cert_num):
    sp = Process(target=run_server_func, args=(cert_num,))
    sp.start()
    time.sleep(1)

    p = subprocess.Popen(["openssl", "s_client", "-connect",  "localhost:4433"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.communicate()[1]
    prog = re.compile(r"verify error:num=[0-9]+:(.*)")
    result = prog.findall(output)
    for r in result:
        print r

    sp.join()

def test_gnutls(cert_num):
    sp = Process(target=run_server_func, args=(cert_num,))
    sp.start()
    time.sleep(1)

    p = subprocess.Popen(["gnutls-3.3.9/src/gnutls-cli", "-p 4433", "localhost"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.communicate()[0]
    prog = re.compile(r"- Status: (.*)")
    result = prog.search(output)

    for k in result.group(1).split("."):
        print k.strip()

    sp.join()


for i in range(10):
    print "Test cert {}".format(i)
    test_openssl(i)
    test_gnutls(i)

