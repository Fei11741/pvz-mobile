
<<<<<<< SEARCH
=======
[app]
title = 植物大战僵尸
package.name = pvz
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 31
android.minapi = 21
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
>>>>>>> REPLACE


.github/workflows/build.yml


<<<<<<< SEARCH
=======
name: Build APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-17-jdk \
            autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
            libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

      - name: Install Buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer cython==0.29.36

      - name: Build APK
        run: |
          buildozer -v android debug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: pvz-apk
          path: bin/*.apk
>>>>>>> REPLACE


