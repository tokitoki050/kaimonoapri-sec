import json
import os

# 新しいファイルの絶対パスを設定
JSON_FILE_PATH = "C:\\Users\\toki2\\OneDrive\\shopping_list.json"

def load_data():
    # JSONファイルが存在するか確認
    if os.path.exists(JSON_FILE_PATH):
        try:
            # JSONファイルを読み込む
            with open(JSON_FILE_PATH, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # JSONDecodeErrorが発生した場合は初期データを返す
            return {"shopping_list": [], "purchase_history": []}
    else:
        # JSONファイルが存在しない場合は初期データを返す
        return {"shopping_list": [], "purchase_history": []}

def save_data(data):
    # JSONファイルにデータを書き込む
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

# 初期化のために、空のJSONファイルを作成または上書きする
def initialize_json_file():
    if not os.path.exists(JSON_FILE_PATH):
        save_data({"shopping_list": [], "purchase_history": []})

# アプリケーションの起動時にJSONファイルを初期化する
initialize_json_file()
