"""
Cross-Cultural Translation Assistant - Desktop GUI Version
跨文化智能翻译助手 - 桌面版主入口
"""

import sys

# 尝试导入 Qt 框架
QT_FRAMEWORK = None
try:
    from PyQt6.QtWidgets import QApplication
    QT_FRAMEWORK = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import QApplication
        QT_FRAMEWORK = "PySide6"
    except ImportError:
        print("=" * 60)
        print("ERROR: Neither PyQt6 nor PySide6 is installed!")
        print("=" * 60)
        print("\nPlease install one of the following:")
        print("\n  Option 1 (PyQt6):")
        print("    pip install PyQt6==6.6.1")
        print("\n  Option 2 (PySide6):")
        print("    pip install PySide6==6.6.1")
        print("\n" + "=" * 60)
        sys.exit(1)

print(f"✓ Using {QT_FRAMEWORK} for GUI")

# 检查可选依赖
try:
    import vosk
    import pyaudio
    print("✓ Vosk speech recognition available")
except ImportError as e:
    print(f"⚠️ Vosk not available: {e}")
    print("   Install with: pip install vosk pyaudio")

try:
    import pyttsx3
    print("✓ pyttsx3 TTS available")
except ImportError:
    print("⚠️ pyttsx3 not available. Install with: pip install pyttsx3")

from ui import TranslationApp


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TranslationApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()