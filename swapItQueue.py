import os
from queue import Queue

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:/AIProject/evilOrgs"  # 输出文件夹
input_folder = r"E:\AIProject\uai\ogi erena\tp_ogi04"  # 待换脸的图片文件夹
source_face_image = r"E:\AIProject\evilFace\TangY1fan.png"  # 提供脸部特征的参考图片

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)
 
# 初始化任务队列
task_queue = Queue(maxsize=20)

def execute_tasks(queue):
    """统一执行队列中的任务"""
    os.system(f'python facefusion.py job-delete 1145')
    os.system(f'python facefusion.py job-create 1145')
    while not queue.empty():
        source, target, output = queue.get()
        os.system(f'python facefusion.py job-add-step 1145 --source-paths "{source}" --output-path "{output}" --target-path "{target}" --face-selector-mode "reference" --face-swapper-model "inswapper_128" --face-swapper-pixel-boost "512x512"')
    os.system(f'python facefusion.py job-submit 1145')
    os.system(f'python facefusion.py job-run 1145')

# 遍历文件夹中的所有图片
for target_image_filename in os.listdir(input_folder):
    target_image_path = os.path.join(input_folder, target_image_filename)
    if target_image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # 获取目标文件的扩展名
        target_extension = os.path.splitext(target_image_path)[1]
        # 确保输出文件扩展名与目标文件一致
        output_filename = os.path.splitext(target_image_filename)[0] + target_extension
        output_path = os.path.join(output_folder, output_filename)

        # 将任务添加到队列
        task_queue.put((source_face_image, target_image_path, output_path))

        # 如果队列已满，统一执行任务
        if task_queue.full():
            execute_tasks(task_queue)

# 处理剩余任务
if not task_queue.empty():
    execute_tasks(task_queue)
