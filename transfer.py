import os
import sys
import stat
import paramiko
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QFileDialog
from PyQt5.QtCore import Qt

class FileTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.local_dir = ""
        self.queue = []  # List to store files to be sent
        self.remote_dir = "/home/pi/RetroPie/splashscreens"  # Replace with your actual remote directory
        self.current_local_dir = ""  # Keep track of the current local directory
        self.current_remote_dir = ""  # Keep track of the current remote directory

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
        remote_label = QLabel("Remote Directory:")
        queue_label = QLabel("Queue:")

        self.local_entry = QLabel()
        self.remote_entry = QLabel()
        self.queue_listbox = QListWidget()

        local_button = QPushButton("Open Local Directory")
        local_button.clicked.connect(self.open_local_directory)

        remote_button = QPushButton("Open Remote Directory")
        remote_button.clicked.connect(self.open_remote_directory)

        add_button = QPushButton("Add Files to Queue")
        add_button.clicked.connect(self.add_files_to_queue)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected)

        go_up_local_button = QPushButton("Go Up (Local)")
        go_up_local_button.clicked.connect(self.go_up_local_directory)

        go_up_remote_button = QPushButton("Go Up (Remote)")
        go_up_remote_button.clicked.connect(self.go_up_remote_directory)

        send_button = QPushButton("Send Files")
        send_button.clicked.connect(self.send_files)
        send_button.setStyleSheet("background-color: #4CAF50; color: #FFF;")  # Green button with white text

        self.local_listbox = QListWidget()
        self.remote_listbox = QListWidget()

        self.local_listbox.itemDoubleClicked.connect(self.on_local_item_double_clicked)  # Double-click event handler for local
        self.remote_listbox.itemDoubleClicked.connect(self.on_remote_item_double_clicked)  # Double-click event handler for remote

        left_layout.addWidget(local_label)
        left_layout.addWidget(self.local_entry)
        left_layout.addWidget(local_button)
        left_layout.addWidget(self.local_listbox)
        left_layout.addWidget(go_up_local_button)  # Added "Go Up (Local)" button
        left_layout.addWidget(add_button)

        right_layout.addWidget(remote_label)
        right_layout.addWidget(self.remote_entry)
        right_layout.addWidget(remote_button)
        right_layout.addWidget(self.remote_listbox)
        right_layout.addWidget(go_up_remote_button)  # Added "Go Up (Remote)" button
        right_layout.addWidget(queue_label)
        right_layout.addWidget(self.queue_listbox)
        right_layout.addWidget(remove_button)
        right_layout.addWidget(send_button)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        central_widget.setLayout(layout)

        self.setStyleSheet("QMainWindow { background-color: #333; color: #FFF; }"
                           "QLabel { color: #FFF; }"
                           "QListWidget { background-color: #444; color: #FFF; border: none; }"
                           "QListWidget::item:selected { background-color: #555; }")

    def open_local_directory(self):
        self.current_local_dir = QFileDialog.getExistingDirectory(self, "Open Local Directory")
        self.local_entry.setText(self.current_local_dir)
        self.populate_local_listbox()

    def open_remote_directory(self):
        try:
            transport = paramiko.Transport(('192.168.1.137', 22))
            transport.connect(username='pi', password='password')
            sftp = transport.open_sftp_client()
            self.current_remote_dir = self.remote_dir
            self.remote_entry.setText(self.current_remote_dir)
            self.populate_remote_listbox(sftp)
            sftp.close()
            transport.close()
        except Exception as e:
            print(f"Error: {str(e)}")

    def add_files_to_queue(self):
        selected_items = self.local_listbox.selectedItems()
        for item in selected_items:
            file_name = item.text()
            local_path = os.path.join(self.current_local_dir, file_name)
            self.queue.append(local_path)
            self.queue_listbox.addItem(file_name)

    def remove_selected(self):
        selected_items = self.queue_listbox.selectedItems()
        for item in selected_items:
            index = self.queue_listbox.row(item)
            del self.queue[index]
            self.queue_listbox.takeItem(index)

    def populate_local_listbox(self):
        self.local_listbox.clear()
        if self.current_local_dir:
            for item in os.listdir(self.current_local_dir):
                is_directory = os.path.isdir(os.path.join(self.current_local_dir, item))
                item_text = f"[Dir] {item}" if is_directory else item
                self.local_listbox.addItem(item_text)

    def populate_remote_listbox(self, sftp):
        self.remote_listbox.clear()
        if self.current_remote_dir:
            remote_items = sftp.listdir_attr(self.current_remote_dir)
            for item in remote_items:
                is_directory = stat.S_ISDIR(item.st_mode)
                item_text = f"[Dir] {item.filename}" if is_directory else item.filename
                self.remote_listbox.addItem(item_text)

    def on_local_item_double_clicked(self, item):
        item_text = item.text()
        if item_text.startswith("[Dir] "):
            # Extract the directory name without "[Dir] " prefix
            dir_name = item_text[6:]
            # Navigate into the directory by updating the current_local_dir and refreshing the list
            self.current_local_dir = os.path.join(self.current_local_dir, dir_name)
            self.local_entry.setText(self.current_local_dir)
            self.populate_local_listbox()

    def on_remote_item_double_clicked(self, item):
        item_text = item.text()
        if item_text.startswith("[Dir] "):
            # Extract the directory name without "[Dir] " prefix
            dir_name = item_text[6:]
            # Navigate into the directory by updating the current_remote_dir and refreshing the list
            self.current_remote_dir = os.path.join(self.current_remote_dir, dir_name).replace("\\", "/")  # Replace backslashes with forward slashes
            self.remote_entry.setText(self.current_remote_dir)
            try:
                transport = paramiko.Transport(('192.168.1.137', 22))
                transport.connect(username='pi', password='password')
                sftp = transport.open_sftp_client()
                self.populate_remote_listbox(sftp)
                sftp.close()
                transport.close()
            except Exception as e:
                print(f"Error: {str(e)}")


    def go_up_local_directory(self):
        if self.current_local_dir:
            self.current_local_dir = os.path.dirname(self.current_local_dir)
            self.local_entry.setText(self.current_local_dir)
            self.populate_local_listbox()

    def go_up_remote_directory(self):
        if self.current_remote_dir:
            self.current_remote_dir = os.path.dirname(self.current_remote_dir)
            self.remote_entry.setText(self.current_remote_dir)
            try:
                transport = paramiko.Transport(('192.168.1.137', 22))
                transport.connect(username='pi', password='password')
                sftp = transport.open_sftp_client()
                self.populate_remote_listbox(sftp)
                sftp.close()
                transport.close()
            except Exception as e:
                print(f"Error: {str(e)}")

    def send_files(self):
        if self.queue and self.remote_dir:
            try:
                print(f"Local Directory: {self.current_local_dir}")
                print(f"Remote Directory: {self.current_remote_dir}")
                transport = paramiko.Transport(('192.168.1.137', 22))
                transport.connect(username='pi', password='password')
                sftp = transport.open_sftp_client()
                for local_path in self.queue:
                    file_name = os.path.basename(local_path)
                    remote_path = os.path.join(self.current_remote_dir, file_name).replace("\\", "/")  # Replace backslashes with forward slashes
                    print(f"Sending file: {file_name} to {remote_path}")
                    sftp.put(local_path, remote_path)
                sftp.close()
                transport.close()
                self.queue = []  # Clear the queue after sending
                self.queue_listbox.clear()
                print("Files sent successfully.")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use the Fusion style for dark mode

    window = FileTransferApp()
    window.show()

    sys.exit(app.exec_())
