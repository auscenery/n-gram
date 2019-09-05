#!/usr/bin/env bash

# kenlm n-gram 开发包
gram_order=$1
data_in_file_path=$2
data_out_arpa_file_path=$3
lmplz -o $1 --verbose_header --text $2 --arpa $3
