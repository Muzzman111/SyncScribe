# Synchronized Lyrics: a Quod Libet plugin for showing synchronized lyrics.
# Copyright (C) 2015 elfalem
#            2016-22 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
import functools
import os
import re
from os.path import splitext
from typing import List, Tuple, Optional

from gi.repository import Gtk, Gdk, GLib

from quodlibet import _, util
from quodlibet import app
from quodlibet import qltk
from quodlibet.formats import AudioFile
from quodlibet.plugins import PluginConfigMixin
from quodlibet.plugins.events import EventPlugin
from quodlibet.qltk import Icons
from quodlibet.util.dprint import print_d


class SynchronizedLyrics(EventPlugin, PluginConfigMixin):
    PLUGIN_ID = 'SynchronizedLyricsDualLanguage'
    PLUGIN_NAME = _('Synchronized Lyrics Dual Language')
    PLUGIN_DESC = _('Shows synchronized lyrics from an .lrc file '
                    'with the same name as the track (or similar), '
                    'plus an additional OG version if available.')
    PLUGIN_ICON = Icons.FORMAT_JUSTIFY_FILL

    SYNC_PERIOD = 10000

    DEFAULT_BGCOLOR = '#343428282C2C'
    DEFAULT_TXTCOLOR = '#FFFFFFFFFFFF'
    DEFAULT_FONTSIZE = 25

    CFG_BGCOLOR_KEY = "backgroundColor"
    CFG_TXTCOLOR_KEY = "textColor"
    CFG_FONTSIZE_KEY = "fontSize"

    # Note the trimming of whitespace, seems "most correct" behaviour
    LINE_REGEX = re.compile(r"\s*\[([0-9]+:[0-9.]*)]\s*(.+)\s*")

    def __init__(self) -> None:
        super().__init__()
        # For original lyrics
        self._lines: List[Tuple[int, str]] = []
        self._timers: List[Tuple[int, int]] = []
        # For OG lyrics
        self._lines_og: List[Tuple[int, str]] = []
        self._timers_og: List[Tuple[int, int]] = []
        self._start_clearing_from = 0
        self._start_clearing_from_og = 0

        # Two text views for two languages
        self.textview_original = None
        self.textview_og = None
        self.scrolled_window_original = None
        self.scrolled_window_og = None

    @classmethod
    def PluginPreferences(cls, window):
        vb = Gtk.VBox(spacing=6)
        vb.set_border_width(6)

        t = Gtk.Table(n_rows=5, n_columns=2, homogeneous=True)
        t.set_col_spacings(6)
        t.set_row_spacings(3)

        clr_section = Gtk.Label()
        clr_section.set_markup(util.bold(_("Colors")))
        t.attach(clr_section, 0, 2, 0, 1)

        l = Gtk.Label(label=_("Text:"))
        l.set_alignment(xalign=1.0, yalign=0.5)
        t.attach(l, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL)

        c = Gdk.RGBA()
        c.parse(cls._get_text_color())
        b = Gtk.ColorButton(rgba=c)
        t.attach(b, 1, 2, 1, 2)
        b.connect('color-set', cls._set_text_color)

        l = Gtk.Label(label=_("Background:"))
        l.set_alignment(xalign=1.0, yalign=0.5)
        t.attach(l, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL)

        c = Gdk.RGBA()
        c.parse(cls._get_background_color())
        b = Gtk.ColorButton(rgba=c)
        t.attach(b, 1, 2, 2, 3)
        b.connect('color-set', cls._set_background_color)

        font_section = Gtk.Label()
        font_section.set_markup(util.bold(_("Font")))
        t.attach(font_section, 0, 2, 3, 4)

        l = Gtk.Label(label=_("Size (px):"))
        l.set_alignment(xalign=1.0, yalign=0.5)
        t.attach(l, 0, 1, 4, 5, xoptions=Gtk.AttachOptions.FILL)

        a = Gtk.Adjustment.new(cls._get_font_size(), 10, 72, 2, 3, 0)
        s = Gtk.SpinButton(adjustment=a)
        s.set_numeric(True)
        s.set_text(str(cls._get_font_size()))
        t.attach(s, 1, 2, 4, 5)
        s.connect('value-changed', cls._set_font_size)

        vb.pack_start(t, False, False, 0)
        return vb

    @classmethod
    def _get_text_color(cls):
        v = cls.config_get(cls.CFG_TXTCOLOR_KEY, cls.DEFAULT_TXTCOLOR)
        return v[:3] + v[5:7] + v[9:11]

    @classmethod
    def _get_background_color(cls):
        v = cls.config_get(cls.CFG_BGCOLOR_KEY, cls.DEFAULT_BGCOLOR)
        return v[:3] + v[5:7] + v[9:11]

    @classmethod
    def _get_font_size(cls):
        return int(cls.config_get(cls.CFG_FONTSIZE_KEY, cls.DEFAULT_FONTSIZE))

    def _set_text_color(self, button):
        self.config_set(self.CFG_TXTCOLOR_KEY, button.get_color().to_string())
        self._style_lyrics_windows()

    def _set_background_color(self, button):
        self.config_set(self.CFG_BGCOLOR_KEY, button.get_color().to_string())
        self._style_lyrics_windows()

    def _set_font_size(self, button):
        self.config_set(self.CFG_FONTSIZE_KEY, button.get_value_as_int())
        self._style_lyrics_windows()

    def enabled(self):
        # Create a vertical container for both sets of lyrics.
        container = Gtk.VBox(spacing=6)

        # Original lyrics
        self.scrolled_window_original = Gtk.ScrolledWindow()
        self.scrolled_window_original.set_policy(Gtk.PolicyType.AUTOMATIC,
                                                   Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window_original.get_vadjustment().set_value(0)
        self.textview_original = Gtk.TextView()
        self.textview_original.set_editable(False)
        self.textview_original.set_cursor_visible(False)
        self.textview_original.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview_original.set_justification(Gtk.Justification.CENTER)
        self.scrolled_window_original.add_with_viewport(self.textview_original)
        container.pack_start(self.scrolled_window_original, True, True, 6)

        # OG lyrics (displayed right under original)
        self.scrolled_window_og = Gtk.ScrolledWindow()
        self.scrolled_window_og.set_policy(Gtk.PolicyType.AUTOMATIC,
                                             Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window_og.get_vadjustment().set_value(0)
        self.textview_og = Gtk.TextView()
        self.textview_og.set_editable(False)
        self.textview_og.set_cursor_visible(False)
        self.textview_og.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview_og.set_justification(Gtk.Justification.CENTER)
        self.scrolled_window_og.add_with_viewport(self.textview_og)
        container.pack_start(self.scrolled_window_og, True, True, 6)

        container.show_all()
        app.window.get_child().pack_start(container, False, True, 0)
        app.window.get_child().reorder_child(container, 2)

        self._style_lyrics_windows()

        self.scrolled_window_original.show()
        self.scrolled_window_og.show()

        self._sync_timer = GLib.timeout_add(self.SYNC_PERIOD, self._sync)
        self._build_data_all(app.player.song)
        self._timer_control()
        self._timer_control_og()

    def disabled(self):
        self._clear_timers()
        self._clear_timers_og()
        GLib.source_remove(self._sync_timer)
        self.textview_original.destroy()
        self.textview_original = None
        self.scrolled_window_original.destroy()
        self.scrolled_window_original = None
        self.textview_og.destroy()
        self.textview_og = None
        self.scrolled_window_og.destroy()
        self.scrolled_window_og = None

    def _style_lyrics_windows(self):
        # Apply style to both textviews.
        if self.scrolled_window_original:
            self.scrolled_window_original.set_size_request(-1, int(1.5 * self._get_font_size()))
            qltk.add_css(self.textview_original, f"""
                * {{
                    background-color: {self._get_background_color()};
                    color: {self._get_text_color()};
                    font-size: {self._get_font_size()}px;
                    padding: 0.25rem;
                    border-radius: 6px;
                }}
            """)
        if self.scrolled_window_og:
            self.scrolled_window_og.set_size_request(-1, int(1.5 * self._get_font_size()))
            qltk.add_css(self.textview_og, f"""
                * {{
                    background-color: {self._get_background_color()};
                    color: {self._get_text_color()};
                    font-size: {self._get_font_size()}px;
                    padding: 0.25rem;
                    border-radius: 6px;
                }}
            """)

    def _cur_position(self):
        return app.player.get_position()

    def _build_data_all(self, song: Optional[AudioFile]) -> None:
        # Build data for both original and OG lyrics.
        self._lines = self._build_data_original(song)
        self._lines_og = self._build_data_og(song)

    def _build_data_original(self, song: Optional[AudioFile]) -> List[Tuple[int, str]]:
        if self.textview_original:
            self.textview_original.get_buffer().set_text("")
        if song:
            track_name = splitext(song("~basename") or "")[0]
            dir_ = song("~dirname")
            print_d(f"Looking for original .lrc files in {dir_}")
            # Try a set of candidate filenames for the original lyrics.
            candidates = [f"{s}.lrc" for s in {
                track_name,
                track_name.lower(),
                track_name.upper(),
                song("~artist~title"),
                song("~artist~tracknumber~title"),
                song("~tracknumber~title")
            }]
            for filename in candidates:
                print_d(f"Looking for {filename!r}")
                try:
                    with open(os.path.join(dir_, filename), 'r', encoding="utf-8") as f:
                        print_d(f"Found original lyrics file: {filename}")
                        contents = f.read()
                except FileNotFoundError:
                    continue
                return self._parse_lrc(contents)
            print_d(f"No original lyrics found for {track_name!r}")
        return []

    def _build_data_og(self, song: Optional[AudioFile]) -> List[Tuple[int, str]]:
        if self.textview_og:
            self.textview_og.get_buffer().set_text("")
        if song:
            track_name = splitext(song("~basename") or "")[0]
            dir_ = song("~dirname")
            print_d(f"Looking for OG .lrc file in {dir_}")
            # The OG file is expected to be named as "name OG.lrc"
            filename = f"{track_name} OG.lrc"
            print_d(f"Looking for {filename!r}")
            try:
                with open(os.path.join(dir_, filename), 'r', encoding="utf-8") as f:
                    print_d(f"Found OG lyrics file: {filename}")
                    contents = f.read()
            except FileNotFoundError:
                print_d(f"No OG lyrics found for {track_name!r}")
                return []
            return self._parse_lrc(contents)
        return []

    def _parse_lrc(self, contents: str) -> List[Tuple[int, str]]:
        data = []
        for line in contents.splitlines():
            match = self.LINE_REGEX.match(line)
            if not match:
                continue
            timing, text = match.groups()
            minutes, seconds = (float(p) for p in timing.split(":", 1))
            timestamp = int(1000 * (minutes * 60 + seconds))
            data.append((timestamp, text))
        return sorted(data)

    def _set_timers(self):
        # For original lyrics.
        if not self._timers:
            print_d("Setting timers for original lyrics")
            cur_time = self._cur_position()
            cur_idx = self._greater(self._lines, cur_time)
            if cur_idx != -1:
                while (cur_idx < len(self._lines) and
                       self._lines[cur_idx][0] < cur_time + self.SYNC_PERIOD):
                    timestamp = self._lines[cur_idx][0]
                    line = self._lines[cur_idx][1]
                    tid = GLib.timeout_add(timestamp - cur_time, self._show_original, line)
                    self._timers.append((timestamp, tid))
                    cur_idx += 1

    def _set_timers_og(self):
        # For OG lyrics.
        if not self._timers_og:
            print_d("Setting timers for OG lyrics")
            cur_time = self._cur_position()
            cur_idx = self._greater(self._lines_og, cur_time)
            if cur_idx != -1:
                while (cur_idx < len(self._lines_og) and
                       self._lines_og[cur_idx][0] < cur_time + self.SYNC_PERIOD):
                    timestamp = self._lines_og[cur_idx][0]
                    line = self._lines_og[cur_idx][1]
                    tid = GLib.timeout_add(timestamp - cur_time, self._show_og, line)
                    self._timers_og.append((timestamp, tid))
                    cur_idx += 1

    def _sync(self):
        if not app.player.paused:
            self._clear_timers()
            self._clear_timers_og()
            self._set_timers()
            self._set_timers_og()
        return True

    def _timer_control(self):
        if app.player.paused:
            self._clear_timers()
        else:
            self._set_timers()
        return False

    def _timer_control_og(self):
        if app.player.paused:
            self._clear_timers_og()
        else:
            self._set_timers_og()
        return False

    def _clear_timers(self):
        for ts, tid in self._timers[self._start_clearing_from:]:
            GLib.source_remove(tid)
        self._timers = []
        self._start_clearing_from = 0

    def _clear_timers_og(self):
        for ts, tid in self._timers_og[self._start_clearing_from_og:]:
            GLib.source_remove(tid)
        self._timers_og = []
        self._start_clearing_from_og = 0

    def _show_original(self, line) -> bool:
        if self.textview_original:
            self.textview_original.get_buffer().set_text(line)
        self._start_clearing_from += 1
        print_d(f"Original: ♪ {line.strip()} ♪")
        return False

    def _show_og(self, line) -> bool:
        if self.textview_og:
            self.textview_og.get_buffer().set_text(line)
        self._start_clearing_from_og += 1
        print_d(f"OG: ♪ {line.strip()} ♪")
        return False

    def plugin_on_song_started(self, song: AudioFile) -> None:
        if song:
            print_d(f"Preparing for {song.key}")
        self._clear_timers()
        self._clear_timers_og()
        self._build_data_all(song)
        # delay so that current position is for current track, not previous one
        GLib.timeout_add(5, self._timer_control)
        GLib.timeout_add(5, self._timer_control_og)

    def plugin_on_song_ended(self, song, stopped):
        self._clear_timers()
        self._clear_timers_og()

    def plugin_on_paused(self):
        self._timer_control()
        self._timer_control_og()

    def plugin_on_unpaused(self):
        self._timer_control()
        self._timer_control_og()

    def plugin_on_seek(self, song, msec):
        if not app.player.paused:
            self._clear_timers()
            self._clear_timers_og()
            self._set_timers()
            self._set_timers_og()

    def _greater(self, array, probe):
        length = len(array)
        if length == 0:
            return -1
        elif probe < array[0][0]:
            return 0
        elif probe >= array[length - 1][0]:
            return length
        else:
            return self._search(array, probe, 0, length - 1)

    def _search(self, array, probe, lower, upper):
        if lower == upper:
            if array[lower][0] <= probe:
                return lower + 1
            else:
                return lower
        else:
            middle = int((lower + upper) / 2)
            if array[middle][0] <= probe:
                return self._search(array, probe, middle + 1, upper)
            else:
                return self._search(array, probe, lower, middle)
