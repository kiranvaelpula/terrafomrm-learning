# Distributed Training

## Overview

Distributed training splits ML model training across multiple GPUs or machines, dramatically reducing training time for large models and datasets.

## Why Distributed Training?

- **Large Models:** Models too big for single GPU
- **Large Datasets:** Faster training on big data
- **Experimentation:** More experiments in less time
- **Cost Efficiency:** Reduce training time and costs

## Training Strategies

### 1. Data Parallelism
Split data across GPUs, same model on each

```
GPU 1: Batch 1-32   → Gradients → Average → Update
GPU 2: Batch 33-64  → Gradients → Average → Update
GPU 3: Batch 65-96  → Gradients → Average → Update
GPU 4: Batch 97-128 → Gradients → Average → Update
```

### 2. Model Parallelism
Split model layers across GPUs

```
GPU 1: Layers 1-25
GPU 2: Layers 26-50
GPU 3: Layers 51-75
GPU 4: Layers 76-100
```

## PyTorch Distributed

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup(rank, world_size):
    """Initialize distributed training"""
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def train(rank, world_size):
    setup(rank, world_size)
    
    # Create model and move to GPU
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    
    # Training loop
    for epoch in range(epochs):
        for batch in dataloader:
            outputs = ddp_model(batch)
            loss = criterion(outputs, targets)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

# Launch distributed training
if __name__ == "__main__":
    world_size = 4  # 4 GPUs
    torch.multiprocessing.spawn(
        train,
        args=(world_size,),
        nprocs=world_size
    )
```

## TensorFlow Distributed

```python
import tensorflow as tf

strategy = tf.distribute.MirroredStrategy()

with strategy.scope():
    model = create_model()
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Train on multiple GPUs
model.fit(train_dataset, epochs=10)
```

## Horovod (Framework-Agnostic)

```python
import horovod.tensorflow as hvd

# Initialize Horovod
hvd.init()

# Pin GPU
gpus = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_visible_devices(gpus[hvd.local_rank()], 'GPU')

# Build model
model = create_model()

# Horovod optimizer
optimizer = tf.optimizers.Adam(0.001 * hvd.size())
optimizer = hvd.DistributedOptimizer(optimizer)

# Training
model.compile(optimizer=optimizer, loss='mse')
model.fit(dataset, epochs=10, callbacks=[hvd.callbacks.BroadcastGlobalVariablesCallback(0)])
```

Launch:
```bash
horovodrun -np 4 python train.py
```

## Best Practices

✅ Use data parallelism for most cases  
✅ Adjust batch size for multiple GPUs  
✅ Scale learning rate with workers  
✅ Use gradient accumulation for large batches  
✅ Monitor GPU utilization  
✅ Handle failures gracefully

## When to Use

| Dataset Size | Model Size | Strategy |
|-------------|------------|----------|
| Large | Small | Data Parallelism |
| Small | Large | Model Parallelism |
| Large | Large | Hybrid (both) |
| Small | Small | Single GPU |

## Key Takeaways

✅ Distributed training reduces training time  
✅ Data parallelism is most common  
✅ Model parallelism for huge models  
✅ Frameworks provide easy APIs  
✅ Essential for large-scale ML

---

**Next:** [MLOps Best Practices](19-mlops-best-practices.md)
