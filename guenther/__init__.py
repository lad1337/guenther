from argparse import ArgumentParser
from glob import glob
import io
import logging

from lafayette import Lafayette
import pyaudio
import numpy as np

import speech_recognition as sr
from speech_recognition import AudioData

from . import stuff
from .config import Config

class Guenther:

    def __init__(self, **kwargs):
        self.logger = logging.getLogger('guenther')
        self.lafayette = Lafayette()
        self.recognizer = sr.Recognizer()
        self.config = Config(**kwargs)
        self.load_samples(self.config.path.samples)

    def load_samples(self, sample_path):
        self.logger.debug('Loading samples from: %s', sample_path)
        for file_path in glob('%s/*' % sample_path):
            self.load_sample(file_path)

    def load_sample(self, file_path):
        self.logger.debug('Fingerprinting: %s', file_path)
        self.lafayette.fingerprint_file(file_path)

    def listen_forever(self, check_intervals=None):
        check_intervals = check_intervals or self.config.listen.interval
        audio = pyaudio.PyAudio()

        def open_stream():
            return audio.open(
                format=self.config.audio.format,
                channels=self.config.audio.channels,
                rate=self.config.audio.sample_rate,
                input=True,
                frames_per_buffer=self.config.audio.chunk_size
            )
        stream = open_stream()
        loop_size = int(
            self.config.audio.sample_rate / self.config.audio.chunk_size * check_intervals)
        self.logger.info('Starting to LISTEN!')
        try:
            raw_frames = io.BytesIO()
            while True:
                raw_frames.seek(0, 0)
                for i in range(0, loop_size):
                    data = stream.read(self.config.audio.chunk_size)
                    raw_frames.write(data)
                    stuff.draw_kit(i, loop_size)
                match = self.lafayette.match_frames(
                        raw_frames.getvalue(),
                        frame_rate=self.config.audio.sample_rate)
                if match:
                    stream.stop_stream()
                    stream.close()
                    print('')  # to get a newline
                    self.logger.info('Found match: %s', match['id'])
                    self.handle_input(
                        raw_frames.getvalue(),
                        match=match
                    )
                    stream = open_stream()
        except KeyboardInterrupt:
            print('')  # to get a newline
            self.logger.info('Stopped by user')
        finally:
            raw_frames.close()
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def handle_input(self, frames, stream=None, match=None):
        words = self.recognizer.recognize_ibm(
            AudioData(frames, self.config.audio.sample_rate, self.config.audio.channels),
            '28a8107f-63d4-4042-a935-07d74c42f59c',
            '7eAEJYKb83fH'
        )
        self.logger.info('Understood words: %s', words)


def main():
    parser = ArgumentParser()
    parser.add_argument('--samples')
    parser.add_argument('--listen-interval', dest='listen_interval')
    args = parser.parse_args()

    stuff.init_logging()

    g = Guenther(
        sample_folder=args.samples,
        listen_interval=args.listen_interval
    )
    g.listen_forever()

if __name__ == "__main__":
    main()
