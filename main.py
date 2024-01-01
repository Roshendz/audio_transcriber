import os
import sys

import speech_recognition as sr
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, \
    QProgressDialog, QStyle, QMessageBox
from pydub import AudioSegment

AudioSegment.converter = "C:\\FFmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffmpeg = "C:\\FFmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = "C:\\FFmpeg\\bin\\ffprobe.exe"


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.btn = None
        self.save_btn = None
        self.info_btn = None
        self.text_edit = None
        self.audio_file_name = None
        self.initUI()

    def initUI(self):
        self.text_edit = QTextEdit()
        self.btn = QPushButton(' Select Audio File')
        self.btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btn.clicked.connect(self.select_audio_file)
        self.save_btn = QPushButton(' Save to Text File')
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.save_to_text_file)
        self.info_btn = QPushButton(' Info')
        self.info_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.info_btn.clicked.connect(self.show_info)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn)
        hbox.addWidget(self.save_btn)
        hbox.addWidget(self.info_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.text_edit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setWindowTitle('Audio Transcriber')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setGeometry(300, 300, 500, 500)
        self.show()

    def select_audio_file(self):
        fname = QFileDialog.getOpenFileName(self)
        if fname[0]:
            self.audio_file_name = os.path.splitext(os.path.basename(fname[0]))[0]
            audio = AudioSegment.from_mp3(fname[0])
            if len(audio) > 4 * 60 * 1000:  # audio duration is more than 4 minutes
                QMessageBox.warning(self, 'Warning', 'You cannot transcribe more than 4 minutes.')
                return
            try:
                # Show a progress dialog while the audio file is being transcribed
                progress = QProgressDialog("Transcribing audio file...", None, 0, 0, self)
                progress.setCancelButton(None)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                QApplication.processEvents()

                text = self.transcribe_audio(fname[0])

                progress.close()

                self.text_edit.setText(text)
            except Exception as e:
                print(f"An error occurred: {e}")

    def save_to_text_file(self):
        if self.text_edit.toPlainText():
            with open(f"{self.audio_file_name}.txt", "w") as file:
                file.write(self.text_edit.toPlainText())

    def show_info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Audio Transcriber v1.0\n\nThis application transcribes audio files to text. Please note that it can only transcribe audio files that are 4 minutes or shorter.")
        msg.setWindowTitle("Info")
        msg.exec_()

    def transcribe_audio(self, audio_file):
        r = sr.Recognizer()
        try:
            # Convert mp3 file to wav
            audio = AudioSegment.from_mp3(audio_file)
            audio.export("transcript.wav", format="wav")
            with sr.AudioFile("transcript.wav") as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"
        except IOError:
            return f"Could not find or read the audio file; {audio_file}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
