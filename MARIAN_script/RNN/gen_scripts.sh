SRCL=en
TGTL=th
TERM=Common
CORPUS=/data/workshop/world/tizh/corpus/handle
CORPUS=$(echo $CORPUS| sed 's/\//\\\//g')
rm -r tmp
mkdir -p tmp
cp train_en-zh.sh tmp/train_$SRCL-$TGTL.sh
cp train_en-zh.sh tmp/train_$TGTL-$SRCL.sh
cp validate-en-zh.sh tmp/validate-$SRCL-$TGTL.sh
cp validate-en-zh.sh tmp/validate-$TGTL-$SRCL.sh

# modify content
#SRCL->TGTL
TMP=s/SRCL=en/SRCL=${SRCL}/g
sed -i $TMP tmp/train_$SRCL-$TGTL.sh
sed -i $TMP tmp/validate-$SRCL-$TGTL.sh
TMP=s/TGTL=zh/TGTL=$TGTL/g
sed -i $TMP tmp/train_$SRCL-$TGTL.sh
sed -i $TMP tmp/validate-$SRCL-$TGTL.sh
#TGTL->SRCL
TMP=s/SRCL=en/SRCL=${TGTL}/g
sed -i $TMP tmp/train_$TGTL-$SRCL.sh
sed -i $TMP tmp/validate-$TGTL-$SRCL.sh
TMP=s/TGTL=zh/TGTL=$SRCL/g
sed -i $TMP tmp/train_$TGTL-$SRCL.sh
sed -i $TMP tmp/validate-$TGTL-$SRCL.sh
# term
TMP=s/TERM=Laws/TERM=$TERM/g
sed -i $TMP tmp/train_$SRCL-$TGTL.sh
sed -i $TMP tmp/validate-$SRCL-$TGTL.sh
sed -i $TMP tmp/train_$TGTL-$SRCL.sh
sed -i $TMP tmp/validate-$TGTL-$SRCL.sh
TMP='s/CORPUS_DIR=.*$/CORPUS_DIR='$CORPUS'\/'$SRCL-$TGTL'/g'
sed -i $TMP tmp/train_$SRCL-$TGTL.sh
TMP='s/CORPUS_DIR=.*$/CORPUS_DIR='$CORPUS'\/'$TGTL-$SRCL'/g'
sed -i $TMP tmp/train_$TGTL-$SRCL.sh
# GPUS
sed -i 's/^GPUS=.*$/GPUS="0 1 2 3"/g' tmp/train_$SRCL-$TGTL.sh
sed -i 's/^GPUS=.*$/GPUS="4 5 6 7"/g' tmp/train_$TGTL-$SRCL.sh
