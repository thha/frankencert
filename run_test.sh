#/bin/sh

if [[ $1 -eq 1 ]]; then
	./test_cert.py --gen_method original --out rel_org01.csv --repeat 5 output1 4433 200 500 1000 5000
fi

if [[ $1 -eq 2 ]]; then
	./test_cert.py --gen_method original --out rel_org02.csv --repeat 5 output2 4435 5000
fi

if [[ $1 -eq 5 ]]; then
	./test_cert.py --gen_method improved --out rel_imp01.csv --repeat 5 output3 4437 200 500 1000
fi

if [[ $1 -eq 6 ]]; then
	./test_cert.py --gen_method improved --out rel_imp02.csv --repeat 5 output4 4439 5000
fi
