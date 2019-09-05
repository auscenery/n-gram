 #!/usr/bin/env bash

 sentence=$1 # 空格隔开的字或词粒度句子
 arpa_file_path=$2 #　相应的ａｒpa路径
 python ppl.py "$sentence" "$arpa_file_path"
