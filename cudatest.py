import onnxruntime as ort

# 打印当前设备
print("当前设备:", ort.get_device())

# 打印所有可用的执行提供者
print("可用的执行提供者:", ort.get_available_providers())

# 检查TensorRT是否在可用提供者列表中
if 'TensorrtExecutionProvider' in ort.get_available_providers():
    print("TensorRT执行提供者可用")
    print("TensorRT版本信息可用 - 需要模型文件才能完全测试")
else:
    print("TensorRT执行提供者不可用")

# 打印ONNX Runtime版本信息
print("ONNX Runtime版本:", ort.__version__)

# 尝试创建CUDA会话测试
try:
    sess_options = ort.SessionOptions()
    cuda_providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
    print("CUDA执行提供者可用 - 需要模型文件才能完全测试")
except Exception as e:
    print(f"CUDA初始化出错: {e}")