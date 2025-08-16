# 導入所有需要的模組
import urequests
import uhashlib
import utime
import gc
import os # <--- 新增導入 os 模組

class Senko:
    raw = "https://raw.githubusercontent.com"
    github = "https://github.com"

    def __init__(self, user, repo, url=None, branch="master", working_dir="app", files=["boot.py", "main.py"], headers={}):
        self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        self.headers = headers
        self.files = files
        self.chunk_size = 512  # 設定每個數據塊的大小 (bytes)

    def _get_local_hash(self, file):
        """以流式讀取本地檔案並計算 SHA1 雜湊值"""
        try:
            with open(file, 'rb') as f:
                sha = uhashlib.sha1()
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    sha.update(chunk)
                return sha.digest()
        except OSError:
            # 檔案不存在，回傳空字串的雜湊值
            return uhashlib.sha1(b"").digest()

    def _stream_to_temp_and_hash(self, url):
        """以流式下載檔案至暫存檔，並同時計算雜湊值"""
        temp_file = "senko.tmp"
        sha = uhashlib.sha1()
        
        try:
            # 確保舊的暫存檔被刪除
            if "senko.tmp" in os.listdir():
                os.remove(temp_file)

            resp = urequests.get(url, headers=self.headers)
            if resp.status_code != 200:
                print("Got HTTP {} for {}".format(resp.status_code, url))
                resp.close()
                return None, None
            
            with open(temp_file, 'wb') as f:
                while True:
                    chunk = resp.raw.read(self.chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    sha.update(chunk)
            
            resp.close()
            return temp_file, sha.digest()

        except Exception as e:
            print("Failed to stream download {}: {}".format(url, e))
            # 清理可能不完整的暫存檔
            if "senko.tmp" in os.listdir():
                os.remove(temp_file)
            return None, None

    def _check_all(self):
        """以流式下載檢查所有檔案是否有變更"""
        changes = []
        for file in self.files:
            remote_hash = None
            
            # 帶有重試機制地獲取遠端雜湊值
            for attempt in range(3):
                temp_file, r_hash = self._stream_to_temp_and_hash(self.url + "/" + file)
                if temp_file:
                    os.remove(temp_file) # 檢查完畢，刪除暫存檔
                    remote_hash = r_hash
                    break
                else:
                    print("Failed to check {}, attempt {}/3. Retrying...".format(file, attempt + 1))
                    utime.sleep(1)

            if not remote_hash:
                print("Could not get remote hash for {}. Skipping.".format(file))
                continue
            
            local_hash = self._get_local_hash(file)

            if remote_hash != local_hash:
                changes.append(file)
                print("File '{}' has changed.".format(file))

            gc.collect()
        return changes

    def fetch(self):
        """檢查是否有新版本可用"""
        return bool(self._check_all())

    def update(self):
        """以流式下載和原子性取代來更新檔案"""
        changes = self._check_all()
        files_updated = []

        for file in changes:
            updated = False
            # 帶有重試機制地下載並取代檔案
            for attempt in range(3):
                temp_file, remote_hash = self._stream_to_temp_and_hash(self.url + "/" + file)
                
                if temp_file and remote_hash:
                    # 再次驗證本地雜湊值，以防萬一
                    local_hash = self._get_local_hash(file)
                    if remote_hash != local_hash:
                        os.rename(temp_file, file) # 原子性操作，安全地取代舊檔案
                        print("Successfully updated {}.".format(file))
                    else:
                        # 在下載過程中，本地檔案可能已被其他方式更新
                        os.remove(temp_file)
                        print("File '{}' already up to date.".format(file))
                    updated = True
                    break # 成功，跳出重試
                else:
                    print("Failed to download {}, attempt {}/3. Retrying...".format(file, attempt + 1))
                    utime.sleep(1)
            
            if updated:
                files_updated.append(file)
            else:
                 print("Could not update {} after 3 attempts. Skipping.".format(file))

            gc.collect()

        if files_updated:
            print("Update complete. Updated files: {}".format(files_updated))
            return True
        return False
