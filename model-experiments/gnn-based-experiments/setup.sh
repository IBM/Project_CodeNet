#!/usr/bin/env bash

if source activate pyg; then
	:
else
	echo 'Creating environment pyg'
	conda create -n pyg python=3.8 -y
	source activate pyg
fi

# TODO 1: Install PyTorch
#  use command for your system: https://pytorch.org/
#  (scroll down to "INSTALL PYTORCH" and choose the parameters for your system)
# e.g.
# conda install pytorch==1.7.1 torchvision==0.8.2 torchaudio==0.7.2 cpuonly -c pytorch


# TODO 2: Install PyTorch Geometric (after having installed pytorch)
#  see PyTorch Geometric's installation instructions: https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html
#CUDA=
#TORCH=
#pip install torch-scatter -f https://pytorch-geometric.com/whl/torch-${TORCH}+${CUDA}.html
#pip install torch-sparse -f https://pytorch-geometric.com/whl/torch-${TORCH}+${CUDA}.html
#pip install torch-cluster -f https://pytorch-geometric.com/whl/torch-${TORCH}+${CUDA}.html
#pip install torch-spline-conv -f https://pytorch-geometric.com/whl/torch-${TORCH}+${CUDA}.html
#pip install torch-geometric
