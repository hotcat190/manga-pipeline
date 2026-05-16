import json
import os

json_string = r"""{
    "text": "{\n  \"translations\": [\n    {\n      \"chunks\": [\n        {\n          \"chunk_id\": \"1\",\n          \"meaning_in_context\": \"Tiếng kêu gây chú ý\"\n        }\n      ]\n    }\n  ]\n}"
}"""

data = json.loads(json_string)
text_content = data["text"]

os.makedirs("local_output", exist_ok=True)

output_path_json = "local_output/output_json.txt"
with open(output_path_json, "w", encoding="utf-8") as f:
    f.write(text_content)

raw_string = "Dòng thứ nhất\\nDòng thứ hai\\nDòng thứ ba"
processed_string = raw_string.replace("\\n", "\n")

output_path_raw = "local_output/output_raw.txt"
with open(output_path_raw, "w", encoding="utf-8") as f:
    f.write(processed_string)