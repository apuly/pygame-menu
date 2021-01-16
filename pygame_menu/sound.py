"""
pygame-menu
https://github.com/ppizarror/pygame-menu

SOUND
Sound class.

License:
-------------------------------------------------------------------------------
The MIT License (MIT)
Copyright 2017-2021 Pablo Pizarro R. @ppizarror

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-------------------------------------------------------------------------------
"""

import os.path as path
import time
import warnings

from pygame import error as pygame_error
from pygame import mixer
from pygame import vernum as pygame_version

from pygame_menu.custom_types import NumberType, List, Dict, Any, Optional

try:  # pygame<2.0.0 compatibility
    from pygame import AUDIO_ALLOW_CHANNELS_CHANGE
    from pygame import AUDIO_ALLOW_FREQUENCY_CHANGE
except ImportError:
    AUDIO_ALLOW_CHANNELS_CHANGE = False
    AUDIO_ALLOW_FREQUENCY_CHANGE = False

# Sound types
SOUND_TYPE_CLICK_MOUSE = '__pygame_menu_sound_click_mouse__'
SOUND_TYPE_CLOSE_MENU = '__pygame_menu_sound_close_menu__'
SOUND_TYPE_ERROR = '__pygame_menu_sound_error__'
SOUND_TYPE_EVENT = '__pygame_menu_sound_event__'
SOUND_TYPE_EVENT_ERROR = '__pygame_menu_sound_event_error__'
SOUND_TYPE_KEY_ADDITION = '__pygame_menu_sound_key_addition__'
SOUND_TYPE_KEY_DELETION = '__pygame_menu_sound_key_deletion__'
SOUND_TYPE_OPEN_MENU = '__pygame_menu_sound_open_menu__'
SOUND_TYPE_WIDGET_SELECTION = '__pygame_menu_sound_widget_selection__'

# Sound example paths
__sounds_path__ = path.join(path.dirname(path.abspath(__file__)), 'resources', 'sounds', '{0}')

SOUND_EXAMPLE_CLICK_MOUSE = __sounds_path__.format('click_mouse.ogg')
SOUND_EXAMPLE_CLOSE_MENU = __sounds_path__.format('close_menu.ogg')
SOUND_EXAMPLE_ERROR = __sounds_path__.format('error.ogg')
SOUND_EXAMPLE_EVENT = __sounds_path__.format('event.ogg')
SOUND_EXAMPLE_EVENT_ERROR = __sounds_path__.format('event_error.ogg')
SOUND_EXAMPLE_KEY_ADD = __sounds_path__.format('key_add.ogg')
SOUND_EXAMPLE_KEY_DELETE = __sounds_path__.format('key_delete.ogg')
SOUND_EXAMPLE_OPEN_MENU = __sounds_path__.format('open_menu.ogg')
SOUND_EXAMPLE_WIDGET_SELECTION = __sounds_path__.format('widget_selection.ogg')

SOUND_EXAMPLES = (SOUND_EXAMPLE_CLICK_MOUSE, SOUND_EXAMPLE_CLOSE_MENU, SOUND_EXAMPLE_ERROR,
                  SOUND_EXAMPLE_EVENT, SOUND_EXAMPLE_EVENT_ERROR, SOUND_EXAMPLE_KEY_ADD,
                  SOUND_EXAMPLE_KEY_DELETE, SOUND_EXAMPLE_OPEN_MENU, SOUND_EXAMPLE_WIDGET_SELECTION)

# Stores global reference that marks sounds as initialized
SOUND_INITIALIZED = [False]


class Sound(object):
    """
    Sound engine class.
    
    :param uniquechannel: Force the channel to be unique, this is set at the object creation moment
    :param frequency: Frequency of sounds
    :param size: Size of sample
    :param channels: Number of channels
    :param buffer: Buffer size
    :param devicename: Device name
    :param allowedchanges: Convert the samples at runtime, only in pygame>=2.0.0
    :param force_init: Force mixer init with new parameters
    """
    _channel: Optional['mixer.Channel']
    _last_play: str
    _last_time: float
    _sound: Dict[str, Dict[str, Any]]
    _type_sounds: List[str]
    _uniquechannel: bool
    _verbose: bool

    # noinspection PyShadowingBuiltins
    def __init__(self,
                 uniquechannel: bool = True,
                 frequency: int = 22050,
                 size: int = -16,
                 channels: int = 2,
                 buffer: int = 4096,
                 devicename: str = '',
                 allowedchanges: int = AUDIO_ALLOW_CHANNELS_CHANGE | AUDIO_ALLOW_FREQUENCY_CHANGE,
                 force_init: bool = False
                 ) -> None:
        assert isinstance(uniquechannel, bool)
        assert isinstance(frequency, int)
        assert isinstance(size, int)
        assert isinstance(channels, int)
        assert isinstance(buffer, int)
        assert isinstance(devicename, str)
        assert isinstance(allowedchanges, int)
        assert isinstance(force_init, bool)
        assert frequency > 0, 'frequency must be greater than zero'
        assert channels > 0, 'channels must be greater than zero'
        assert buffer > 0, 'buffer size must be greater than zero'

        # Initialize sounds if not initialized
        if (mixer.get_init() is None and not SOUND_INITIALIZED[0]) or force_init:

            # Set sound as initialized globally
            SOUND_INITIALIZED[0] = True

            # Check pygame version
            version_major, _, version_minor = pygame_version

            # noinspection PyBroadException
            try:
                # <= 1.9.4
                if version_major == 1 and version_minor <= 4:
                    mixer.init(frequency=frequency,
                               size=size,
                               channels=channels,
                               buffer=buffer)

                # <2.0.0 & >= 1.9.5
                elif version_major == 1 and version_minor > 4:  # lgtm [py/redundant-comparison]
                    mixer.init(frequency=frequency,
                               size=size,
                               channels=channels,
                               buffer=buffer,
                               devicename=devicename)

                # >= 2.0.0
                elif version_major > 1:
                    mixer.init(frequency=frequency,
                               size=size,
                               channels=channels,
                               buffer=buffer,
                               devicename=devicename,
                               allowedchanges=allowedchanges)

            except Exception as e:
                print('sound error: ' + str(e))
            except pygame_error as e:
                print('sound engine could not be initialized, pygame error: ' + str(e))

        # Channel where a sound is played
        self._channel = None
        self._uniquechannel = uniquechannel

        # Sound dict
        self._type_sounds = [
            SOUND_TYPE_CLICK_MOUSE,
            SOUND_TYPE_CLOSE_MENU,
            SOUND_TYPE_ERROR,
            SOUND_TYPE_EVENT,
            SOUND_TYPE_EVENT_ERROR,
            SOUND_TYPE_KEY_ADDITION,
            SOUND_TYPE_KEY_DELETION,
            SOUND_TYPE_OPEN_MENU,
            SOUND_TYPE_WIDGET_SELECTION
        ]
        self._sound = {}
        for sound in self._type_sounds:
            self._sound[sound] = {}

        # Last played song
        self._last_play = ''
        self._last_time = 0

    def get_channel(self) -> 'mixer.Channel':
        """
        Return the channel of the sound engine.

        :return: Sound engine channel
        """
        # noinspection PyArgumentList
        channel = mixer.find_channel()  # force only available on pygame v2
        if self._uniquechannel:  # If the channel is unique
            if self._channel is None:  # If the channel has not been set
                self._channel = channel
        else:
            self._channel = channel  # Store the available channel
        return self._channel

    def set_sound(self, sound_type: str, sound_file: Optional[str], volume: float = 0.5,
                  loops: int = 0, maxtime: NumberType = 0, fade_ms: NumberType = 0) -> bool:
        """
        Link a sound file to a sound type.

        :param sound_type: Sound type
        :param sound_file: Sound file
        :param volume: Volume of the sound, from ``0.0`` to ``1.0``
        :param loops: Loops of the sound
        :param maxtime: Max playing time of the sound
        :param fade_ms: Fading ms
        :return: The status of the sound load, ``True`` if the sound was loaded
        """
        assert isinstance(sound_type, str)
        assert isinstance(sound_file, (str, type(None)))
        assert isinstance(volume, float)
        assert isinstance(loops, int)
        assert isinstance(maxtime, (int, float))
        assert isinstance(fade_ms, (int, float))
        assert loops >= 0, 'loops count must be equal or greater than zero'
        assert maxtime >= 0, 'maxtime must be equal or greater than zero'
        assert fade_ms >= 0, 'fade_ms must be equal or greater than zero'
        assert 1 >= volume >= 0, 'volume must be between 0 and 1'

        # Check sound type is correct
        if sound_type not in self._type_sounds:
            raise ValueError('sound type not valid, check the manual')

        # If file is none disable the sound
        if sound_file is None:
            self._sound[sound_type] = {}
            return False

        # Check the file exists
        if not path.isfile(sound_file):
            raise IOError('sound file "{0}" does not exist'.format(sound_file))

        # Load the sound
        try:
            # noinspection PyTypeChecker
            sound_data = mixer.Sound(file=sound_file)
        except pygame_error:
            warnings.warn('the sound format is not valid, the sound has been disabled')
            self._sound[sound_type] = {}
            return False

        # Configure the sound
        sound_data.set_volume(volume)

        # Store the sound
        self._sound[sound_type] = {
            'file': sound_data,
            'path': sound_file,
            'type': sound_type,
            'length': sound_data.get_length(),
            'volume': volume,
            'loops': loops,
            'maxtime': maxtime,
            'fade_ms': fade_ms
        }
        return True

    def load_example_sounds(self, volume: float = 0.5) -> None:
        """
        Load the example sounds provided by the package.

        :param volume: Volume of the sound, ``(0-1)``
        :return: None
        """
        assert isinstance(volume, float)
        for sound in range(len(self._type_sounds)):
            self.set_sound(self._type_sounds[sound], SOUND_EXAMPLES[sound], volume=volume)

    def _play_sound(self, sound: Optional[Dict[str, Any]]) -> bool:
        """
        Play a sound.

        :param sound: Sound to be played
        :return: ``True`` if the sound was played
        """
        if not sound:
            return False

        # Find an available channel
        channel = self.get_channel()  # This will set the channel if it's None
        if channel is None:  # The sound can't be played because all channels are busy
            return False

        # Play the sound
        soundtime = time.time()

        # If the previous sound is the same and has not ended (max 20% overlap)
        if sound['type'] != self._last_play or \
                soundtime - self._last_time >= 0.2 * sound['length'] or self._uniquechannel:
            try:
                if self._uniquechannel:  # Stop the current channel if it's unique
                    channel.stop()
                channel.play(sound['file'],
                             loops=sound['loops'],
                             maxtime=sound['maxtime'],
                             fade_ms=sound['fade_ms']
                             )
            except pygame_error:  # Ignore errors
                pass

        # Store last execution
        self._last_play = sound['type']
        self._last_time = soundtime
        return True

    def play_click_mouse(self) -> None:
        """
        Play click mouse sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_CLICK_MOUSE])

    def play_error(self) -> None:
        """
        Play error sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_ERROR])

    def play_event(self) -> None:
        """
        Play event sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_EVENT])

    def play_event_error(self) -> None:
        """
        Play event error sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_EVENT_ERROR])

    def play_key_add(self) -> None:
        """
        Play key addition sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_KEY_ADDITION])

    def play_key_del(self) -> None:
        """
        Play key deletion sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_KEY_DELETION])

    def play_open_menu(self) -> None:
        """
        Play open Menu sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_OPEN_MENU])

    def play_close_menu(self) -> None:
        """
        Play close Menu sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_CLOSE_MENU])

    def play_widget_selection(self) -> None:
        """
        Play widget selection sound.

        :return: None
        """
        self._play_sound(self._sound[SOUND_TYPE_WIDGET_SELECTION])

    def stop(self) -> None:
        """
        Stop the the channel.

        :return: None
        """
        channel = self.get_channel()
        if channel is None:  # The sound can't be played because all channels are busy
            return
        try:
            channel.stop()
        except pygame_error:
            pass

    def pause(self) -> None:
        """
        Pause the channel.

        :return: None
        """
        channel = self.get_channel()
        if channel is None:  # The sound can't be played because all channels are busy
            return
        try:
            channel.pause()
        except pygame_error:
            pass

    def unpause(self) -> None:
        """
        Unpause channel.

        :return: None
        """
        channel = self.get_channel()
        if channel is None:  # The sound can't be played because all channels are busy
            return
        try:
            channel.unpause()
        except pygame_error:
            pass

    def get_channel_info(self) -> Dict[str, Any]:
        """
        Return the channel information.

        :return: Information dict e.g.: ``{'busy': 0, 'endevent': 0, 'queue': None, 'sound': None, 'volume': 1.0}``
        """
        channel = self.get_channel()
        data = {}
        if channel is None:  # The sound can't be played because all channels are busy
            return data
        data['busy'] = channel.get_busy()
        data['endevent'] = channel.get_endevent()
        data['queue'] = channel.get_queue()
        data['sound'] = channel.get_sound()
        data['volume'] = channel.get_volume()
        return data


# Workspace cleaning
del AUDIO_ALLOW_CHANNELS_CHANGE, AUDIO_ALLOW_FREQUENCY_CHANGE
