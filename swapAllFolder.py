import os
import random
import uuid
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:/AIProject/evilOrgs"  # 输出文件夹
input_folder = r"E:\AIProject\ua4"  # 待换脸的图片文件夹
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
        os.system(f'python facefusion.py job-add-step {task_id} --source-paths "{selected_face_image}" --output-path "{output}" --target-path "{target}" --face-selector-mode "reference" --face-swapper-model "inswapper_128" --face-swapper-pixel-boost "1024x1024" --face-enhancer-model "gfpgan_1.4"')
    os.system(f'python facefusion.py job-submit {task_id}')
    os.system(f'python facefusion.py job-run {task_id}')

def process_folder(input_folder, output_folder):
    """递归处理文件夹"""
    for root, dirs, files in os.walk(input_folder):
        # 随机选择一个脸部图片
        selected_face_image = random.choice(source_faces)
        selected_face_name = os.path.splitext(os.path.basename(selected_face_image))[0]  # 获取脸部图片的文件名（不含扩展名）

        # 更新输出文件夹路径，包含所选脸部图片的名称
        updated_output_folder = os.path.join(output_folder, selected_face_name)

        # 计算当前文件夹对应的输出文件夹路径
        relative_path = os.path.relpath(root, input_folder)
        current_output_folder = os.path.join(updated_output_folder, relative_path)
        os.makedirs(current_output_folder, exist_ok=True)

        # 初始化任务队列
        task_queue = Queue(maxsize=15)  # 每个任务队列最多包含 15 个任务
        task_id = str(uuid.uuid4())[:8]  # 为当前任务队列生成一个随机任务 ID

        # 遍历当前文件夹中的所有图片
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                target_image_path = os.path.join(root, file)
                target_extension = os.path.splitext(file)[1]

                # 确保输出文件扩展名与目标文件一致，并在文件名中将人名放在最前面
                output_filename = f"{selected_face_name}_{os.path.splitext(file)[0]}{target_extension}"
                output_path = os.path.join(current_output_folder, output_filename)

                # 将任务添加到队列
                task_queue.put((target_image_path, output_path))

                # 如果队列已满，统一执行任务
                if task_queue.full():
                    execute_tasks(task_queue, task_id, selected_face_image, selected_face_name)

        # 处理剩余任务
        if not task_queue.empty():
            execute_tasks(task_queue, task_id, selected_face_image, selected_face_name)

# 开始处理输入文件夹
process_folder(input_folder, output_folder)
