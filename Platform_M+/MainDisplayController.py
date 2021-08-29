#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplayController.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import str
from builtins import range
from .MackieControlComponent import *

class MainDisplayController(MackieControlComponent):
    """
        Controlling all available main displays (the display above the channel strips),
        which will be only one when only using the 'main' Mackie Control, and severals
        when using at least one Mackie Control XT, attached to the main Mackie Control.

        The Displays can be run in two modes: Channel strip and Global mode:
        - In channel strip mode 2*6 characters can be shown for each channel strip
        - In global mode, you can setup the two 56 charchter lines to whatever you want

        See 'class ChannelStripController' for descriptions of the stack_index or details
        about the different assignment modes.
    """

    def __init__(self, main_script, display):
        MackieControlComponent.__init__(self, main_script)
        self.__smpt_format = Live.Song.TimeFormat.smpte_25
        self.__last_send_time = []
        self.__left_extensions = []
        self.__right_extensions = []
        self.__displays = [display]
        self.__own_display = display
        self.__parameters = [ [] for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ u'' for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_mode = True
        self.__time_mode = False
        self.__info_mode = False
        self.__info_timer = 0
        self.__duration = 0
        self.__show_parameter_names = False
        self.__bank_channel_offset = 0
        self.__meters_enabled = False
        self.__show_return_tracks = False

    def destroy(self):
        self.enable_meters(False)
        MackieControlComponent.destroy(self)

    def refresh_state(self):
        self.__last_send_time = []

    def set_controller_extensions(self, left_extensions, right_extensions):
        """
            Called from the main script (after all scripts where initialized), to let us
            know where and how many MackieControlXT are installed.
        """
        self.__left_extensions = left_extensions
        self.__right_extensions = right_extensions
        self.__displays = []
        stack_offset = 0
        for le in left_extensions:
            self.__displays.append(le.main_display())
            le.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__displays.append(self.__own_display)
        self.__own_display.set_stack_offset(stack_offset)
        stack_offset += NUM_CHANNEL_STRIPS
        for re in right_extensions:
            self.__displays.append(re.main_display())
            re.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__parameters = [ [] for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ u'' for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.refresh_state()

    def toggle_channel_strip_mode(self):
        """ Toggle Channel strip / Global mode """
        self.__channel_strip_mode = not self.__channel_strip_mode

    def toggle_time_mode(self):
        self.__time_mode = not self.__time_mode

    def time_mode_status(self):
        if self.__time_mode:
            return True
        return False

    def toggle_info_mode(self):
        self.__info_mode = not self.__info_mode

    def show_time_mode(self):
        """ Called from the main script """
        if not self.__info_mode:
            self.toggle_channel_strip_mode()
            if not self.__channel_strip_mode:
                self.toggle_time_mode()
                for display in self.__displays:
                    self.__last_send_time = str(self.song().get_current_beats_song_time()).rjust(16)
                    """ Clear display and show Time (Position + SMPTE) """
                    time_string1 = u'Position [Bars.Beats.Subdivision.Ticks]'.ljust(40) + self.__last_send_time
                    time_string2 = u'SMPTE    [Hours:Minutes:Seconds:Frames]'.ljust(40) + str(self.song().get_current_smpte_song_time(self.__smpt_format)).rjust(16)
                    display.send_display_string(time_string1, 0, 0)
                    display.send_display_string(time_string2, 1, 0)
            else:
                self.toggle_time_mode()

    def show_assignment_status(self, status1, status2, duration):
        """
            Called from 'ChannelStripController'
            Show which assignment mode is currently active
        """
        self.__duration = duration
        self.__info_timer = 0
        if not self.__info_mode:
            self.toggle_info_mode()
            self.toggle_channel_strip_mode()
        for display in self.__displays:
            display.send_display_string(status1.center(56), 0, 0)
            display.send_display_string(status2, 1, 0)

    def enable_meters(self, enabled):
        if self.__meters_enabled != enabled:
            self.__meters_enabled = enabled
            self.refresh_state()

    def set_show_parameter_names(self, enable):
        self.__show_parameter_names = enable

    def set_channel_offset(self, channel_offset):
        self.__bank_channel_offset = channel_offset

    def parameters(self):
        return self.__parameters

    def set_parameters(self, parameters):
        if parameters:
            self.set_channel_strip_strings(None)
        for d in self.__displays:
            self.__parameters = parameters

    def channel_strip_strings(self):
        return self.__channel_strip_strings

    def set_channel_strip_strings(self, channel_strip_strings):
        if channel_strip_strings:
            self.set_parameters(None)
        self.__channel_strip_strings = channel_strip_strings

    def set_show_return_track_names(self, show_returns):
        self.__show_return_tracks = show_returns

    def refresh_state(self):
        for d in self.__displays:
            d.refresh_state()

    def on_update_display_timer(self):
        """ Called by a timer which gets called every 100 ms. """
        strip_index = 0
        for display in self.__displays:
            if self.__channel_strip_mode:
                upper_string = u''
                lower_string = u''
                track_index_range = list(range(self.__bank_channel_offset + display.stack_offset(), self.__bank_channel_offset + display.stack_offset() + NUM_CHANNEL_STRIPS))
                if self.__show_return_tracks:
                    tracks = self.song().return_tracks
                else:
                    tracks = self.song().visible_tracks
                for t in track_index_range:
                    if self.__parameters and self.__show_parameter_names:
                        if self.__parameters[strip_index]:
                            upper_string += self.__generate_6_char_string(self.__parameters[strip_index][1])
                        else:
                            upper_string += self.__generate_6_char_string(u'')
                    elif t < len(tracks):
                        upper_string += self.__generate_6_char_string(tracks[t].name)
                    else:
                        upper_string += self.__generate_6_char_string(u'')
                    upper_string += u' '
                    if self.__parameters and self.__parameters[strip_index]:
                        if self.__parameters[strip_index][0]:
                            lower_string += self.__generate_6_char_string(str(self.__parameters[strip_index][0]))
                        else:
                            lower_string += self.__generate_6_char_string(u'')
                    elif self.__channel_strip_strings and self.__channel_strip_strings[strip_index]:
                        lower_string += self.__generate_6_char_string(self.__channel_strip_strings[strip_index])
                    else:
                        lower_string += self.__generate_6_char_string(u'')
                    lower_string += u' '
                    strip_index += 1

                """ If nothing to display show 'No Sends/Returns', if no Plug-ins or I/O show 'No Entries' """
                if upper_string == u''.ljust(56):
                    lower_string = u'No Sends/Returns'.center(56)
                if lower_string == u''.ljust(56):
                    lower_string = u'No Entries'.center(56)
                display.send_display_string(upper_string, 0, 0)
                if not self.__meters_enabled:
                    display.send_display_string(lower_string, 1, 0)
            elif self.__time_mode:
                if not self.__info_mode:
                    """ Show only the values for Time mode """
                    time_string1 = str(self.song().get_current_beats_song_time()).rjust(16)
                    time_string2 = str(self.song().get_current_smpte_song_time(self.__smpt_format))
                    """ If Time has changed send new Time """
                    if self.__last_send_time != time_string1:
                        self.__last_send_time = time_string1
                        display.send_display_string(time_string1, 0, 40)
                        display.send_display_string(time_string2, 1, 43)
            else:
                """ Info mode """
                self.__info_timer += 1
                if self.__info_timer == self.__duration:
                    self.toggle_info_mode()
                    self.toggle_channel_strip_mode()

    def __generate_6_char_string(self, display_string):
        if not display_string:
            return u'      '
        if len(display_string.strip()) > 6 and display_string.endswith(u'dB') and display_string.find(u'.') != -1:
            display_string = display_string[:-2]
        if len(display_string) > 6:
            for um in [u' ',
             u'i',
             u'o',
             u'u',
             u'e',
             u'a']:
                while len(display_string) > 6 and display_string.rfind(um, 1) != -1:
                    um_pos = display_string.rfind(um, 1)
                    display_string = display_string[:um_pos] + display_string[um_pos + 1:]

        else:
            display_string = display_string.center(6)
        ret = u''
        for i in range(6):
            ret += display_string[i]

        assert len(ret) == 6
        return ret
