import os
import cv2

image_path = "D:\\garbage-data\\TrashType_Image_Dataset\\cardboard"
output_folder = "D:\\garbage-data\\TrashType_Image_Dataset\\cardboard_label"

def create_yolo_txt(image_path, output_folder, class_id=0):
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Bounding box: 80% of the image, centered
    bbox_width = width * 0.8
    bbox_height = height * 0.8
    x_center = width / 2
    y_center = height / 2

    # Normalize all values (between 0 and 1)
    x_center_norm = x_center / width
    y_center_norm = y_center / height
    width_norm = bbox_width / width
    height_norm = bbox_height / height

    yolo_format_line = f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"

    # Save .txt
    filename_wo_ext = os.path.splitext(os.path.basename(image_path))[0]
    txt_output_path = os.path.join(output_folder, filename_wo_ext + ".txt")
    with open(txt_output_path, "w") as f:
        f.write(yolo_format_line + "\n")

def batch_label_cardboard_yolo(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            full_path = os.path.join(input_folder, file)
            create_yolo_txt(full_path, output_folder)

    print(f"✅ YOLO labels saved in: {output_folder}")

# Example usage:
batch_label_cardboard_yolo(image_path, output_folder)