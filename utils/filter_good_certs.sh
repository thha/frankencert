#!/bin/sh

for f in test_certs/*
do
	err_msg=`openssl verify $f | grep error`
	if test "$err_msg" = ""; then
		echo $f is good
		cp $f valid_certs
	fi
done


