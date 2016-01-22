from argparse import ArgumentParser
from glob import glob
import io
import logging
from pathlib import Path

from attrdict import AttrDict
from lafayette import Lafayette
import speech_recognition as sr
from speech_recognition import AudioData

from . import stuff
from . import audio
from .config import Config
from .config import configure_parser

logger = logging.getLogger('guenther')


class Guenther:

    def __init__(self, train=False, **config):
        self.lafayette = Lafayette()
        self.recognizer = sr.Recognizer()
        self.config = Config(**config)
        self.load_samples(self.config.path.samples)
        self.load_and_apply_blacklist(self.config.path.blacklist)
        self.train = train

    def load_samples(self, sample_path):
        logger.debug('Loading samples from: %s', sample_path)
        for file_path in glob('%s/*' % sample_path):
            self.load_sample(file_path)

    def load_sample(self, file_path):
        logger.debug('Fingerprinting: %s', file_path)
        self.lafayette.fingerprint_file(file_path)

    def load_and_apply_blacklist(self, blacklist_path):
        if not Path(blacklist_path).exists():
            logger.warning("Blacklist file does not exist")
            return
        logger.info('Loading blacklist from: %s', blacklist_path)
        with open(blacklist_path, 'r') as blacklist_file:
            count = self.lafayette.rm_hashes((l.strip() for l in blacklist_file))
        logger.debug('Removed %s fingerprints', count)

    def append_to_blacklist_and_apply(self, matches, blacklist_path):
        with open(blacklist_path, 'a') as blacklist_file:
            for hash_, _, _ in matches:
                blacklist_file.write('%s\n' % hash_)
        self.load_and_apply_blacklist(blacklist_path)

    def listen_forever(self, check_intervals=None):
        check_intervals = check_intervals or self.config.listen.interval
        try:
            while True:
                match = None
                last_fingerprint_count = 0
                with audio.mic(check_intervals, self.config.audio) as (mic_iter, loop_size):
                    while not match:
                        frames = io.BytesIO()
                        for data, step in mic_iter():
                            frames.write(data)
                            stuff.draw_kit(step, loop_size, last_fingerprint_count)

                        fingerprints = [f for f in self.lafayette.fingerprint_frames(
                                frames.getvalue(), self.config.audio.sample_rate)]
                        last_fingerprint_count = len(fingerprints)
                        matches = [m for m in self.lafayette.get_matched(fingerprints)]
                        match = self.lafayette.best_match(matches)
                    print('')  # to get a newline
                    logger.info('Found match: %s', match['id'])
                    if not self.train:
                        self.handle_input(frames.getvalue(), match=match)
                    else:
                        correct = stuff.is_match_correct()
                        if correct:
                            new_sample = self.save_correct_match(frames)
                            self.lafayette.fingerprint_file(new_sample)
                        else:
                            self.append_to_blacklist_and_apply(
                                matches,
                                self.config.path.blacklist
                            )

        except KeyboardInterrupt:
            print('')  # to get a newline
            logger.info('Stopped by user')

    def save_correct_match(self, frames):
        new_sample = str(Path(self.config.path.samples) / stuff.get_unique_name())
        audio.save_frames_to_file(
            frames.getvalue(),
            new_sample,
            self.config.audio
        )
        return new_sample

    def match_callback(self):

        if not self.traingin:
            self.handle_input(frames.getvalue(), match=match)
        else:
            correct = stuff.is_match_correct()
            if correct:
                new_sample = self.save_correct_match(frames)
                self.lafayette.fingerprint_file(new_sample)
            else:
                self.append_to_blacklist_and_apply(
                    matches,
                    self.config.path.blacklist
                )


    def handle_input(self, frames, stream=None, match=None):
        caller = getattr(self.recognizer, 'recognize_%s' % self.config.stt.service_slug)
        logger.info(
            'Connection to %s with id: %s',
            self.config.stt.service_slug,
            self.config.stt.username
        )
        words = caller(
            AudioData(frames, self.config.audio.sample_rate, self.config.audio.channels),
            self.config.stt.username,
            self.config.stt.password
        )
        logger.info('Understood words: %s', words)


def main():
    parser = ArgumentParser(
        description='Yet another J.A.R.V.I.S / Jasper / Siri in python.'
    )
    parser.add_argument('--train', action='store_true')
    parser.add_argument('--no-pp', action='store_true', dest='no_pp')
    configure_parser(parser)
    args = AttrDict(vars(parser.parse_args()))
    stuff.init_logging()

    g = Guenther(
        train=args.pop('train'),
        **args
    )
    g.listen_forever()

if __name__ == "__main__":
    main()
