from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QPushButton, QStyle, QHBoxLayout, QLabel, QDialog


class VolumeDialog(QDialog):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Volume Control')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))

        # Create a horizontal volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.player.volume())
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Create a mute button
        self.mute_btn = QPushButton()
        self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_btn.setCheckable(False)
        self.mute_btn.clicked.connect(self.mute_audio)

        # Create a label to display the volume percentage
        self.volume_label = QLabel()
        self.volume_label.setText(f"Volume: {self.player.volume()}%")

        # Add the controls to a horizontal layout
        controls = QHBoxLayout()
        controls.addWidget(self.mute_btn)
        controls.addWidget(self.volume_slider)
        controls.addWidget(self.volume_label)

        self.setLayout(controls)

    def set_volume(self, volume):
        self.player.setVolume(volume)
        self.volume_label.setText(f"Volume: {volume}%")

    def mute_audio(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.volume_label.setText(f"Volume: {self.player.volume()}%")
        else:
            self.player.setMuted(True)
            self.mute_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.volume_label.setText("Volume: 0%")
