import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QProgressBar, QTextEdit, QDateEdit, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont

from config_manager import ConfigManager
from twitch_downloader import TwitchClipDownloader
from info_dialog import InfoDialog

class DownloaderThread(QThread):
    progress_updated = pyqtSignal(str)
    download_progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)

    def __init__(self, client_id, client_secret, channel_name, creator_name, start_date, end_date):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.channel_name = channel_name
        self.creator_name = creator_name
        self.start_date = start_date
        self.end_date = end_date
        self.is_cancelled = False
        
    def cancel(self):
        self.is_cancelled = True
        
    def run(self):
        try:
            downloader = TwitchClipDownloader(self.client_id, self.client_secret)
            
            self.progress_updated.emit("Recherche des IDs utilisateurs...")
            channel_id = downloader.get_user_id(self.channel_name)
            creator_id = downloader.get_user_id(self.creator_name)
            
            if not channel_id or not creator_id:
                self.finished.emit({"success": False, "message": "Impossible de trouver l'ID de la chaîne ou du créateur"})
                return
            
            self.progress_updated.emit("Recherche des clips disponibles...")
            clips = downloader.get_clips(channel_id, creator_id, self.start_date, self.end_date)
            
            if not clips:
                self.finished.emit({"success": False, "message": "Aucun clip trouvé pour la période spécifiée"})
                return
            
            self.progress_updated.emit(f"Nombre total de clips trouvés: {len(clips)}")
                
            output_dir = f"bulkdownload_{self.channel_name}_{self.creator_name}_{self.start_date.strftime('%d-%m-%Y')}_{self.end_date.strftime('%d-%m-%Y')}"
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, clip in enumerate(clips, 1):
                if self.is_cancelled:
                    self.progress_updated.emit("Téléchargement annulé après la fin du clip en cours...")
                    break
                
                self.progress_updated.emit(f"Traitement du clip {i}/{len(clips)}: {clip['title']}")
                if downloader.download_clip(clip, output_dir, 
                                         lambda c, t, f: self.download_progress.emit(c, t, f)):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                self.progress_updated.emit(f"Progression totale: {int((i/len(clips))*100)}%")
            
            result = {
                "success": True,
                "total": len(clips),
                "successful": successful_downloads,
                "failed": failed_downloads,
                "output_dir": output_dir,
                "cancelled": self.is_cancelled
            }
            self.finished.emit(result)
            
        except Exception as e:
            self.finished.emit({"success": False, "message": str(e)})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.init_ui()
        self.check_credentials()

    def init_ui(self):
        self.setWindowTitle("Bulk Twitch Clips Downloader")
        self.setFixedSize(800, 700)
        
        # Style général
        self.setStyleSheet("""
            QMainWindow {
                background-color: #18181b;
                color: #efeff1;
            }
            QLabel {
                color: #efeff1;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3c3c44;
                border-radius: 4px;
                background-color: #1f1f23;
                color: #efeff1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #9147ff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #772ce8;
            }
            QPushButton:disabled {
                background-color: #3c3c44;
            }
            QTextEdit {
                background-color: #1f1f23;
                color: #efeff1;
                border: 2px solid #3c3c44;
                border-radius: 4px;
                font-family: monospace;
            }
            QProgressBar {
                border: 2px solid #3c3c44;
                border-radius: 4px;
                text-align: center;
                background-color: #1f1f23;
            }
            QProgressBar::chunk {
                background-color: #9147ff;
            }
            QDateEdit {
                padding: 8px;
                border: 2px solid #3c3c44;
                border-radius: 4px;
                background-color: #1f1f23;
                color: #efeff1;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header avec bouton Info
        header_layout = QHBoxLayout()
        header = QLabel("Bulk Twitch Clips Downloader")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        info_button = QPushButton("ℹ")
        info_button.setFixedSize(30, 30)
        info_button.clicked.connect(self.show_info)
        header_layout.addWidget(info_button)
        layout.addLayout(header_layout)
        
        # Formulaire
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        # Chaine Twitch
        channel_layout = QHBoxLayout()
        channel_label = QLabel("Chaîne Twitch:")
        channel_label.setFixedWidth(150)
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Nom de la chaîne")
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.channel_input)
        form_layout.addLayout(channel_layout)
        
        # Créateur
        creator_layout = QHBoxLayout()
        creator_label = QLabel("Créateur des clips:")
        creator_label.setFixedWidth(150)
        self.creator_input = QLineEdit()
        self.creator_input.setPlaceholderText("Nom du créateur")
        creator_layout.addWidget(creator_label)
        creator_layout.addWidget(self.creator_input)
        form_layout.addLayout(creator_layout)
        
        # Dates
        dates_layout = QHBoxLayout()
        
        start_date_layout = QHBoxLayout()
        start_date_label = QLabel("Date de début:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("dd/MM/yyyy")
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addMonths(-1))
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addWidget(self.start_date_input)
        
        end_date_layout = QHBoxLayout()
        end_date_label = QLabel("Date de fin:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat("dd/MM/yyyy")
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        end_date_layout.addWidget(end_date_label)
        end_date_layout.addWidget(self.end_date_input)
        
        dates_layout.addLayout(start_date_layout)
        dates_layout.addSpacing(20)
        dates_layout.addLayout(end_date_layout)
        form_layout.addLayout(dates_layout)
        
        layout.addLayout(form_layout)
        
        # Bouton de téléchargement
        self.download_button = QPushButton("Démarrer le téléchargement")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Bouton d'annulation'
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)
        layout.addWidget(self.cancel_button)
        
        # Barres de progression
        progress_layout = QVBoxLayout()
        
        self.total_progress = QProgressBar()
        self.total_progress.setFormat("Progression totale: %p%")
        progress_layout.addWidget(self.total_progress)
        
        self.current_progress = QProgressBar()
        self.current_progress.setFormat("Clip en cours: %p%")
        progress_layout.addWidget(self.current_progress)
        
        layout.addLayout(progress_layout)
        
        # Zone de logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(200)
        layout.addWidget(self.log_output)
        
        self.downloader_thread = None

    def show_info(self):
        info_dialog = InfoDialog(self)
        info_dialog.exec()

    def check_credentials(self):
        client_id = self.config_manager.get_client_id()
        client_secret = self.config_manager.get_client_secret()
        
        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Configuration manquante",
                "Veuillez configurer votre Client ID et Client Secret dans le fichier config.json"
            )
            self.download_button.setEnabled(False)

    def log(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
        
    def start_download(self):
        if not self.channel_input.text() or not self.creator_input.text():
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
            
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.channel_input.setEnabled(False)
        self.creator_input.setEnabled(False)
        self.start_date_input.setEnabled(False)
        self.end_date_input.setEnabled(False)
        
        self.total_progress.setValue(0)
        self.current_progress.setValue(0)
        
        self.downloader_thread = DownloaderThread(
            self.config_manager.get_client_id(),
            self.config_manager.get_client_secret(),
            self.channel_input.text(),
            self.creator_input.text(),
            self.start_date_input.date().toPyDate(),
            self.end_date_input.date().toPyDate()
        )
        
        self.downloader_thread.progress_updated.connect(self.update_progress)
        self.downloader_thread.download_progress.connect(self.update_download_progress)
        self.downloader_thread.finished.connect(self.download_finished)
        
        self.downloader_thread.start()
        
    def update_progress(self, message):
        self.log(message)
        if message.startswith("Progression totale:"):
            percentage = int(message.split(":")[1].strip().replace("%", ""))
            self.total_progress.setValue(percentage)
        
    def update_download_progress(self, current, total, filename):
        percentage = int((current / total) * 100) if total > 0 else 0
        self.current_progress.setValue(percentage)
        self.current_progress.setFormat(f"Téléchargement de {filename}: {percentage}%")

    def cancel_download(self):
        if self.downloader_thread and self.downloader_thread.isRunning():
            self.log("Annulation demandée... Attente de la fin du clip en cours...")
            self.cancel_button.setEnabled(False)
            self.downloader_thread.cancel()

    def download_finished(self, result):
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.channel_input.setEnabled(True)
        self.creator_input.setEnabled(True)
        self.start_date_input.setEnabled(True)
        self.end_date_input.setEnabled(True)
        
        if result["success"]:
            status = "annulé" if result.get("cancelled", False) else "terminé"
            self.log(f"\nTéléchargement {status} !")
            self.log(f"Clips téléchargés: {result['successful']}/{result['total']}")
            self.log(f"Échecs: {result['failed']}")
            self.log(f"Dossier de sortie: {result['output_dir']}")
        else:
            self.log(f"\nErreur: {result['message']}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()