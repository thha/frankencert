#!/usr/bin/env python

import os
import re
import subprocess
import sys
from multiprocessing import Process
import time

IGNORE_ERR_MSG = {
    "openssl": [
       # "unable to get local issuer certificate",
       # "certificate not trusted",
       # "unable to verify the first certificate"
    ],
    "gnutls": [
       # "The certificate is NOT trusted",
       # "The name in the certificate does not match the expected",
       # "The certificate issuer is unknown"
       "The certificate is trusted",
    ]
}


def run_server_func(cert_num, port_num):
    os.system("python utils/test_ssl_server.py output/frankencert-{}.pem {}".format(cert_num, port_num))


def test_openssl(cert_num, port_num):
    p = subprocess.Popen(["openssl", "s_client", "-CAfile",
        "/etc/ssl/certs/ca-certificates.crt", "-connect",  "localhost:{}".format(port_num)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.communicate()[1]
    prog = re.compile(r"verify error:num=[0-9]+:(.*)")
    msg = prog.findall(output)
    result = 1
    for r in msg:
        if r not in IGNORE_ERR_MSG["openssl"]:
            print "OPENSSL:", r
            result = 0

    return result


def test_gnutls(cert_num, port_num):
    p = subprocess.Popen(["gnutls-3.3.9/src/gnutls-cli", "-p {}".format(port_num), "localhost"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.communicate()[0]
    prog = re.compile(r"- Status: (.*)")
    msg = prog.search(output)
    result = 1
    for k in msg.group(1).split("."):
        r = k.strip()
        if len(r) > 0 and r not in IGNORE_ERR_MSG["gnutls"]:
            print "GNUTLS :", r
            result = 0

    return result


sp = []
test_rel = {}
for i in range(200):
    print "Test cert {}".format(i)

    for pnum in [4433, 4434]:
        p = Process(target=run_server_func, args=(i, pnum))
        p.start()
        sp.append(p)

    time.sleep(1)
    r1 = test_openssl(i, 4433)
    r2 = test_gnutls(i, 4434)

    test_rel[i] = (r1, r2)

    for p in sp:
        p.join()

    sp = sp[:]


count = 0
for k, v in test_rel.iteritems():
    print "Cert {}: ({}, {})".format(k, v[0], v[1])
    if v[0] != v[1]:
        count += 1

print "Differential count: ", count

