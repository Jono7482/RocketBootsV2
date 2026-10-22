#!/usr/bin/env bash
# Rocket Boots - WSL Local APK Build Script
set -e

echo "=== Rocket Boots Android APK Builder ==="

# 1. Install dependencies
echo "[1/4] Installing dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential libtool libltdl-dev autoconf automake pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev patch gettext git zip unzip openjdk-17-jdk python3-dev

# 2. Install Buildozer
echo "[2/4] Installing Buildozer and Cython..."
pip install --user --upgrade "Cython==0.29.33" virtualenv "git+https://github.com/kivy/buildozer.git"
export PATH=$PATH:~/.local/bin

# 3. Build APK
echo "[3/4] Building APK (Android API 34, 64-bit ARM)..."
buildozer -v android debug

# 4. Result
echo "[4/4] Build complete! APK is located in the bin/ folder:"
ls -lh bin/*.apk
