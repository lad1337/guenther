from contextlib import contextmanager
import logging
import wave

logger = logging.getLogger('guenther.audio')

import pyaudio

@contextmanager
def mic(duration, config):
    logger.debug('Init Mic with: %s', config)
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(
            format=config.format,
            channels=config.channels,
            rate=config.sample_rate,
            input=True,
            frames_per_buffer=config.chunk_size,
            start=False
        )
        loop_size = get_loop_size(config, duration)

        def iterator():
            stream.start_stream()
            for step in range(0, loop_size):
                yield stream.read(config.chunk_size), step
        yield iterator, loop_size
    except OSError:
        logger.exception('Error during record')
        raise
    finally:
        try:
            stream.stop_stream()
        except OSError:
            logger.exception('Error during stopping stream')
        try:
            stream.close()
        except OSError:
            logger.exception('Error during stream close')
        audio.terminate()


def get_loop_size(config, duration):
    return int(config.sample_rate / config.chunk_size * duration)


def save_frames_to_file(frames, file_location, config):
    logger.debug('Saving new sample at: %s', file_location)
    audio = pyaudio.PyAudio()

    waveFile = wave.open(file_location, 'wb')
    waveFile.setnchannels(config.channels)
    waveFile.setsampwidth(audio.get_sample_size(config.format))
    waveFile.setframerate(config.sample_rate)
    waveFile.writeframes(frames)
    waveFile.close()
