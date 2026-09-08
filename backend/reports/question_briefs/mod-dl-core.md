# Question brief: Deep Learning Core (`mod-dl-core`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 32

For each topic below, write at least 4 self-check questions in
`content/questions/mod-dl-core.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `dl-why-deep-learning` — Why deep learning?

- Depth target: AWARENESS  ·  Track: CORE
- Objective: State the problem handcrafted features could not solve; name what representation learning buys
- Context: State the problem handcrafted features could not solve; name what representation learning buys.
- Resources:
  - **PRIMARY** D2L.ai — Introduction (Dive into Deep Learning) (~15 min)
    https://d2l.ai/chapter_introduction/index.html
- Currently has **no questions at all**.

## `dl-neuron-intuition` — Neuron intuition

- Depth target: INTUITION  ·  Track: CORE
- Objective: Weighted sum + nonlinearity as a tiny decision unit; connect back to linear models
- Context: Weighted sum + nonlinearity as a tiny decision unit; connect back to linear models.
- Resources:
  - **PRIMARY** Vizuara — Lecture 1 - Neural Network from Scratch: Coding Neurons and Layers (~33 min)
    https://www.youtube.com/watch?v=zrKpz9-AZ_E
  - **REFERENCE** D2L.ai — Multilayer Perceptrons (~20 min)
    https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
- Currently has **no questions at all**.

## `dl-perceptron` — Perceptron

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Trace the perceptron learning rule on toy data; state its linear-limitation result
- Context: Trace the perceptron learning rule on toy data; state its linear-limitation result.
- Resources:
  - **PRIMARY** Vizuara — Lecture 2 - The beauty of numpy and dot product in coding neurons (~40 min)
    https://www.youtube.com/watch?v=mK_PfqM88OY
  - **REFERENCE** D2L.ai — The Perceptron (~20 min)
    https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
- Currently has **no questions at all**.

## `dl-activation-functions` — Activation functions

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Compare sigmoid/tanh/ReLU families; explain why nonlinearity is non-negotiable
- Context: Compare sigmoid/tanh/ReLU families; explain why nonlinearity is non-negotiable.
- Resources:
  - **PRIMARY** Vizuara — Lecture 6 - Coding Neural Network Activation Functions from scratch (~43 min)
    https://www.youtube.com/watch?v=SP372QpruDg
  - **REFERENCE** D2L.ai — Activation Functions (~20 min)
    https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
- Currently has **no questions at all**.

## `dl-forward-propagation` — Forward propagation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Push shapes and numbers through layer-by-layer; verify output dimension reasoning
- Context: Push shapes and numbers through layer-by-layer; verify output dimension reasoning.
- Resources:
  - **PRIMARY** D2L.ai — Forward Propagation (~25 min)
    https://d2l.ai/chapter_multilayer-perceptrons/backprop.html
    exact part: Forward Propagation
- Currently has **no questions at all**.

## `dl-loss-functions-nn` — Loss functions for networks

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Choose MSE vs cross-entropy deliberately; tie output activation to loss pairing
- Context: Choose MSE vs cross-entropy deliberately; tie output activation to loss pairing.
- Resources:
  - **PRIMARY** D2L.ai — Multilayer Perceptrons — loss and activation choices (~20 min)
    https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
    exact part: loss
- Currently has **no questions at all**.

## `dl-backprop-intuition` — Backpropagation intuition

- Depth target: INTUITION  ·  Track: CORE
- Objective: Chain rule backwards through a computational graph on paper for a 2-layer net
- Context: Chain rule backwards through a computational graph on paper for a 2-layer net.
- Resources:
  - **PRIMARY** CS231n — Backpropagation, Intuitions (~30 min)
    https://cs231n.github.io/optimization-2/
    exact part: Intuitive understanding of backpropagation
- Currently has **no questions at all**.

## `dl-computational-graphs` — Computational graphs

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Represent expressions as graphs; see how autodiff generalizes backprop
- Context: Represent expressions as graphs; see how autodiff generalizes backprop.
- Resources:
  - **PRIMARY** CS231n — Computational graphs and backpropagation (~20 min)
    https://cs231n.github.io/optimization-2/
    exact part: Compound expressions, chain rule, backpropagation through Patterns in backward flow
- Currently has **no questions at all**.

## `dl-gradient-descent-nn` — Gradient descent in networks

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Update weights end-to-end once by hand-scale; connect LR to stability
- Context: Update weights end-to-end once by hand-scale; connect LR to stability.
- Resources:
  - **PRIMARY** D2L.ai — Optimization intro: gradient descent (~20 min)
    https://d2l.ai/chapter_optimization/gd.html
- Currently has **no questions at all**.

## `dl-mlp` — Multi-layer perceptrons

- Depth target: IMPLEMENTATION  ·  Track: CORE
- Objective: Build/train an MLP mentally: hidden widths, depth, parameter counting
- Context: Build/train an MLP mentally: hidden widths, depth, parameter counting.
- Resources:
  - **PRIMARY** D2L.ai — Implementing an MLP from scratch (~25 min)
    https://d2l.ai/chapter_multilayer-perceptrons/mlp-implementation.html
- Currently has **no questions at all**.

## `dl-vanishing-gradients` — Vanishing & exploding gradients

- Depth target: INTUITION  ·  Track: CORE
- Objective: Explain saturation and depth amplification; name ReLU/residuals as mitigations
- Context: Explain saturation and depth amplification; name ReLU/residuals as mitigations.
- Resources:
  - **PRIMARY** D2L.ai — Numerical Stability and Initialization (~20 min)
    https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
    exact part: vanishing gradients
- Currently has **no questions at all**.

## `dl-initialization` — Initialization

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Xavier/He scaling keeps signal variance stable at depth-one pass
- Context: Xavier/He scaling keeps signal variance stable at depth-one pass.
- Resources:
  - **PRIMARY** D2L.ai — Parameter Initialization (~15 min)
    https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
    exact part: parameter initialization
- Currently has **no questions at all**.

## `dl-normalization` — Normalization layers

- Depth target: MECHANICS  ·  Track: CORE
- Objective: BatchNorm steadies internal distributions; LayerNorm powers transformers
- Context: BatchNorm steadies internal distributions; LayerNorm powers transformers.
- Resources:
  - **PRIMARY** D2L.ai — Batch Normalization (~20 min)
    https://d2l.ai/chapter_convolutional-modern/batch-norm.html
    exact part: Batch Normalization
- Currently has **no questions at all**.

## `dl-dropout` — Dropout

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Random deactivation as cheap ensembling; train vs inference mode distinction
- Context: Random deactivation as cheap ensembling; train vs inference mode distinction.
- Resources:
  - **PRIMARY** D2L.ai — Dropout (~15 min)
    https://d2l.ai/chapter_multilayer-perceptrons/dropout.html
- Currently has **no questions at all**.

## `dl-optimizers-sgd` — SGD & momentum

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Noisy but honest steps; momentum accumulates velocity across flat regions
- Context: Noisy but honest steps; momentum accumulates velocity across flat regions.
- Resources:
  - **PRIMARY** D2L.ai — SGD & Momentum (~20 min)
    https://d2l.ai/chapter_optimization/momentum.html
- Currently has **no questions at all**.

## `dl-optimizers-adam` — RMSProp & Adam

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Per-parameter adaptive rates; when Adam's defaults win and when SGD generalizes better
- Context: Per-parameter adaptive rates; when Adam's defaults win and when SGD generalizes better.
- Resources:
  - **PRIMARY** D2L.ai — Adam optimizer family (~20 min)
    https://d2l.ai/chapter_optimization/adam.html
- Currently has **no questions at all**.

## `dl-batch-epoch-lr` — Batch size, epochs, learning rate

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Trade noise/stability/throughput; schedule LR decay deliberately
- Context: Trade noise/stability/throughput; schedule LR decay deliberately.
- Resources:
  - **PRIMARY** D2L.ai — Learning rate schedules (~20 min)
    https://d2l.ai/chapter_optimization/lr-scheduler.html
- Currently has **no questions at all**.

## `dl-cnn-foundations` — CNN foundations

- Depth target: INTUITION  ·  Track: CORE
- Objective: Why shared weights beat dense nets on images: locality + translation structure
- Context: Why shared weights beat dense nets on images: locality + translation structure.
- Resources:
  - **PRIMARY** D2L.ai — From Fully-Connected to Convolutions (~20 min)
    https://d2l.ai/chapter_convolutional-neural-networks/why-conv.html
- Currently has **no questions at all**.

## `dl-convolution-op` — Convolution operation

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Slide kernels over inputs; compute output sizes by hand for small cases
- Context: Slide kernels over inputs; compute output sizes by hand for small cases.
- Resources:
  - **PRIMARY** D2L.ai — Convolutional Layer (~25 min)
    https://d2l.ai/chapter_convolutional-neural-networks/conv-layer.html
    exact part: Convolution operation
  - **SUPPLEMENT** Vizuara — Vizuara — Filters in 1D and Convolution Operation (~17 min)
    https://www.youtube.com/watch?v=P6d8NbTlEpU
- Currently has **no questions at all**.

## `dl-padding-stride` — Padding & stride

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Control spatial shrinkage; SAME vs VALID reasoning
- Context: Control spatial shrinkage; SAME vs VALID reasoning.
- Resources:
  - **PRIMARY** D2L.ai — Convolutional Layer (~15 min)
    https://d2l.ai/chapter_convolutional-neural-networks/conv-layer.html
    exact part: Padding and Stride
- Currently has **no questions at all**.

## `dl-pooling` — Pooling

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Downsample with max/avg; state what invariance it buys and costs
- Context: Downsample with max/avg; state what invariance it buys and costs.
- Resources:
  - **PRIMARY** D2L.ai — Pooling (~15 min)
    https://d2l.ai/chapter_convolutional-neural-networks/pooling.html
  - **SUPPLEMENT** Vizuara — Vizuara — What is Max Pooling in CNNs? (~10 min)
    https://www.youtube.com/watch?v=nc46EtxUvD4
- Currently has **no questions at all**.

## `dl-feature-maps` — Feature maps & channels

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Stack conv layers into channel volumes; trace tensor shape end to end
- Context: Stack conv layers into channel volumes; trace tensor shape end to end.
- Resources:
  - **PRIMARY** D2L.ai — LeNet: feature maps and channels (~20 min)
    https://d2l.ai/chapter_convolutional-neural-networks/lenet.html
    exact part: feature maps through channels in LeNet
- Currently has **no questions at all**.

## `dl-rnn-awareness` — RNN awareness

- Depth target: AWARENESS  ·  Track: CORE
- Objective: Recurrence shares weights across time; name vanishing-memory failure mode
- Context: Recurrence shares weights across time; name vanishing-memory failure mode.
- Resources:
  - **PRIMARY** D2L.ai — Sequence Models (~15 min)
    https://d2l.ai/chapter_recurrent-neural-networks/sequence.html
- Currently has **no questions at all**.

## `dl-lstm-gru` — LSTM & GRU

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Gates as learned memory controllers; GRU as streamlined LSTM
- Context: Gates as learned memory controllers; GRU as streamlined LSTM.
- Resources:
  - **PRIMARY** D2L.ai — Long Short-Term Memory (LSTM) (~25 min)
    https://d2l.ai/chapter_recurrent-modern/lstm.html
- Currently has **no questions at all**.

## `dl-attention-intuition` — Attention intuition

- Depth target: INTUITION  ·  Track: CORE
- Objective: Query-key-value lookup replaces fixed-size bottlenecks; alignment becomes dynamic
- Context: Query-key-value lookup replaces fixed-size bottlenecks; alignment becomes dynamic.
- Resources:
  - **PRIMARY** Vizuara — Transformers Explained: Attention Simplified! (~44 min)
    https://www.youtube.com/watch?v=CLQJ9M5LZao
  - **REFERENCE** D2L.ai — Attention Cues (~25 min)
    https://d2l.ai/chapter_attention-mechanisms-and-transformers/queries-keys-values.html
- Currently has **no questions at all**.

## `dl-transformers-foundations` — Transformer foundations

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Self-attention blocks + residuals + norms stack into modern architectures
- Context: Self-attention blocks + residuals + norms stack into modern architectures.
- Resources:
  - **PRIMARY** Vizuara — Transformers Explained: Build a Transformer End-to-End! (~73 min)
    https://www.youtube.com/watch?v=l0mAJ54xey0
  - **REFERENCE** D2L.ai — Transformer architecture (~30 min)
    https://d2l.ai/chapter_attention-mechanisms-and-transformers/transformer.html
    exact part: begins
- Currently has **no questions at all**.

## `dl-pytorch-tensors` — PyTorch tensors

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Create/reshape/index tensors; dtypes and GPU devices
- Context: Create/reshape/index tensors; dtypes and GPU devices.
- Resources:
  - **PRIMARY** PyTorch — Tensors (~30 min)
    https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

## `dl-pytorch-data` — Datasets, DataLoader & transforms

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Package samples; batch/shuffle loaders; compose transforms
- Context: Package samples; batch/shuffle loaders; compose transforms.
- Resources:
  - **PRIMARY** PyTorch — Datasets & DataLoaders (~30 min)
    https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

## `dl-pytorch-build-model` — Building models with nn.Module

- Depth target: MECHANICS  ·  Track: CORE
- Objective: Layers + forward(); inspect parameters by shape
- Context: Layers + forward(); inspect parameters by shape.
- Resources:
  - **PRIMARY** PyTorch — Build the Model (~30 min)
    https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

## `dl-pytorch-autograd` — Autograd mechanics

- Depth target: MECHANICS  ·  Track: CORE
- Objective: requires_grad, backward(), .grad bookkeeping; graph freeing
- Context: requires_grad, backward(), .grad bookkeeping; graph freeing.
- Resources:
  - **PRIMARY** PyTorch — Automatic Differentiation (~30 min)
    https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

## `dl-pytorch-training-loop` — Full optimization loop

- Depth target: MECHANICS  ·  Track: CORE
- Objective: loss.backward + optimizer.step pattern; train/validate split loop
- Context: loss.backward + optimizer.step pattern; train/validate split loop.
- Resources:
  - **PRIMARY** PyTorch — Optimize the Model (~35 min)
    https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

## `dl-pytorch-save-load` — Save & load runs

- Depth target: MECHANICS  ·  Track: CORE
- Objective: state_dict persistence; resume checkpoints reliably
- Context: state_dict persistence; resume checkpoints reliably.
- Resources:
  - **PRIMARY** PyTorch — Save & Load the Model (~20 min)
    https://docs.pytorch.org/tutorials/beginner/basics/saveloadrun_tutorial.html
    exact part: above; content inspection pending
- Currently has **no questions at all**.

