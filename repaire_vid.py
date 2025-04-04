import os
import subprocess

def repair_videos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取 output_folder 中现有文件的最大序号
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("vid_") and f.endswith("_repaired.mp4")]
    max_index = 0
    for f in existing_files:
        try:
            index = int(f.split("_")[1])
            max_index = max(max_index, index)
        except ValueError:
            continue

    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv'))]
    for idx, video_file in enumerate(video_files, start=max_index + 1):
        input_path = os.path.join(input_folder, video_file)
        output_path = os.path.join(output_folder, f"vid_{idx}_repaired.mp4")
        
        # FFmpeg command to repair and convert video with CUDA acceleration
        command = [
            "ffmpeg",
            "-hwaccel", "cuda",
            "-i", input_path,
            "-c:v", "h264_nvenc",
            "-preset", "fast",
            "-cq", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Repaired and converted: {video_file} -> {output_path}")
            # 删除输入文件
            # os.remove(input_path)
        except subprocess.CalledProcessError as e:
            print(f"Failed to process {video_file}: {e}")

if __name__ == "__main__":
    input_folder = r"E:\AIProject\uperfect\vid0"  # Replace with your input folder path
    output_folder = r"E:\AIProject\uperfect\vid2"  # Replace with your output folder path
    repair_videos(input_folder, output_folder)