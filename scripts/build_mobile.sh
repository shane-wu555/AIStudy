#!/bin/bash

# Flutter移动端构建脚本

echo "📱 开始构建Flutter应用..."

cd mobile_app

# 1. 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter未安装，请先安装Flutter SDK"
    exit 1
fi

# 2. 获取依赖
echo "📦 获取Flutter依赖..."
flutter pub get

# 3. 生成代码（如果使用了代码生成）
# flutter pub run build_runner build --delete-conflicting-outputs

# 4. 清理构建
echo "🧹 清理旧构建..."
flutter clean

# 5. 选择构建平台
echo "请选择构建平台:"
echo "1) Android APK"
echo "2) Android AAB"
echo "3) iOS"
echo "4) Web"
echo "5) Windows"
echo "6) Linux"

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo "🔨 构建Android APK..."
        flutter build apk --release
        echo "✅ APK构建完成: build/app/outputs/flutter-apk/app-release.apk"
        ;;
    2)
        echo "🔨 构建Android AAB..."
        flutter build appbundle --release
        echo "✅ AAB构建完成: build/app/outputs/bundle/release/app-release.aab"
        ;;
    3)
        echo "🔨 构建iOS..."
        flutter build ios --release
        echo "✅ iOS构建完成"
        ;;
    4)
        echo "🔨 构建Web..."
        flutter build web --release
        echo "✅ Web构建完成: build/web/"
        ;;
    5)
        echo "🔨 构建Windows..."
        flutter build windows --release
        echo "✅ Windows构建完成: build/windows/runner/Release/"
        ;;
    6)
        echo "🔨 构建Linux..."
        flutter build linux --release
        echo "✅ Linux构建完成: build/linux/x64/release/bundle/"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo "🎉 构建完成！"
