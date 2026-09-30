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
