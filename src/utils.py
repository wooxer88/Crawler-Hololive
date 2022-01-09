import json
import os
import time

from datetime import datetime
from pathlib import Path

def get_project_root() -> Path:
  return Path(__file__).parent.parent

def update_checksum(key, code) -> None:
  file_path = os.path.join(get_project_root(), 'data-checksum.json')
  timestamp = round(datetime.now().timestamp())
  
  with open(file_path) as f:
    data = json.load(f)

  data[key]['code'] = code
  data[key]['timestamp'] = timestamp

  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

