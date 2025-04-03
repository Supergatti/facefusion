import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def process_image(input_path, output_path):
    # 使用 CUDA 加速的 FFmpeg 命令
    command = [
        "ffmpeg",
        "-hwaccel", "cuda",  # 启用 CUDA 硬件加速
        "-i", input_path,
        "-vf", "format=rgb24",  # 使用通用滤镜
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Repaired and converted: {input_path} -> {output_path}")
        # 删除成功处理的输入文件
        os.remove(input_path)
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {input_path}: {e}")

def repair_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取 output_folder 中现有文件的最大序号
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("img_") and f.endswith("_repaired.png")]
    max_index = 0
    for file in existing_files:
        try:
            index = int(file.split("_")[1])
            max_index = max(max_index, index)
        except ValueError:
            continue

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    tasks = []
    with ThreadPoolExecutor() as executor:
        for idx, image_file in enumerate(image_files, start=max_index + 1):
            input_path = os.path.join(input_folder, image_file)
            output_path = os.path.join(output_folder, f"img_{idx}_repaired.png")
            # output_path = os.path.join(output_folder, image_file)
            tasks.append(executor.submit(process_image, input_path, output_path))
        for task in tasks:
            task.result()  # 等待所有任务完成

if __name__ == "__main__":
    input_folder = "E:\AIProject\evilOrgs"  # Replace with your input folder path
    output_folder = "E:\AIProject\evilFace"  # Replace with your output folder path
    repair_images(input_folder, output_folder)
