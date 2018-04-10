GPU_ID=$1
ITERS=$2


time ./tools/train_net.py --gpu ${GPU_ID} \
  --solver models/solver.prototxt \
  --weights data/pretrained_model/VGG_FACE.caffemodel \
  --iters ${ITERS} \
  --snap 10000
