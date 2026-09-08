# Question brief: Computer Vision (`mod-cv`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 26

For each topic below, write at least 4 self-check questions in
`content/questions/mod-cv.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `cv-what-is-an-image` — What is an image?

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Grids of intensity values; resolution and aspect ratio consequences
- Context: Grids of intensity values; resolution and aspect ratio consequences.
- Resources:
  - **PRIMARY** scikit-image — scikit-image — Image data representation with NumPy (~15 min)
    https://scikit-image.org/docs/stable/user_guide/numpy_images.html
  - **REFERENCE** Vizuara — Vizuara — Computer Vision from Scratch Intro (~29 min)
    https://www.youtube.com/watch?v=Tu11SMJGGIA
- Currently has **no questions at all**.

## `cv-pixels-channels` — Pixels & channels

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Index pixels; separate H×W×C tensor layout conventions (HWC vs CHW)
- Context: Index pixels; separate H×W×C tensor layout conventions (HWC vs CHW).
- Resources:
  - **PRIMARY** scikit-image — Image data: NumPy arrays (~15 min)
    https://scikit-image.org/docs/stable/user_guide/numpy_images.html
- Currently has **no questions at all**.

## `cv-color-spaces` — RGB & grayscale

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Channel mixing to gray; when color carries signal vs noise
- Context: Channel mixing to gray; when color carries signal vs noise.
- Resources:
  - **PRIMARY** OpenCV — Changing Colorspaces (~15 min)
    https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
- Currently has **no questions at all**.

## `cv-image-tensors` — Image tensors

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Batch tensors for networks; normalize ranges and dtype traps
- Context: Batch tensors for networks; normalize ranges and dtype traps.
- Resources:
  - **PRIMARY** Vizuara — Introduction to Computer Vision | Lecture 1 (~25 min)
    https://www.youtube.com/watch?v=lgbKpn7q40M
  - **REFERENCE** Stanford CS231n — CS231n — Input volumes, depth/height/width (~20 min)
    https://cs231n.github.io/convolutional-networks/
- Currently has **no questions at all**.

## `cv-transformations` — Image transformations

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Resize/crop/flip geometrically; interpolation artifacts awareness
- Context: Resize/crop/flip geometrically; interpolation artifacts awareness.
- Resources:
  - **PRIMARY** PyTorch — torchvision.transforms — geometric and colour transforms (~20 min)
    https://docs.pytorch.org/vision/stable/transforms.html
- Currently has **no questions at all**.

## `cv-normalization-cv` — Normalization for vision

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Match pretrained stats (mean/std per channel); avoid silent distribution drift
- Context: Match pretrained stats (mean/std per channel); avoid silent distribution drift.
- Resources:
  - **PRIMARY** Stanford CS231n — Preprocessing: normalization (~15 min)
    https://cs231n.github.io/linear-classify/
- Currently has **no questions at all**.

## `cv-augmentation` — Data augmentation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Label-preserving transforms expand data; over-augmentation destroys signal
- Context: Label-preserving transforms expand data; over-augmentation destroys signal.
- Resources:
  - **PRIMARY** D2L.ai — torchvision transforms (~20 min)
    https://d2l.ai/chapter_computer-vision/image-augmentation.html
- Currently has **no questions at all**.

## `cv-traditional-filters` — Traditional CV filters

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Edge/blur detectors before deep learning; convolution lineage starts here
- Context: Edge/blur detectors before deep learning; convolution lineage starts here.
- Resources:
  - **PRIMARY** OpenCV — Convolution as edge detection origin (~20 min)
    https://docs.opencv.org/4.13.0/d4/dbd/tutorial_filter_2d.html
- Currently has **no questions at all**.

## `cv-convolution-in-cv` — Convolution for images

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Reuse DL conv mechanics on real image grids; stride/padding effects visually
- Context: Reuse DL conv mechanics on real image grids; stride/padding effects visually.
- Resources:
  - **PRIMARY** Stanford CS231n — Convolutional layers (~25 min)
    https://cs231n.github.io/convolutional-networks/
    exact part: The Convolutional Layer
  - **SUPPLEMENT** Vizuara — Vizuara — Filters in 1D and Convolution Operation (~17 min)
    https://www.youtube.com/watch?v=P6d8NbTlEpU
- Currently has **no questions at all**.

## `cv-classification-workflow` — Image classification workflow

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Data → augment → CNN → softmax → metrics; assemble the standard loop
- Context: Data → augment → CNN → softmax → metrics; assemble the standard loop.
- Resources:
  - **PRIMARY** Stanford CS231n — Linear classification pipeline (~30 min)
    https://cs231n.github.io/linear-classify/
- Currently has **no questions at all**.

## `cv-classic-architectures` — LeNet → AlexNet → VGG

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Depth/history arc: what each added and why it mattered
- Context: Depth/history arc: what each added and why it mattered.
- Resources:
  - **PRIMARY** D2L.ai — Convolutional Neural Networks (LeNet) (~25 min)
    https://d2l.ai/chapter_convolutional-neural-networks/lenet.html
    exact part: LeNet through AlexNet-style architecture discussion
- Currently has **no questions at all**.

## `cv-resnet` — ResNet & residual learning

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Identity shortcuts defeat degradation; skip connections as gradient highways
- Context: Identity shortcuts defeat degradation; skip connections as gradient highways.
- Resources:
  - **PRIMARY** D2L.ai — Residual Networks (ResNet) (~25 min)
    https://d2l.ai/chapter_convolutional-modern/resnet.html
- Currently has **no questions at all**.

## `cv-efficientnet-awareness` — EfficientNet awareness

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Compound scaling of depth/width/resolution; know when to reach for it
- Context: Compound scaling of depth/width/resolution; know when to reach for it.
- Resources:
  - **PRIMARY** arXiv — EfficientNet — Rethinking Model Scaling for CNNs (~15 min)
    https://arxiv.org/abs/1905.11946
    exact part: architecture scaling
- Currently has **no questions at all**.

## `cv-transfer-learning-cv` — Transfer learning for vision

- Depth target: APPLICATION  ·  Track: CORE
- Objective: Freeze/fine-tune pretrained backbones; small-data wins explained
- Context: Freeze/fine-tune pretrained backbones; small-data wins explained.
- Resources:
  - **PRIMARY** D2L.ai — Fine-tuning pretrained models (~25 min)
    https://d2l.ai/chapter_computer-vision/fine-tuning.html
- Currently has **no questions at all**.

## `cv-object-detection-overview` — Object detection overview

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Classification + localization jointly; output space of boxes+classes
- Context: Classification + localization jointly; output space of boxes+classes.
- Resources:
  - **PRIMARY** D2L.ai — Bounding boxes and object detection (~20 min)
    https://d2l.ai/chapter_computer-vision/bounding-box.html
    exact part: bounding-box definition through object-detection introduction
- Currently has **no questions at all**.

## `cv-bounding-boxes-iou` — Bounding boxes & IoU

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Box formats; IoU computation by hand; matching threshold meaning
- Context: Box formats; IoU computation by hand; matching threshold meaning.
- Resources:
  - **PRIMARY** D2L.ai — Bounding boxes and object detection (~20 min)
    https://d2l.ai/chapter_computer-vision/bounding-box.html
    exact part: bounding boxes through IoU
- Currently has **no questions at all**.

## `cv-nms` — Non-maximum suppression

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Suppress duplicate detections; score-order greedy algorithm trace
- Context: Suppress duplicate detections; score-order greedy algorithm trace.
- Resources:
  - **PRIMARY** Ultralytics — Non-Maximum Suppression (NMS) (~20 min)
    https://www.ultralytics.com/glossary/non-maximum-suppression-nms
- Currently has **no questions at all**.

## `cv-two-stage-vs-one-stage` — Two-stage vs one-stage detection

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Region proposals (R-CNN family) vs direct prediction (YOLO/SSD) tradeoffs
- Context: Region proposals (R-CNN family) vs direct prediction (YOLO/SSD) tradeoffs.
- Resources:
  - **PRIMARY** D2L.ai — Single Shot Multibox Detection (~20 min)
    https://d2l.ai/chapter_computer-vision/rcnn.html
- Currently has **no questions at all**.

## `cv-yolo-concept` — YOLO family concept

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Single-shot grid predictions; speed/accuracy positioning across versions
- Context: Single-shot grid predictions; speed/accuracy positioning across versions.
- Resources:
  - **PRIMARY** Ultralytics — YOLO Explained (~20 min)
    https://docs.ultralytics.com/tasks/detect/
    exact part: object-detection through YOLO detection
- Currently has **no questions at all**.

## `cv-semantic-segmentation` — Semantic segmentation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Per-pixel classes; encoder–decoder shape recovery idea
- Context: Per-pixel classes; encoder–decoder shape recovery idea.
- Resources:
  - **PRIMARY** D2L.ai — Semantic Segmentation & transposed conv (~25 min)
    https://d2l.ai/chapter_computer-vision/transposed-conv.html
- Currently has **no questions at all**.

## `cv-u-net` — U-Net

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Skip connections fuse coarse and fine features; biomedical origin story
- Context: Skip connections fuse coarse and fine features; biomedical origin story.
- Resources:
  - **PRIMARY** D2L.ai — Fully Convolutional Networks (~25 min)
    https://d2l.ai/chapter_computer-vision/fcn.html
- Currently has **no questions at all**.

## `cv-instance-segmentation` — Instance segmentation & Mask R-CNN

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Separate overlapping instances; mask branch atop detection pipeline
- Context: Separate overlapping instances; mask branch atop detection pipeline.
- Resources:
  - **PRIMARY** D2L.ai — Instance-level task awareness via Kaggle pipeline (~25 min)
    https://d2l.ai/chapter_computer-vision/rcnn.html
- Currently has **no questions at all**.

## `cv-evaluation-metrics-cv` — CV evaluation metrics

- Depth target: MECHANICS  ·  Track: CORE
- Objective: mAP construction; per-class recall pitfalls; segmentation IoU/Dice
- Context: mAP construction; per-class recall pitfalls; segmentation IoU/Dice.
- Resources:
  - **PRIMARY** Ultralytics — Object Detection Metrics (~20 min)
    https://docs.ultralytics.com/guides/yolo-performance-metrics/
- Currently has **no questions at all**.

## `cv-vision-transformers-awareness` — Vision Transformers awareness

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Patch embeddings route images through transformer stacks; data appetite contrast
- Context: Patch embeddings route images through transformer stacks; data appetite contrast.
- Resources:
  - **PRIMARY** D2L.ai — Vision Transformers (~20 min)
    https://d2l.ai/chapter_attention-mechanisms-and-transformers/vision-transformer.html
- Currently has **no questions at all**.

## `cv-end-to-end-project` — End-to-end CV project

- Depth target: PROJECT  ·  Track: CORE
- Objective: Ship one classifier or detector: data prep → train → evaluate → reflect
- Context: Ship one classifier or detector: data prep → train → evaluate → reflect.
- Resources:
  - **PRIMARY** PyTorch — Transfer Learning for Computer Vision Tutorial (~60 min)
    https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial
- Currently has **no questions at all**.

## `cv-sift-orb-awareness` — SIFT & ORB awareness

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Keypoint descriptors before deep features; where they still win
- Context: Keypoint descriptors before deep features; where they still win.
- Resources:
  - **PRIMARY** OpenCV — Introduction to SIFT (~20 min)
    https://docs.opencv.org/4.13.0/da/df5/tutorial_py_sift_intro.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

