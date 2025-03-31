import os
import random
import uuid
import time  # 用于测量运行时间
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:/AIProject/evilOrgs"  # 输出文件夹
input_folder = r"E:/AIProject/evilU15"  # 待换脸的图片文件夹
source_faces_folder = r"E:/AIProject/evilFace"  # 提供脸部特征的参考图片文件夹

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 获取所有脸部图片文件
source_faces = [os.path.join(source_faces_folder, f) for f in os.listdir(source_faces_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

def execute_tasks(queue, task_id, selected_face_image, selected_face_name):
    """统一执行队列中的任务"""
    os.system(f'python facefusion.py job-delete {task_id}')
    os.system(f'python facefusion.py job-create {task_id}')
    while not queue.empty():
        target, output = queue.get()
        os.system(f'python facefusion.py job-add-step {task_id} --source-paths "{selected_face_image}" --output-path "{output}" --target-path "{target}" --face-selector-mode "reference" --face-swapper-model "inswapper_128_fp16" --face-swapper-pixel-boost "256x256"')
    os.system(f'python facefusion.py job-submit {task_id}')
    os.system(f'python facefusion.py job-run {task_id}')

# 获取输入文件夹中的前 120 张图片
input_images = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:120]

# 定义不同的队列长度进行测试
queue_lengths = [2, 4, 6, 8, 10]

for queue_length in queue_lengths:
    print(f"Testing with queue length: {queue_length}")
    task_queue = Queue(maxsize=queue_length)  # 设置当前队列长度
    start_time = time.time()  # 记录开始时间

    for target_image_filename in input_images:
        target_image_path = os.path.join(input_folder, target_image_filename)
        if target_image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 随机选择一个脸部图片（仅在队列为空时选择）
            if task_queue.empty():
                selected_face_image = random.choice(source_faces)
                selected_face_name = os.path.splitext(os.path.basename(selected_face_image))[0]  # 获取脸部图片的文件名（不含扩展名）
                task_id = str(uuid.uuid4())[:8]  # 为当前任务队列生成一个随机任务 ID

            # 获取目标文件的扩展名
            target_extension = os.path.splitext(target_image_path)[1]

            # 确保输出文件扩展名与目标文件一致，并在文件名中将人名放在最前面
            output_filename = f"{selected_face_name}_{os.path.splitext(target_image_filename)[0]}{target_extension}"  # 将人名放在最前面
            output_path = os.path.join(output_folder, output_filename)

            # 将任务添加到队列
            task_queue.put((target_image_path, output_path))

            # 如果队列已满，统一执行任务
            if task_queue.full():
                execute_tasks(task_queue, task_id, selected_face_image, selected_face_name)

    # 处理剩余任务
    if not task_queue.empty():
        execute_tasks(task_queue, task_id, selected_face_image, selected_face_name)

    end_time = time.time()  # 记录结束时间
    print(f"Queue length {queue_length} completed in {end_time - start_time:.2f} seconds")