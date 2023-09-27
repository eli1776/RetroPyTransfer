import os
import sys
import paramiko
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QFileDialog
from PyQt5.QtCore import Qt

class FileTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.local_dir = ""
        self.queue = []  # List to store files to be sent
        self.remote_dir = "/path/to/hardcoded/remote/directory"  # Replace with your actual remote directory

        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Transfer App")
        self.setGeometry(100, 100, 800, 500)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        local_label = QLabel("Local Directory:")
        queue_label = QLabel("Queue:")

        self.local_entry = QLabel()
        self.queue_listbox = QListWidget()

        local_button = QPushButton("Open Local Directory")
        local_button.clicked.connect(self.open_local_directory)

        add_button = QPushButton("Add Files to Queue")
        add_button.clicked.connect(self.add_files_to_queue)

        send_button = QPushButton("Send Files")
        send_button.clicked.connect(self.send_files)
        send_button.setStyleSheet("background-color: #4CAF50; color: #FFF;")  # Green button with white text

        self.local_listbox = QListWidget()

        left_layout.addWidget(local_label)
        left_layout.addWidget(self.local_entry)
        left_layout.addWidget(local_button)
        left_layout.addWidget(self.local_listbox)
        left_layout.addWidget(add_button)

        right_layout.addWidget(queue_label)
        right_layout.addWidget(self.queue_listbox)
        right_layout.addWidget(send_button)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        central_widget.setLayout(layout)

        self.setStyleSheet("QMainWindow { background-color: #333; color: #FFF; }"
                           "QLabel { color: #FFF; }"
                           "QListWidget { background-color: #444; color: #FFF; border: none; }"
                           "QListWidget::item:selected { background-color: #555; }")

    def open_local_directory(self):
        self.local_dir = QFileDialog.getExistingDirectory(self, "Open Local Directory")
        self.local_entry.setText(self.local_dir)
        self.populate_local_listbox()

    def add_files_to_queue(self):
        selected_items = self.local_listbox.selectedItems()
        for item in selected_items:
            file_name = item.text()
            local_path = os.path.join(self.local_dir, file_name)
            self.queue.append(local_path)
            self.queue_listbox.addItem(file_name)

    def populate_local_listbox(self):
        self.local_listbox.clear()
        if self.local_dir:
            for item in os.listdir(self.local_dir):
                self.local_listbox.addItem(item)

    def send_files(self):
        if self.queue and self.remote_dir:
            try:
                transport = paramiko.Transport(('your_raspberry_pi_ip', 22))
                transport.connect(username='your_username', password='your_password')
                sftp = transport.open_sftp()
                for local_path in self.queue:
                    file_name = os.path.basename(local_path)
                    remote_path = os.path.join(self.remote_dir, file_name)
                    sftp.put(local_path, remote_path)
                sftp.close()
                transport.close()
                self.queue = []  # Clear the queue after sending
                self.queue_listbox.clear()
            except Exception as e:
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use the Fusion style for dark mode

    window = FileTransferApp()
    window.show()

    sys.exit(app.exec_())
