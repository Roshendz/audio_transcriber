import os
import shutil
import sys
import time

import speech_recognition as sr
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, \
    QProgressDialog, QStyle, QMessageBox, QSlider, QLabel, QLineEdit, QRadioButton, QButtonGroup, QToolBar, QAction, \
    QComboBox, QFontComboBox
from PyQt5.QtCore import QUrl, QTime
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from gtts import gTTS
import qdarkstyle
from moviepy.editor import VideoFileClip

from volume_dialog import VolumeDialog

AudioSegment.converter = "C:\\FFmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffmpeg = "C:\\FFmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = "C:\\FFmpeg\\bin\\ffprobe.exe"


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.language = None
        self.btn_mp4 = None
        self.font_box = None
        self.font_size_box = None
        self.formatting_toolbar = None
        self.label_position = None
        self.volume_dialog = None
        self.underline_action = None
        self.bold_action = None
        self.italic_action = None
        self.language_group = None
        self.italian_button = None
        self.english_button = None
        self.search_bar = None
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
        self.btn_mp4 = QPushButton(' Select MP4 File')
        self.btn_mp4.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btn_mp4.clicked.connect(self.select_mp4_file)

        self.speech_btn = QPushButton('Generate Speech')
        self.speech_btn.setIcon(self.style().standardIcon(QStyle.SP_DriveCDIcon))
        self.speech_btn.setToolTip('Generate speech from the inserted text')
        self.speech_btn.clicked.connect(self.generate_speech)
        self.export_btn = QPushButton('Export Speech')
        self.export_btn.setToolTip('Export the generated speech')
        self.export_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.export_btn.clicked.connect(self.export_speech)

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
        self.btn_mp4.setStyleSheet(button_style)
        self.speech_btn.setStyleSheet(button_style)
        self.export_btn.setStyleSheet(button_style)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn)
        hbox.addWidget(self.btn_mp4)
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
        self.play_btn.setToolTip('Play the audio')
        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn = QPushButton('Pause')
        self.pause_btn.setToolTip('Pause the audio')
        self.pause_btn.clicked.connect(self.pause_audio)

        # Style the play and pause buttons
        self.play_btn.setStyleSheet(button_style)
        self.pause_btn.setStyleSheet(button_style)

        # Create mute button
        self.mute_btn = QPushButton()
        self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_btn.setCheckable(False)
        # self.mute_btn.clicked.connect(self.mute_audio)
        self.mute_btn.clicked.connect(self.show_volume_dialog)

        # Create a QLineEdit for the search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.setToolTip('Search the transcription')
        self.search_bar.textChanged.connect(self.highlight_text)

        # Create radio buttons for language selection
        self.english_button = QRadioButton('English')
        self.italian_button = QRadioButton('Italian')

        # Make English the default selection
        self.english_button.setChecked(True)

        # Add the radio buttons to a button group
        self.language_group = QButtonGroup()
        self.language_group.addButton(self.english_button, 0)
        self.language_group.addButton(self.italian_button, 1)

        # Create a horizontal layout for the search bar and radio buttons
        search_and_language_layout = QHBoxLayout()
        search_and_language_layout.addWidget(self.search_bar)
        search_and_language_layout.addWidget(self.english_button)
        search_and_language_layout.addWidget(self.italian_button)

        # Create a toolbar for formatting actions
        self.formatting_toolbar = QToolBar()

        # Create actions for bold, italic, and underline
        self.bold_action = QAction('Bold', self)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.set_bold)
        self.formatting_toolbar.addAction(self.bold_action)

        self.italic_action = QAction('Italic', self)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.set_italic)
        self.formatting_toolbar.addAction(self.italic_action)

        self.underline_action = QAction('Underline', self)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.set_underline)
        self.formatting_toolbar.addAction(self.underline_action)

        # Create a font size combo box
        self.font_size_box = QComboBox()
        self.font_size_box.addItems([str(i) for i in range(6, 50)])
        self.font_size_box.currentTextChanged.connect(self.set_font_size)
        self.formatting_toolbar.addWidget(self.font_size_box)

        # Create a font combo box
        self.font_box = QFontComboBox()
        self.font_box.currentFontChanged.connect(self.set_font)
        self.formatting_toolbar.addWidget(self.font_box)

        # Add the controls to a horizontal layout
        controls = QHBoxLayout()
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.mute_btn)
        controls.addWidget(self.slider)
        controls.addWidget(self.label_position)
        controls.addWidget(self.label_duration)
        # controls.addWidget(self.label_remaining)

        h_tts_box = QHBoxLayout()
        h_tts_box.addWidget(self.speech_btn)
        h_tts_box.addWidget(self.export_btn)

        vbox = QVBoxLayout()
        # Add the search bar to your layout
        vbox.addLayout(search_and_language_layout)
        vbox.addWidget(self.text_edit)
        # Add the toolbar to your layout
        vbox.addWidget(self.formatting_toolbar)
        # Add the controls layout to the main vertical layout
        vbox.addLayout(controls)
        vbox.addLayout(h_tts_box)
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

    def select_mp4_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            try:
                video = VideoFileClip(fname[0])
                audio = video.audio
                audio.write_audiofile("extracted_audio.wav")
                self.audio_file_name = os.path.splitext(os.path.basename(fname[0]))[0]
                if audio.duration > 4 * 60 * 1000:  # audio duration is more than 4 minutes
                    QMessageBox.warning(self, 'Warning', 'You cannot transcribe more than 4 minutes.')
                    return

                # Show a progress dialog while the audio file is being transcribed
                progress = QProgressDialog("Transcribing audio file...", None, 0, 0, self)
                progress.setGeometry(350, 350, 300, 30)
                progress.setWindowTitle(' ')
                progress.show()
                QApplication.processEvents()

                text = self.transcribe_audio("extracted_audio.wav", progress)

                progress.close()

                self.text_edit.setText(text)

                # Set the media content
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile("extracted_audio.wav")))

                # Connect the media player signals
                self.player.positionChanged.connect(self.position_changed)
                self.player.durationChanged.connect(self.duration_changed)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f"An error occurred: {e}")

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
        msg.setText(
            "Audio Transcriber v1.6.0.0\n\nThis application transcribes audio files to text. Please note that it can only transcribe audio files that are 4 minutes or shorter.")
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

                # Specify the language based on the selected radio button
                language = 'en-US' if self.english_button.isChecked() else 'it-IT'
                text = r.recognize_google(audio_data, language=language)
                # text = r.recognize_google(audio_data)

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

    # def mute_audio(self):
    #     if self.player.isMuted():
    #   self.player.setMuted(False)
    #   self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
    # else:
    #    self.player.setMuted(True)
    #    self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))

    def show_volume_dialog(self):
        self.volume_dialog = VolumeDialog(self.player)
        self.volume_dialog.exec_()

    def highlight_text(self):
        # Get the search text from the search bar
        search_text = self.search_bar.text()

        # Get the transcribed text from the text edit
        transcribed_text = self.text_edit.toPlainText()

        # Check if the search text is in the transcribed text
        if search_text in transcribed_text:
            # Highlight the search text in the transcribed text
            self.text_edit.setHtml(
                transcribed_text.replace(search_text, f'<span style="background-color: #FFFF00">{search_text}</span>'))
        else:
            # Show a message box if the search text is not found
            QMessageBox.information(self, 'Search', 'No matches found for your search.')

    def set_bold(self):
        format_text = QTextCharFormat()
        format_text.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)
        self.merge_format(format_text)

    def set_italic(self):
        format_text = QTextCharFormat()
        format_text.setFontItalic(self.italic_action.isChecked())
        self.merge_format(format_text)

    def set_underline(self):
        format_text = QTextCharFormat()
        format_text.setFontUnderline(self.underline_action.isChecked())
        self.merge_format(format_text)

    def set_font_size(self, size):
        format_text = QTextCharFormat()
        format_text.setFontPointSize(float(size))
        self.merge_format(format_text)

    def set_font(self, font):
        format_text = QTextCharFormat()
        format_text.setFont(font)
        self.merge_format(format_text)

    def merge_format(self, format_text):
        cursor = self.text_edit.textCursor()
        cursor.mergeCharFormat(format_text)
        self.text_edit.mergeCurrentCharFormat(format_text)

    # def set_language(self, index):
    #     # Set the language based on the selected index
    #     self.language = self.languages[self.language_box.itemText(index)]

    def generate_speech(self):
        try:
            # Get the text from the text edit
            text = self.text_edit.toPlainText()

            # Show a progress dialog while the speech is being generated
            progress = QProgressDialog("Generating speech...", None, 0, 0, self)
            progress.setGeometry(350, 350, 300, 30)
            progress.setWindowTitle(' ')
            progress.show()
            QApplication.processEvents()

            # Get the selected language
            selected_id = self.language_group.checkedId()
            if selected_id == 0:
                self.language = 'en'
            elif selected_id == 1:
                self.language = 'it'

            # Convert the text to speech
            speech = gTTS(text=text, lang=self.language, slow=False)

            # Save the speech audio to a file
            speech.save("speech.mp3")

            progress.close()

            # Set the media content to the generated speech audio
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile("speech.mp3")))

            # Connect the media player signals
            self.player.positionChanged.connect(self.position_changed)
            self.player.durationChanged.connect(self.duration_changed)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"An error occurred: {e}")

    def export_speech(self):
        # Open a file dialog for the user to choose the export location
        fname = QFileDialog.getSaveFileName(self, 'Save File', '/home', 'MP3 Files (*.mp3)')

        if fname[0]:
            # Show a progress dialog while the speech is being exported
            progress = QProgressDialog("Exporting speech...", None, 0, 0, self)
            progress.setGeometry(350, 350, 300, 30)
            progress.setWindowTitle(' ')
            progress.show()
            QApplication.processEvents()

            # Copy the generated speech file to the chosen location
            shutil.copyfile('speech.mp3', fname[0])

            progress.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    ex = MyApp()
    sys.exit(app.exec_())
