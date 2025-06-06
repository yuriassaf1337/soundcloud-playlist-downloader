<h1 align="center">
  🎵 soundcloud playlist downloader 🎵
</h1>
<p align="center">
  <img src="helper/sc.ico" width="100" alt="App Icon">
</p>
<p align="center">
  <strong>python-based tool to download soundcloud playlists or individual tracks (public or private)</strong>
</p>
<p align="center">
  <img src="helper/ex.png" width="550" alt="App Icon">
</p>

## 📌 features

- 🔗 supports both private and public links
- 📥 downloads all audio files into a single zip file to ease organization
- 🧰 simple interface 
- 🐍 built with python (for windows only)

---

## 🚀 getting started

### 🔧 prerequisites

- python 3.6 or higher  
- `pip` package manager  
- **[ffmpeg](https://www.gyan.dev/ffmpeg/builds/)** - needs to be installed and added to system path manually
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**

---

### 📦 manual installation

1. **clone or download the repository:**
    ```powershell
    git clone https://github.com/yuriassaf1337/soundcloud-playlist-downloader.git
    cd soundcloud-playlist-downloader
    ```
2. **recreate virtual enviroment**
    ```powershell
    python -m venv venv  
    ```
3. **activate the virtual enviroment**
    ```powershell
    venv\Scripts\activate
    ```
4. **install the requirements**
    ```powershell
    pip install -r requirements.txt
    ```

---

### 🎮 usage

#### ▶️ run from terminal (for development)
```powershell
python main.py
```

#### 📦 build .exe 
use [pyinstaller](https://pyinstaller.org/) to create a standalone executable:
```powershell
pyinstaller --onefile --windowed --icon=helper/sc.ico --add-data "helper/sc.ico;helper" main.py
```
