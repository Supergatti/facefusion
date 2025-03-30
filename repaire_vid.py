import os
import subprocess

def repair_videos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    for idx, video_file in enumerate(video_files, start=1):
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
        except subprocess.CalledProcessError as e:
            print(f"Failed to process {video_file}: {e}")

if __name__ == "__main__":
    input_folder = "E:\AIProject\evilPics"  # Replace with your input folder path
    output_folder = "E:\AIProject\evilVids"  # Replace with your output folder path
    repair_videos(input_folder, output_folder)