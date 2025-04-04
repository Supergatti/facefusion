import os
import uuid
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:\AI_Swapper_Videos"  # 视频输出文件夹
input_folder = r"E:\AIProject\Videos\vid1"  # 待换脸的视频文件夹
source_faces_folder = r"E:\AIProject\GoodFaces"  # 提供脸部特征的参考图片文件夹

# for ubuntu
# output_folder = "/mnt/d/AI_Swapper_Videos"  # 视频输出文件夹
# input_folder = "/mnt/e/AIProject/Videos/batch1"  # 待换脸的视频文件夹
# source_faces_folder = "/mnt/e/AIProject/GoodFaces"  # 提供脸部特征的参考图片文件夹

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 获取所有脸部图片文件
source_faces = [os.path.join(source_faces_folder, f) for f in os.listdir(source_faces_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 初始化全局任务队列
global_task_queue = Queue()

def add_task_to_global_queue(task_id, selected_face_image, target_video_path, output_path):
    """将任务添加到全局任务队列"""
    global_task_queue.put((task_id, selected_face_image, target_video_path, output_path))

def process_task(task_id, selected_face_image, target_video_path, output_path):
    """处理单个任务"""
    try:
        # 视频处理命令，添加视频专用参数
        os.system(f'python facefusion.py job-add-step {task_id} --source-paths "{selected_face_image}" --output-path "{output_path}" --target-path "{target_video_path}" --face-selector-mode "reference" --face-swapper-model "inswapper_128_fp16" --face-detection-size "640x640" --temp-frame-format "jpg" --temp-frame-quality 100 --output-video-encoder "libx264" --output-video-quality 23')
        return True
    except Exception as e:
        print(f"Error adding task step: {e}")
        return False

def execute_task_batch(task_batch):
    """执行一批任务"""
    task_id = str(uuid.uuid4())[:8]  # 为任务批次生成一个随机任务 ID
    
    # 创建任务
    create_result = os.system(f'python facefusion.py job-create {task_id}')
    if create_result != 0:
        print(f"Failed to create job {task_id}")
        return
    
    # 添加所有步骤
    steps_added = 0
    for task in task_batch:
        _, selected_face_image, target_video_path, output_path = task
        if process_task(task_id, selected_face_image, target_video_path, output_path):
            steps_added += 1
    
    if steps_added == 0:
        print(f"No steps were added to job {task_id}, skipping")
        return
        
    # 提交并运行任务
    submit_result = os.system(f'python facefusion.py job-submit {task_id}')
    if submit_result != 0:
        print(f"Failed to submit job {task_id}")
        return
        
    run_result = os.system(f'python facefusion.py job-run {task_id}')
    if run_result != 0:
        print(f"Failed to run job {task_id}")

def execute_global_tasks():
    """分批执行全局任务队列中的所有任务"""
    task_batch = []
    while not global_task_queue.empty():
        task = global_task_queue.get()
        task_batch.append(task)
        
        # 视频处理资源密集，每批次只处理5个视频
        if len(task_batch) == 5:
            execute_task_batch(task_batch)
            task_batch = []
    
    # 处理剩余的任务
    if task_batch:
        execute_task_batch(task_batch)

def process_all_faces(input_folder, output_folder):
    """对每个人脸图像处理所有视频"""
    for selected_face_image in source_faces:
        selected_face_name = os.path.splitext(os.path.basename(selected_face_image))[0]  # 获取脸部图片的文件名（不含扩展名）

        # 更新输出文件夹路径，包含所选脸部图片的名称
        updated_output_folder = os.path.join(output_folder, selected_face_name)

        for root, dirs, files in os.walk(input_folder):
            # 计算当前文件夹对应的输出文件夹路径
            relative_path = os.path.relpath(root, input_folder)
            current_output_folder = os.path.join(updated_output_folder, relative_path)
            os.makedirs(current_output_folder, exist_ok=True)

            # 遍历当前文件夹中的所有视频
            for file in files:
                # 检查是否为视频文件
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv')):
                    target_video_path = os.path.join(root, file)
                    target_extension = os.path.splitext(file)[1]

                    # 确保输出文件扩展名与目标文件一致
                    output_filename = f"{selected_face_name}_{os.path.splitext(file)[0]}{target_extension}"
                    output_path = os.path.join(current_output_folder, output_filename)

                    # 将任务添加到全局任务队列
                    add_task_to_global_queue(uuid.uuid4(), selected_face_image, target_video_path, output_path)

# 开始处理输入文件夹
process_all_faces(input_folder, output_folder)

# 统一执行所有任务
execute_global_tasks()
