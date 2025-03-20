from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

def cut_image(img, threshold=200, null_size=0.5):
    """
    使用 grabCut 裁剪图片中非背景区域，返回处理后的 BGRA 图像。
    参数：
      img：numpy 数组格式的原图（BGR）
      threshold, null_size：用于边界裁剪的阈值参数
    """
    height, width, _ = img.shape
    mask = np.zeros((height, width), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (10, 10, width - 20, height - 20)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img_fg = img * mask2[:, :, np.newaxis]
    alpha = np.where(mask2 == 1, 255, 0).astype('uint8')
    img_bgra = cv2.cvtColor(img_fg, cv2.COLOR_BGR2BGRA)
    img_bgra[:, :, 3] = alpha

    alpha_channel = img_bgra[:, :, 3]
    cols = np.where(np.sum(alpha_channel >= threshold, axis=0) > (alpha_channel.shape[0] * null_size))[0]
    rows = np.where(np.sum(alpha_channel >= threshold, axis=1) > (alpha_channel.shape[1] * null_size))[0]
    if cols.size:
        img_bgra = img_bgra[:, cols[0]:cols[-1] + 1]
    if rows.size:
        img_bgra = img_bgra[rows[0]:rows[-1] + 1]
    return img_bgra

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': '未上传图片'}), 400
    file = request.files['image']
    file_bytes = file.read()
    # 从文件数据读取为 numpy 数组
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': '图片数据无效'}), 400

    # 调用 cut_image 处理图片
    processed_img = cut_image(img)
    # 对处理结果以 PNG 格式编码
    retval, buffer = cv2.imencode('.png', processed_img)
    if not retval:
        return jsonify({'error': '图片编码失败'}), 500
    # 转换为 base64 字符串，附加 data URI 前缀
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    data_uri = 'data:image/png;base64,' + img_base64
    return jsonify({'image': data_uri})

# 同时提供静态文件服务，默认返回 index_demo.html
@app.route('/')
def index():
    # 获取当前文件所在的目录
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(base_dir, 'index_demo.html')

if __name__ == '__main__':
    import webbrowser
    import threading
    port = 5005
    threading.Timer(1, lambda: webbrowser.open("http://127.0.0.1:{}/".format(port))).start()
    app.run(debug=True, port=port)