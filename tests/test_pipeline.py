import os
import sys
import json
import argparse
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import init_engines, process_job
from app.services.storage import LocalStorageService

def run_local_test(image_filename):
    print("-> Đang khởi tạo các Engine OCR...")
    init_engines()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    assets_dir = os.path.join(base_dir, 'tests', 'assets')
    image_path = os.path.join(assets_dir, image_filename)
    
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy ảnh tại {image_path}")
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(base_dir, "local_output", timestamp)
    local_storage = LocalStorageService(output_dir=output_dir)
    
    test_job = {
        "job_id": "test_001",
        "page_id": "page_01",
        "image_path": image_path,
        "source_lang": "ja",
        "target_langs": ["en"],
        "comic_type": "manga"
    }
    
    print("-> Bắt đầu xử lý Job...")
    print(f"Job config: \n{json.dumps(test_job, indent=2, ensure_ascii=False)}")
    try:
        result = process_job(test_job, storage=local_storage)
        print("\n✅ HOÀN THÀNH! Kết quả JSON trả về:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n📂 Hãy kiểm tra thư mục 'local_output' để xem ảnh và file metadata.")
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình chạy Pipeline: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Manga Pipeline")
    parser.add_argument("--image", type=str, default="0008.jpg", help="Tên file ảnh trong thư mục tests/assets/")
    args = parser.parse_args()

    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local.test')
    load_dotenv(dotenv_path=env_path)
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ CẢNH BÁO: Chưa set GEMINI_API_KEY. Vui lòng thiết lập biến môi trường này trước khi chạy.")
    else:
        run_local_test(args.image)

    