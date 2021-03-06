#!/bin/bash

cat $1 \
    | sed 's/\@\@ //g' \
    | ~/GOD.util/util_token/detokenize.py -l zh \
    | python -m jieba -d 2>/dev/null \
    | ~/moses-scripts/scripts/generic/multi-bleu.perl -lc test/news.tok.zh \
    | sed -r 's/BLEU = ([0-9.]+),.*/\1/'
#  ~/moses-scripts/scripts/recaser/detruecase.perl 2> /dev/null \
#  ~/moses-scripts/scripts/tokenizer/detokenizer.perl -l en 2>/dev/null \
