import os
import subprocess

def repair_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    for idx, image_file in enumerate(image_files, start=1):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, f"img_{idx}_repaired.png")
        
        # FFmpeg command to repair and convert images
        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", "format=rgb24",
            output_path
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Repaired and converted: {image_file} -> {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to process {image_file}: {e}")

if __name__ == "__main__":
    input_folder = "E:\AIProject\evilPics"  # Replace with your input folder path
    output_folder = "E:\AIProject\evilImgs"  # Replace with your output folder path
    repair_images(input_folder, output_folder)
