from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices  # Correction de l'import

class InfoDialog(QDialog):
    VERSION = "1.0.0"
    TWITTER_URL = "https://x.com/foedi_"
    GITHUB_URL = "https://github.com/FOEDI"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")
        self.setFixedSize(400, 200)
        self.setup_ui()
        
        self.setStyleSheet("""
            QDialog {
                background-color: #18181b;
                color: #efeff1;
            }
            QLabel {
                color: #efeff1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #9147ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #772ce8;
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Bulk Twitch Clips Downloader")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Version
        version_label = QLabel(f"Version: {self.VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addSpacing(20)
        
        # Liens sociaux
        social_layout = QHBoxLayout()
        
        twitter_btn = QPushButton("Twitter")
        twitter_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.TWITTER_URL))
        )
        
        github_btn = QPushButton("GitHub")
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.GITHUB_URL))
        )
        
        social_layout.addWidget(twitter_btn)
        social_layout.addWidget(github_btn)
        
        layout.addLayout(social_layout)
        
        layout.addSpacing(20)
        
        # Créateur
        creator_label = QLabel("Créé par Foedi")
        creator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(creator_label)
        
        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)