import json
import sys
import os

def merge_json(original_path, trans_path, output_path="local_output/metadata.json"):
    try:
        # Đọc dữ liệu từ file gốc
        with open(original_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            
        # Đọc dữ liệu từ file dịch
        with open(trans_path, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)
            
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Lỗi: File JSON không hợp lệ - {e}")
        sys.exit(1)

    # Tạo một dictionary map các bubble theo id từ file dịch để tra cứu nhanh
    trans_bubbles_dict = {b['id']: b for b in trans_data.get('bubbles', [])}

    merged_bubbles = []
    
    # Lặp qua từng bubble ở file gốc
    for orig_bubble in original_data.get('bubbles', []):
        bubble_id = orig_bubble['id']
        trans_bubble = trans_bubbles_dict.get(bubble_id, {})
        
        # Khởi tạo cấu trúc cho bubble đã gộp
        merged_bubble = {
            "id": bubble_id,
            "box": orig_bubble.get("box", []),
            "original_text": orig_bubble.get("original_text", ""),
            "full_translation": trans_bubble.get("full_translation", ""),
            "chunks": []
        }
        
        # Gom các chunk_meanings từ file dịch thành một dictionary phẳng để dễ tra cứu
        # Ví dụ: [{"1_1": "Ahem"}, {"1_2": "everyone"}] -> {"1_1": "Ahem", "1_2": "everyone"}
        meanings_dict = {}
        for chunk_meaning in trans_bubble.get("chunk_meanings", []):
            meanings_dict.update(chunk_meaning)
            
        # Lặp qua từng chunk ở file gốc và thêm ý nghĩa (meaning) vào
        for orig_chunk in orig_bubble.get("chunks", []):
            chunk_id = orig_chunk['chunk_id']
            merged_chunk = {
                "chunk_id": chunk_id,
                "word": orig_chunk.get("word", ""),
                "romaji": orig_chunk.get("romaji", ""),
                "type": orig_chunk.get("type", ""),
                "meaning": meanings_dict.get(chunk_id, "") # Lấy meaning tương ứng với chunk_id
            }
            merged_bubble["chunks"].append(merged_chunk)
            
        merged_bubbles.append(merged_bubble)
        
    # Tạo cấu trúc JSON tổng
    merged_data = {
        "page_id": original_data.get("page_id", ""),
        "bubbles": merged_bubbles
    }

    # Ghi ra file mới
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Đã gộp thành công dữ liệu vào file: {output_path}")
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")

if __name__ == "__main__":
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 3 and len(sys.argv) > 4:
        print("Sử dụng sai cú pháp!")
        print("Cách dùng: python merge_json.py path/to/original.json path/to/trans_lang.json path/to/output")
        sys.exit(1)
        
    original_file = sys.argv[1]
    trans_file = sys.argv[2]
    output_path = sys.argv[3]
    
    merge_json(original_file, trans_file, output_path=output_path)