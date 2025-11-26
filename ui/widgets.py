"""
自定义组件模块
"""

try:
    from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
    from PyQt6.QtGui import QFont
except ImportError:
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtGui import QFont


def create_natural_expression_item(idx, text, explanation, theme, play_callback, tts_available):
    """创建单个自然表达项（带播放按钮）"""
    item_widget = QWidget()
    item_layout = QHBoxLayout(item_widget)
    item_layout.setContentsMargins(5, 5, 5, 5)
    
    # 左侧文本区域
    text_widget = QWidget()
    text_layout = QVBoxLayout(text_widget)
    text_layout.setContentsMargins(0, 0, 0, 0)
    
    # 主文本
    text_label = QLabel(f"<b>{idx}. {text}</b>")
    text_label.setFont(QFont("Microsoft YaHei", 11))
    text_label.setWordWrap(True)
    text_layout.addWidget(text_label)
    
    # 解释文本
    if explanation:
        explain_label = QLabel(explanation)
        explain_label.setFont(QFont("Microsoft YaHei", 9))
        explain_label.setStyleSheet(f"color: {theme['secondary_text']}; margin-left: 20px;")
        explain_label.setWordWrap(True)
        text_layout.addWidget(explain_label)
    
    item_layout.addWidget(text_widget, stretch=1)
    
    # 右侧播放按钮
    play_btn = QPushButton("🔊")
    play_btn.setFixedSize(40, 40)
    play_btn.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            border: 2px solid #4CAF50;
            border-radius: 20px;
            background-color: white;
        }
        QPushButton:hover {
            background-color: #e8f5e9;
        }
        QPushButton:pressed {
            background-color: #c8e6c9;
        }
    """)
    play_btn.clicked.connect(lambda: play_callback(text))
    play_btn.setEnabled(tts_available)
    play_btn.setToolTip("朗读此表达")
    item_layout.addWidget(play_btn)
    
    # 添加分隔线
    item_widget.setStyleSheet("""
        QWidget {
            border-bottom: 1px solid #e0e0e0;
            padding: 5px;
        }
    """)
    
    return item_widget
