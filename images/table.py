import os
import base64

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

folder_path = "images"  # 请替换为你的图片文件夹路径
valid_extensions = (".jpg", ".jpeg", ".png")
images = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

if len(images) < 2:
    print("文件夹中不足两张图片！")
else:
    for image_name in images[:2]:
        image_path = os.path.join(folder_path, image_name)
        encoded_str = encode_image_to_base64(image_path)
        print("图片：", image_name)
        with open('images/{}_1.txt'.format(image_name), 'w') as f:
            f.write(encoded_str)
