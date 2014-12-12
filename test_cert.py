#!/usr/bin/env python

import argparse
import csv
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


def run_server_func(cert_path, cert_num, port_num):
    os.system("python utils/test_ssl_server.py {}/frankencert-{}.pem {}".format(cert_path, cert_num, port_num))


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





parser = argparse.ArgumentParser()
parser.add_argument("--gen_method", choices=["original", "improved"], default="original")
parser.add_argument("cert_path")
parser.add_argument("base_portnum", type=int)
parser.add_argument("cert_num", type=int, nargs="+")
parser.add_argument("--out", dest="outfile")
parser.add_argument("--repeat", type=int, default=1)

args = parser.parse_args()

if args.gen_method == "original":
    generator = "frankengen/franken_generate.py"
else:
    generator = "frankengen/franken_generate_r.py"

f = None
csvw = None
if args.outfile:
    f = open(args.outfile, "w")
    csvw = csv.writer(f)

if csvw:
    csvw.writerow(["cert_num", "openssl", "gnutls", "diff"])

for cert_num in args.cert_num:
    for r in range(args.repeat):
        os.system("python {} \
                utils/valid_certs/ utils/rootCA_key_cert.pem \
                {} {}".format(generator, args.cert_path, cert_num))
        sp = []
        test_rel = {}
        for i in range(cert_num):
            print "Test cert {}".format(i)

            for pnum in [args.base_portnum, args.base_portnum + 1]:
                p = Process(target=run_server_func, args=(args.cert_path, i, pnum))
                p.start()
                sp.append(p)

            time.sleep(1)
            r1 = test_openssl(i, args.base_portnum)
            r2 = test_gnutls(i, args.base_portnum + 1)

            test_rel[i] = (r1, r2)

            for p in sp:
                p.join()

            sp = sp[:]


        count = 0
        accept = [0, 0]
        for k, v in test_rel.iteritems():
            print "Cert {}: ({}, {})".format(k, v[0], v[1])
            if v[0] != v[1]:
                count += 1
            for i in range(len(v)):
                if v[i] != 0:
                    accept[i] += 1


        print "Differential count: ", count
        print "Accept count: " , accept[0], accept[1]
        if csvw:
            csvw.writerow([cert_num, accept[0], accept[1], count])

if f:
    f.close()
