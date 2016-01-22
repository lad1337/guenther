from io import BytesIO
import logging
from queue import Queue
from .. import audio
from .. import stuff

from pyspin.spin import make_spin, Default

logger = logging.getLogger('guenther.navi')


class Navi:

    def __init__(self, config, lafayette):
        self.config = config
        self.lafayette = lafayette
        #self.q = Queue(audio.get_loop_size(config, buffer_size_sec))

        self.listen = False


    def listen_forever(self, check_intervals, match_callback):
        while True:
            match = None
            last_fingerprint_count = 0
            with audio.mic(check_intervals, self.config.audio) as (mic_iter, loop_size):
                while not match:
                    frames = BytesIO()
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
                match_callback(match, fingerprints, frames)
