import torch
print(torch.cuda.is_available())  # → True nếu đã bật CUDA
print(torch.cuda.get_device_name(0))  # → Tên GPU