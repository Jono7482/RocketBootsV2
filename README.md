# 🚀 Rocket Boots v0.5.0

Modernized version of Jonathan Brooks' 2017 Rocket Boots game, updated to **Python 3**, **Kivy 2.3+**, and configured for **modern Android (Android 14 / API 34, 64-bit ARM)**.

---

## 🎮 How to Play on Windows Right Now
1. Double-click `run_game.bat` (or run `py main.py` in PowerShell/Command Prompt).
2. Tap / hold mouse click to activate your Rocket Boots!

---

## 📱 How to Build the Android APK (Install on your Phone)

Because the Android compilation tools (`python-for-android` / `buildozer`) require a Linux environment with the Android NDK, here are the two easiest, 100% free ways to build your installable `.apk`:

### Method 1: Google Colab (Recommended — 1 Click, No Setup Required)
1. Open [Google Colab](https://colab.research.google.com/) in your browser.
2. Click **File** > **Upload notebook** and choose `RocketBoots_Build_APK.ipynb` from this folder.
3. Click **Runtime** > **Run all** (or `Ctrl+F9`).
4. When prompted in Step 2, upload the included `RocketBoots-v0.5.0-Source.zip` file.
5. In ~10 minutes, Colab will build the APK and **automatically download the `.apk` file** directly to your browser!

### Method 2: GitHub Actions (Automated Cloud Build)
1. Push this repository to your GitHub account:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/RocketBoots.git
   git branch -M main
   git push -u origin main
   ```
2. Open your repository on GitHub and go to the **Actions** tab.
3. The **Build Rocket Boots APK** workflow will run automatically.
4. Once finished, click on the workflow run and download the **RocketBoots-Android-APK** artifact!

### Method 3: Local Build with WSL (Windows Subsystem for Linux)
If you have WSL installed (`wsl --install`):
```bash
wsl
cd /mnt/c/Jono/AntiGravity\ RocketBoots\ V2
chmod +x build_apk_wsl.sh
./build_apk_wsl.sh
```

---

## 📲 How to Install the APK on Your Cell Phone
1. Transfer the compiled `.apk` to your phone (via USB cable, Google Drive, email, or WhatsApp/Telegram).
2. On your Android phone, tap the `.apk` file to install it.
3. If prompted:
   - Allow **"Install unknown apps"** from your file manager or browser.
   - If Google Play Protect displays a message (*"Unrecognized app"*), tap **"More details"** -> **"Install anyway"** (standard for personal debug apps).
4. Launch **Rocket Boots** and enjoy!
