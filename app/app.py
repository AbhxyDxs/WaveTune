import threading
import os
from os.path import expanduser, join
import cv2
from PyQt5.QtCore import QThreadPool
from typing import Union

from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier

from .avlc import AudioPlayer, AudioPlayerEvent, AvlcMedia, ms2min
from app.ui.mainwindow import MainWindow
from .scanner import LibraryScanner
from .serializer import serialize_library
from .ui.widgets import TrackItem
import time
import math
import numpy as np

class VideoThread(threading.Thread):

    def __init__(self, parent):
        super(VideoThread, self).__init__()
        self.parent = parent
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)
        detector = HandDetector(maxHands=1)
        classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

        offset = 20
        imgSize = 500

        labels = ["play_pause", "forward", "backward", "up", "down", "no_action", "next", "previous"]

        prev = "_"
        start_init = False

        while True:
            cnt = ""
            end_time = time.time()
            success, img = cap.read()
            imgOutput = img.copy()
            hands, img = detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

                imgCropShape = imgCrop.shape

                if imgCropShape[0] > 0 and imgCropShape[1] > 0:
                    aspectRatio = h / w
                    if aspectRatio > 1:
                        k = imgSize / h
                        wCal = math.ceil(k * w)
                        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                        imgResizeShape = imgResize.shape

                        wGap = math.ceil((imgSize - wCal) / 2)

                        # imgWhite[:, wGap:wCal + wGap] = imgResize
                        imgWhite[:, wGap:wCal + wGap] = imgResize[:, :min(wCal, imgSize), :]
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                        print(prediction, index)

                    else:
                        k = imgSize / w
                        hCal = math.ceil(k * h)
                        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                        imgResizeShape = imgResize.shape
                        hGap = math.ceil((imgSize - hCal) / 2)
                        imgWhite[hGap:hGap + min(hCal, imgSize), :] = imgResize[:min(hCal, imgSize), :]
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                        print(prediction, index)


                    cv2.rectangle(imgOutput, (x - offset, y - offset - 50),
                                  (x - offset + 90, y - offset - 50 + 50), (255, 0, 255), cv2.FILLED)
                    cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255),
                                2)
                    cv2.rectangle(imgOutput, (x - offset, y - offset),
                                  (x + w + offset, y + h + offset), (255, 0, 255), 4)

                    cnt = labels[index]

                    if not (prev == cnt):
                        if not (start_init):
                            start_time = time.time()
                            start_init = True
                        elif (end_time - start_time) > 0.3:
                            if labels[index] == "play_pause":
                                self.parent.on_play_pause()
                            elif labels[index] == "next":
                                self.parent.on_next()
                            elif labels[index] == "previous":
                                self.parent.on_previous()
                            prev = cnt
                            start_init = False
                    elif labels[index] == "forward":
                        self.parent.on_fast_forward()
                    elif labels[index] == "backward":
                        self.parent.on_rewind()
                    elif labels[index] == "forward":
                        self.parent.on_fast_forward()
                    elif labels[index] == "up":
                        self.parent.increase_or_decrease_volume(True)
                    elif labels[index] == "down":
                        self.parent.increase_or_decrease_volume(False)


                    # cv2.imshow("ImageCrop", imgCrop)
                    # cv2.imshow("ImageWhite", imgWhite)


                else:
                    cnt = ""
                    prev = "_"
            else:
                cnt = ""
                prev = "_"

            # cv2.imshow("Image", imgOutput)

            if cv2.waitKey(1) & 0xff == ord('q'):
                break


class Application(MainWindow):

    def __init__(self, p):
        super(Application, self).__init__(p)
        self.threadPool = QThreadPool(self)
        self.video_thread = VideoThread(self)
        self.threadPool.setMaxThreadCount(1000)
        self.audioPlayer: Union[AudioPlayer, None] = None
        self.closingQueue.append(self.serialize)
        self.init_player()
        self.scan_library()

        # to enable hand gesture
        self.video_thread.start()

    def init_player(self):
        self.audioPlayer = AudioPlayer()
        self.audioPlayer.set_volume(100)
        self.audioPlayer.connect_event(AudioPlayerEvent.PositionChanged, self.on_pos_changed)
        self.audioPlayer.connect_event(AudioPlayerEvent.TrackEndReached, self.on_track_changed)

        self.playerPanelLayout.seekbarFrame.seekbar.seek.connect(self.audioPlayer.set_position)
        self.playerPanelLayout.playerControllerFrame.playPause.clicked.connect(self.on_play_pause)
        self.playerPanelLayout.playerControllerFrame.nextButton.clicked.connect(self.on_next)
        self.playerPanelLayout.playerControllerFrame.previousButton.clicked.connect(self.on_previous)
        self.playerPanelLayout.playerControllerFrame.fastForward.clicked.connect(self.on_fast_forward)
        self.playerPanelLayout.playerControllerFrame.rewind.clicked.connect(self.on_rewind)
        # self.playerPanelLayout.playerControllerFrame.favouriteFrame.connect(self.setFavorate)

        self.playerPanelLayout.playbackControllerFrame.volumeButton.onValueChanged.connect(self.audioPlayer.set_volume)


        self.playerPanelLayout.playbackControllerFrame.playbackModeButton.onStateChanged.connect(
            self.playback_mode_changed
        )

        self.increase_or_decrease_volume(True)

    def setFavorate(self):
        print(self.audioPlayer.mediaList)
        pass


    def increase_or_decrease_volume(self,mode):
        if mode:
            self.playerPanelLayout.playbackControllerFrame.volumeButton.setVolume(True)
        else:
            self.playerPanelLayout.playbackControllerFrame.volumeButton.setVolume(False)


    def on_play_pause(self):
        self.audioPlayer.pause()
        if self.audioPlayer.isPaused:
            self.playerPanelLayout.playerControllerFrame.playPause.changeIcon("res/icons/play.svg")
        else:
            self.playerPanelLayout.playerControllerFrame.playPause.changeIcon("res/icons/pause.svg")

    def on_next(self):
        self.audioPlayer.next()
        self.on_track_changed()

    def on_previous(self):
        self.audioPlayer.previous()
        self.on_track_changed()

    def on_fast_forward(self):
        self.audioPlayer.set_position(self.audioPlayer.get_position() + 3000)

    def on_rewind(self):
        self.audioPlayer.set_position(self.audioPlayer.get_position() - 3000)

    def playback_mode_changed(self, mode):
        self.audioPlayer.set_playback_mode(mode)

    def library_add_track(self, media: AvlcMedia):
        track = TrackItem(self, media)
        track.onPlay.connect(self.quick_play)
        self.libraryPage.trackContainer.addItem(track)

    def scan_library(self):
        self.libraryPage.closeEmptyPrompt()
        current_directory = os.getcwd()
        #For testing Music files on the project directory Music Folder!
        music_folder = os.path.join(current_directory, "Music")
        libraryScanner = LibraryScanner(self.audioPlayer, music_folder)
        #For the Music files on the Music folder of the Current User Eg:C:\Users\Abhay\Music!
        # libraryScanner = LibraryScanner(self.audioPlayer, join(expanduser("~"), "Music"))
        libraryScanner.signal.scanned.connect(self.library_add_track)
        self.threadPool.start(libraryScanner)

    def on_pos_changed(self):
        if not self.isUpdating:
            self.playerPanelLayout.seekbarFrame.seekbar.updatePosition(self.audioPlayer.get_position())
            self.playerPanelLayout.timeFrame.time.setText(
                f"{ms2min(self.audioPlayer.get_position())}/{ms2min(self.audioPlayer.get_length())}"
            )

    def on_track_changed(self):
        media: AvlcMedia = self.audioPlayer.mediaList[self.audioPlayer.currentIndex]
        self.update_player_info(media.art, media.title, media.artist, media.duration)

    # double-click on a track item to quick play
    def quick_play(self, media: AvlcMedia):
        self.audioPlayer.play(self.audioPlayer.mediaList.index(media))
        self.update_player_info(media.art, media.title, media.artist, media.duration)
        self.playerPanelLayout.playerControllerFrame.playPause.changeIcon("res/icons/pause.svg")

    def update_player_info(self, cover, title, artist, duration):
        self.playerPanelLayout.playerInfoFrame.setCoverArt(cover)
        self.playerPanelLayout.playerInfoFrame.setTitle(title)
        self.playerPanelLayout.playerInfoFrame.setArtist(artist)
        self.playerPanelLayout.seekbarFrame.seekbar.setRange(0, duration)

    def serialize(self):
        serialize_library(self.audioPlayer.mediaList, "conf/library.json")

