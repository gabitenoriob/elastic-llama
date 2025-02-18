import torch

def check_gpu_status():
    if torch.cuda.is_available():
        print(f"CUDA disponível: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA não está disponível.")
check_gpu_status()