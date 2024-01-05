import os
import sys
import time

import speech_recognition as sr
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, \
    QProgressDialog, QStyle, QMessageBox, QSlider, QLabel
from PyQt5.QtCore import QUrl, QTime
from pydub import AudioSegment
from reportlab.pdfgen import canvas
import qdarkstyle

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
        self.player = None
        self.slider = None
        self.label_duration = None
        self.play_btn = None
        self.pause_btn = None
        self.mute_btn = None
        self.initUI()

    def initUI(self):
        # Set the window transparent
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet("background-color:transparent;")

        self.text_edit = QTextEdit()
        self.btn = QPushButton(' Select Audio File')
        self.btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btn.clicked.connect(self.select_audio_file)
        self.save_btn = QPushButton(' Export Transcription')
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.save_to_text_file)
        self.info_btn = QPushButton(' Info')
        self.info_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.info_btn.clicked.connect(self.show_info)

        # Style the buttons
        button_style = """
                    QPushButton {
                        color: #333;
                        border: 2px solid #555;
                        border-radius: 11px;
                        padding: 5px;
                        background: qradialgradient(cx: 0.3, cy: -0.4,
                                                    fx: 0.3, fy: -0.4,
                                                    radius: 1.35, stop: 0 #fff, stop: 1 #888);
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background: qradialgradient(cx: 0.3, cy: -0.4,
                                                    fx: 0.3, fy: -0.4,
                                                    radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
                    }
                    QPushButton:pressed {
                        background: qradialgradient(cx: 0.4, cy: -0.1,
                                                    fx: 0.4, fy: -0.1,
                                                    radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
                    }
                """
        self.btn.setStyleSheet(button_style)
        self.save_btn.setStyleSheet(button_style)
        self.info_btn.setStyleSheet(button_style)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn)
        hbox.addWidget(self.save_btn)
        hbox.addWidget(self.info_btn)

        # Create a QMediaPlayer object
        self.player = QMediaPlayer()

        # Create a QSlider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Create a label for the song duration
        self.label_duration = QLabel()
        self.label_duration.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.label_duration.setStyleSheet("QLabel { color : white; }")

        # Create labels for the current playback position
        self.label_position = QLabel()

        # Create play and pause buttons
        self.play_btn = QPushButton('Play')
        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn = QPushButton('Pause')
        self.pause_btn.clicked.connect(self.pause_audio)

        # Style the play and pause buttons
        self.play_btn.setStyleSheet(button_style)
        self.pause_btn.setStyleSheet(button_style)

        # Create mute button
        self.mute_btn = QPushButton()
        self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_btn.setCheckable(False)
        self.mute_btn.clicked.connect(self.mute_audio)

        # Add the controls to a horizontal layout
        controls = QHBoxLayout()
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.mute_btn)
        controls.addWidget(self.slider)
        controls.addWidget(self.label_position)
        controls.addWidget(self.label_duration)
        # controls.addWidget(self.label_remaining)

        vbox = QVBoxLayout()
        vbox.addWidget(self.text_edit)
        # Add the controls layout to the main vertical layout
        vbox.addLayout(controls)
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
                progress.setGeometry(350, 350, 300, 30)
                progress.setWindowTitle(' ')
                progress.show()
                QApplication.processEvents()

                text = self.transcribe_audio(fname[0], progress)

                progress.close()

                self.text_edit.setText(text)

                # Set the media content
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(fname[0])))

                # Connect the media player signals
                self.player.positionChanged.connect(self.position_changed)
                self.player.durationChanged.connect(self.duration_changed)
            except Exception as e:
                print(f"An error occurred: {e}")

    # def save_to_text_file(self):
    #     if self.text_edit.toPlainText():
    #         with open(f"{self.audio_file_name}.txt", "w") as file:
    #             file.write(self.text_edit.toPlainText())

    def save_to_text_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt);;PDF Files (*.pdf)",
                                                  options=options)
        if fileName:
            # If the user doesn't select a file type, default to .txt
            if _ == 'All Files (*)':
                _ = 'Text Files (*.txt)'
            if _.find('*.txt') != -1:
                # Split the text into words
                words = self.text_edit.toPlainText().split()
                # Group the words into lines of 20 words each
                lines = [' '.join(words[i:i + 20]) for i in range(0, len(words), 20)]
                # Join the lines with newline characters to form the final text
                text = '\n'.join(lines)
                # Write the text to the file
                with open(fileName if fileName.endswith('.txt') else fileName + '.txt', "w") as file:
                    file.write(text)
            elif _.find('*.pdf') != -1:
                c = canvas.Canvas(fileName if fileName.endswith('.pdf') else fileName + '.pdf')
                textobject = c.beginText()
                textobject.setTextOrigin(15, 730)
                # Split the text into words
                words = self.text_edit.toPlainText().split()
                # Group the words into lines of 15 words each
                lines = [' '.join(words[i:i + 15]) for i in range(0, len(words), 15)]
                for line in lines:
                    # Add each line to the text object
                    textobject.textLine(line.strip())
                c.drawText(textobject)
                c.save()

            # Show a message box after the file is saved
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("File has been saved successfully!")
            msg.setWindowTitle("Success")
            msg.exec_()

    def show_info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Audio Transcriber v1.3.0.0\n\nThis application transcribes audio files to text. Please note that it can only transcribe audio files that are 4 minutes or shorter.")
        msg.setWindowTitle("Info")
        msg.exec_()

    def transcribe_audio(self, audio_file, progress):
        r = sr.Recognizer()
        try:
            # Convert mp3 file to wav
            audio = AudioSegment.from_mp3(audio_file)
            audio.export("transcript.wav", format="wav")
            with sr.AudioFile("transcript.wav") as source:
                audio_data = r.record(source)
                # Update the progress value
                progress.setValue(20)
                QApplication.processEvents()
                text = r.recognize_google(audio_data)
                # Update the progress value
                progress.setValue(100)
                QApplication.processEvents()
                return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"
        except IOError:
            return f"Could not find or read the audio file; {audio_file}"

    def play_audio(self):
        self.player.play()

    def pause_audio(self):
        self.player.pause()

    def set_position(self, position):
        self.player.setPosition(position)

    def position_changed(self, position):
        # Update the slider position
        self.slider.setValue(position)

        # Update the current playback position label
        self.label_position.setText(QTime(0, 0).addMSecs(position).toString())

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.label_duration.setText(time.strftime('%H:%M:%S', time.gmtime(duration / 1000)))

    def mute_audio(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        else:
            self.player.setMuted(True)
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    ex = MyApp()
    sys.exit(app.exec_())
