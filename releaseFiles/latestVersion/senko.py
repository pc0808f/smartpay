import urequests
import uhashlib
import gc
from time import sleep

class Senko:
    raw = "https://raw.githubusercontent.com"
    github = "https://github.com"

    def __init__(self, user, repo, url=None, branch="master", working_dir="app", files=["boot.py", "main.py"], headers={}):
        """Senko OTA agent class.
        Args:
            user (str): GitHub user.
            repo (str): GitHub repo to fetch.
            branch (str): GitHub repo branch. (master)
            working_dir (str): Directory inside GitHub repo where the micropython app is.
            url (str): URL to root directory.
            files (list): Files included in OTA update.
            headers (list, optional): Headers for urequests.
        """
        self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        self.headers = headers
        self.files = files

    def _check_hash(self, x, y):
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())
        x = x_hash.digest()
        y = y_hash.digest()
        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        gc.collect()
        payload = urequests.get(url, headers=self.headers)
        code = payload.status_code
        gc.collect()
        if code == 200:
            return payload.text
        else:
            return None

    def _check_all(self):
        changes = []
        for file in self.files:
            print('Checking file hash:', file)
            sleep(2)
            # Getting latest_file_version
            while(gc.mem_free()<60000):
                gc.collect()
                print(gc.mem_free())
                sleep(1)
            latest_version = self._get_file(self.url + "/" + file)
            if latest_version is None:
                continue
            
            # Getting local_file_version
            gc.collect()
            print(gc.mem_free())
            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)
            latest_version = ""
            local_version = ""

        return changes

    def update(self):
        """ Replace all changed files with newer one.
            Returns: True - if changes were made, False - if not.
        """
        changes = self._check_all()
        print("OTAing changed-file:", changes)
        gc.collect()
        for file in changes:
            sleep(2)
            with open(file, "w") as local_file:
                print('Writing file:', file)
                local_file.write(self._get_file(self.url + "/" + file))
            
        if changes:
            return True
        else:
            return False
