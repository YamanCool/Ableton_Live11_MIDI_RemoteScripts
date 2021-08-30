# Ableton Live 11 MIDI RemoteScripts

### Corrected MackieControl Scripts:

#### Changes in 'ChannelStripController.py'

* Missing def 'handle_control_switch_ids' added
* Renamed 'any_slider_is_touched' in 'any_fader_is_touched'

#### Changes in 'const.py'

* List 'channel_strip_control_switch_ids' corrected

#### Changes in 'MackieControl.py'

* Def 'receive_midi' corrected

#### Changes in 'MainDisplayController.py'

* Display test commented out

#### Changes in 'SoftwareController.py'

* Missing def 'update_follow_song_button_led' added

#### Changes in 'Transport.py'

* Def 'handle_user_foot_switch_ids' added
* Cursor LEDs switching added
* Zoom Button LEDs behaviour corrected
* Def 'update_follow_song_button_led' deleted
* Def 'toggle_follow' deleted
