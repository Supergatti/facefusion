import os
import uuid
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"D:\AI_Swapper"  # 输出文件夹
# output_folder = r"E:\AIProject\evilOrgs"
input_folder = r"E:\AIProject\uperfect\batch1"  # 待换脸的图片文件夹
source_faces_folder = r"E:\AIProject\GoodFaces"  # 提供脸部特征的参考图片文件夹
# source_faces_folder = r"E:\AIProject\evilFace\testones"


# for ubuntu
# output_folder = "/mnt/d/AI_Swapper"  # 输出文件夹
# input_folder = "/mnt/e/AIProject/uperfect/batch2"  # 待换脸的图片文件夹
# source_faces_folder = "/mnt/e/AIProject/GoodFaces"  # 提供脸部特征的参考图片文件夹


# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 获取所有脸部图片文件
source_faces = [os.path.join(source_faces_folder, f) for f in os.listdir(source_faces_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 初始化全局任务队列
global_task_queue = Queue()

def add_task_to_global_queue(task_id, selected_face_image, target_image_path, output_path):
    """将任务添加到全局任务队列"""
    global_task_queue.put((task_id, selected_face_image, target_image_path, output_path))

def process_task(task_id, selected_face_image, target_image_path, output_path):
    """处理单个任务"""
    os.system(f'python facefusion.py job-add-step {task_id} --source-paths "{selected_face_image}" --output-path "{output_path}" --target-path "{target_image_path}" --face-selector-mode "reference" --face-swapper-model "inswapper_128" --face-swapper-pixel-boost "1024x1024" --face-enhancer-model "gfpgan_1.4"')

def execute_task_batch(task_batch):
    """执行一批任务"""
    task_id = str(uuid.uuid4())[:8]  # 为任务批次生成一个随机任务 ID
    os.system(f'python facefusion.py job-delete {task_id}')
    os.system(f'python facefusion.py job-create {task_id}')
    
    for task in task_batch:
        _, selected_face_image, target_image_path, output_path = task
        process_task(task_id, selected_face_image, target_image_path, output_path)
    
    os.system(f'python facefusion.py job-submit {task_id}')
    os.system(f'python facefusion.py job-run {task_id}')

def execute_global_tasks():
    """分批执行全局任务队列中的所有任务"""
    task_batch = []
    while not global_task_queue.empty():
        task = global_task_queue.get()
        task_batch.append(task)
        
        # 每 30 个任务为一批
        if len(task_batch) == 30:
            execute_task_batch(task_batch)
            task_batch = []
    
    # 处理剩余的任务
    if task_batch:
        execute_task_batch(task_batch)

def process_all_faces(input_folder, output_folder):
    """对每个人脸图像处理所有写真"""
    for selected_face_image in source_faces:
        selected_face_name = os.path.splitext(os.path.basename(selected_face_image))[0]  # 获取脸部图片的文件名（不含扩展名）

        # 更新输出文件夹路径，包含所选脸部图片的名称
        updated_output_folder = os.path.join(output_folder, selected_face_name)

        for root, dirs, files in os.walk(input_folder):
            # 计算当前文件夹对应的输出文件夹路径
            relative_path = os.path.relpath(root, input_folder)
            current_output_folder = os.path.join(updated_output_folder, relative_path)
            os.makedirs(current_output_folder, exist_ok=True)

            # 遍历当前文件夹中的所有图片
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    target_image_path = os.path.join(root, file)
                    target_extension = os.path.splitext(file)[1]

                    # 确保输出文件扩展名与目标文件一致，并移除任务序号，仅保留人名和原文件名
                    output_filename = f"{selected_face_name}_{os.path.splitext(file)[0]}{target_extension}"
                    output_path = os.path.join(current_output_folder, output_filename)

                    # 将任务添加到全局任务队列
                    add_task_to_global_queue(uuid.uuid4(), selected_face_image, target_image_path, output_path)

# 开始处理输入文件夹
process_all_faces(input_folder, output_folder)

# 统一执行所有任务
execute_global_tasks()



