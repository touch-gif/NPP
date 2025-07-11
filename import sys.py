import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

class TextSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("这是一个示例文本。\n可以在这里查找特定的内容。\n这个文本可以是多行的。")
        layout.addWidget(self.text_edit)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("请输入要查找的内容")
        layout.addWidget(self.query_input)

        search_button = QPushButton("查找")
        search_button.clicked.connect(self.search_text)
        layout.addWidget(search_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setWindowTitle('文本查找示例')
        self.setGeometry(100, 100, 400, 300)

    def search_text(self):
        query = self.query_input.text()
        cursor = self.text_edit.textCursor()

        # 清除之前的选中状态
        cursor.clearSelection()

        # 查找文本
        found = self.text_edit.find(query)

        if found:
            self.status_label.setText(f"找到: '{query}'")
            self.text_edit.setTextCursor(cursor)
        else:
            self.status_label.setText(f"未找到: '{query}'")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextSearchApp()
    window.show()
    sys.exit(app.exec_())