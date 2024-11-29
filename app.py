from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)

# 从环境变量中读取配置
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
API_KEY = os.environ.get('API_KEY')  # 用于 API 身份验证

# 创建 S3 客户端
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 验证 API 密钥
    provided_api_key = request.headers.get('X-API-KEY')
    if provided_api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # 检查是否包含文件
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 上传到 MinIO
    try:
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        file_url = f"{MINIO_ENDPOINT}/{BUCKET_NAME}/{file.filename}"
        return jsonify({'url': file_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port)
