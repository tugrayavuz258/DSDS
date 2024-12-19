import os
import requests
import json
from config import Config
from requestModel import TubeData
from datetime import datetime

class APIClient:
    
    def __init__(self):
        self.token_url = "https://identityapi.aygaz.com.tr/api/Auth/Login" # sunucudan yetki tokeni almak için url
        self.token = None #başta tokenimiz yok none
        self.headers = {"Content-Type": "application/json"} #json formatı için başlık bilgisi
        self.log_dir = "log_txt"  # Log dosyalarının saklanacağı dizin
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)  # Dizin yoksa oluştur
        
    def get_token(self):
        data = {
            "grantType": "password", #giriş türü şifre
            "appCode": "APP001", #api ile hangi uygulamanın bağlandığını belirtir
            "userName": "VAApiUser",
            "password": "V.alf414623"
        }
        response = requests.post(self.token_url, json=data) #istek gönderilir ve yanıt alınır
        if response.status_code == 200:
            self.token = response.json().get("Payload")["AccessToken"] #yanıttan gelen payload alanından token alınır
            self.headers["Authorization"] = f"Bearer {self.token}" #bearer token kimlik doğrulama için kullanılan bir anahtar (http basligidir) token türü tasiyici yani bearer
            return self.token
        else:
            return None

    def log_to_file(self, message):
        current_date = datetime.now().strftime("%Y-%m-%d")  # Şu anki saat formatını alın
        log_file = os.path.join(self.log_dir, f"{current_date}.txt")  # Dosya içinde currentdate.txt oluştur ve kaydet
        with open(log_file, "a", encoding="utf-8") as f:  # UTF-8 kodlamasıyla aç
            f.write(f"{datetime.now()}: {message}\n")  # İlgili mesajı ilgili dökümana yaz

    def send_update(self, tup_bilgileri):
        config = Config()
        json_data = []
        for record in tup_bilgileri:
            brand_ = record["brand"]
            plant_ = record["plant"]
            countingPoint_ = record["countingPoint"]
            item_list = [
                {
                    "productGroup": subrecord["ProductGroup"],
                    "tbkli": subrecord["tbkli"],
                    "tbksiz": subrecord["tbksiz"]
                }
                for subrecord in record["itemList"]
            ]
            json_data.append({
                "date": datetime.now().isoformat(),
                "brand": brand_,
                "itemList": item_list,
                "plant": plant_,
                "countingPoint": countingPoint_
            })

        post_url = "https://dijitalfabrikaapi.aygaz.com.tr/api/TubeCounting/CreateCampTubeCounting"
        json_data_str = json.dumps(json_data, indent=4, ensure_ascii=False)  # UTF-8 kodlaması

        if not self.token:
            self.get_token()
            print("Token alındı:", self.token)

        response = requests.post(post_url, headers=self.headers, data=json_data_str)
        print(json_data_str)
        if response.status_code == 200:
            self.log_to_file(f"Güncelleme başarılı! Veriler: {json_data_str}")
        else:
            self.log_to_file(f"Güncelleme hatası: {response.status_code} - Yanıt: {response.text}")

if __name__ == "__main__": #dogrudan ilgili .py calistirilirsa
    api_client = APIClient()
    
    tup_bilgileri = [
        {
            "date": datetime.now().isoformat(),
            "brand": "Aygaz",
            "itemList": [
                {"ProductGroup": "KampDar", "tbkli": 10, "tbksiz": 5},
                {"ProductGroup": "KampGenis", "tbkli": 20, "tbksiz": 15}
            ],
            "plant": "Ambarlı",
            "countingPoint": "Kamp"
        },
        {
            "date": datetime.now().isoformat(),
            "brand": "Mogaz",
            "itemList": [
                {"ProductGroup": "KampDar", "tbkli": 4, "tbksiz": 2},
                {"ProductGroup": "KampGenis", "tbkli": 0, "tbksiz": 6}
            ],
            "plant": "Ambarlı",
            "countingPoint": "Kamp"
        },
        {
            "date": datetime.now().isoformat(),
            "brand": "Sarı kapak",
            "itemList": [
                {"ProductGroup": "KampDar", "tbkli": 5, "tbksiz": 3},
                {"ProductGroup": "KampGenis", "tbkli": 7, "tbksiz": 4}
            ],
            "plant": "Ambarlı",
            "countingPoint": "Kamp"
        },
        {
            "date": datetime.now().isoformat(),
            "brand": "Kapaksız",
            "itemList": [
                {"ProductGroup": "KampDar", "tbkli": 6, "tbksiz": 0},
                {"ProductGroup": "KampGenis", "tbkli": 9, "tbksiz": 2}
            ],
            "plant": "Ambarlı",
            "countingPoint": "Kamp"
        }]
    

    api_client.send_update(tup_bilgileri)
