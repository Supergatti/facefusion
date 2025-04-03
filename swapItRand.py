import os
import random
import uuid
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:/AIProject/evilOrgs"  # 输出文件夹
input_folder = r"E:/AIProject/evilU15"  # 待换脸的图片文件夹
source_faces_folder = r"E:/AIProject/evilFace"  # 提供脸部特征的参考图片文件夹

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 获取所有脸部图片文件
source_faces = [os.path.join(source_faces_folder, f) for f in os.listdir(source_faces_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 初始化任务队列
task_queue = Queue(maxsize=2)  # 每个任务队列最多包含 30 个任务

def execute_tasks(queue, task_id, selected_face_image, selected_face_name):
    """统一执行队列中的任务"""
    os.system(f'python facefusion.py job-delete {task_id}')
    os.system(f'python facefusion.py job-create {task_id}')
    while not queue.empty():
        target, output = queue.get()
        os.system(f'python facefusion.py job-add-step {task_id} --source-paths "{selected_face_image}" --output-path "{output}" --target-path "{target}" --face-selector-mode "reference" --face-swapper-model "inswapper_128_fp16" --face-swapper-pixel-boost "1024x1024"')
    os.system(f'python facefusion.py job-submit {task_id}')
    os.system(f'python facefusion.py job-run {task_id}')

# 遍历文件夹中的所有目标图片（乱序选择）
target_images = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
random.shuffle(target_images)  # 对目标图片列表进行乱序

for target_image_filename in target_images:
    target_image_path = os.path.join(input_folder, target_image_filename)
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