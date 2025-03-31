import os

# 定义输入文件夹、输出文件夹和参考图片路径
output_folder = r"E:/AIProject/evilOrgs"  # 输出文件夹

input_folder = r"E:\AIProject\evilU15"  # 待换脸的图片文件夹
source_face_image = r"E:\AIProject\evilFace\SunQing.png"  # 提供脸部特征的参考图片


# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 遍历文件夹中的所有图片
for target_image_filename in os.listdir(input_folder):
    target_image_path = os.path.join(input_folder, target_image_filename)
    if target_image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # 获取目标文件的扩展名
        target_extension = os.path.splitext(target_image_path)[1]
        # 确保输出文件扩展名与目标文件一致
        output_filename = os.path.splitext(target_image_filename)[0] + target_extension
        output_path = os.path.join(output_folder, output_filename)

        # 创建任务并添加步骤
        os.system(f'python facefusion.py job-delete 1145')
        os.system(f'python facefusion.py job-create 1145')
        # 使用更具描述性的变量名
        os.system(f'python facefusion.py job-add-step 1145 --source-paths "{source_face_image}" --output-path "{output_path}" --target-path "{target_image_path}" --face-selector-mode "reference" --face-swapper-model "inswapper_128_fp16" --face-swapper-pixel-boost "512x512"')
        os.system(f'python facefusion.py job-submit 1145')
        os.system(f'python facefusion.py job-run 1145')
