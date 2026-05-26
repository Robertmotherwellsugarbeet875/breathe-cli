#!/usr/bin/env python3
"""Breathe CLI — paced breathing for HFrEF vagal training. macOS only."""

import argparse
import ctypes
import os
import select
import signal
import shutil
import subprocess
import sys
import termios
import time
import tty
from dataclasses import dataclass

# ── Constants ────────────────────────────────────────────────────────

VERSION = '1.4'

PRESETS = {
    'morning': {'duration_min': 10, 'inhale_s': 5, 'exhale_s': 5},
    'evening': {'duration_min': 15, 'inhale_s': 4, 'exhale_s': 6},
    'long':    {'duration_min': 20, 'inhale_s': 4, 'exhale_s': 6},
}

PRESET_DESCRIPTIONS = {'morning': 'Daily baseline', 'evening': 'Sympathetic wind-down',
                       'long': 'Full dose, Bernardi protocol'}

SOUND_INHALE = '/System/Library/Sounds/Tink.aiff'
SOUND_EXHALE = '/System/Library/Sounds/Pop.aiff'
AFPLAY       = '/usr/bin/afplay'
AFPLAY_VOL   = '0.3'

LOG_FILE   = os.path.expanduser('~/.breathe_log.csv')
LOG_HEADER = 'date,time,preset,ratio,duration_target_s,duration_actual_s,breaths,completion_pct,status'

BAR_WIDTH      = 30
FRAME_RATE_HZ  = 20
FRAME_SLEEP    = 1.0 / FRAME_RATE_HZ
COUNTDOWN_SECS = 3
MIN_TERM_WIDTH = 40
MIN_CYCLE_SECS = 8

ANSI_CLEAR    = '\033[2J\033[H'
ANSI_HIDE_CUR = '\033[?25l'
ANSI_SHOW_CUR = '\033[?25h'
ANSI_RESET    = '\033[0m'
ANSI_DIM      = '\033[2m'
ANSI_CYAN     = '\033[36m'
ANSI_GREEN    = '\033[32m'
ANSI_CLR_LINE = '\033[K'

INHALE, EXHALE = 'INHALE', 'EXHALE'

SAFETY_TEXT = """\
Breathe CLI \u2014 safety notes
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

This app paces slow breathing at 6 breaths per minute for vagal tone
support. It is a habit tool, not a medical device.

STOP THE SESSION IMMEDIATELY if you experience:

  \u2022 Lightheadedness or dizziness \u2014 you may be breathing too deeply.
    Reduce depth, not rate. If it persists, stop.
  \u2022 Palpitations \u2014 stop, note the time, mention at your next
    cardiology visit.
  \u2022 Tingling in hands or face \u2014 hyperventilation signal. Stop,
    return to normal breathing.

This app deliberately does NOT support:
  \u2022 Breath retention (kumbhaka) of any length
  \u2022 Rapid breathing (kapalbhati, bhastrika, Wim Hof patterns)
  \u2022 Total breath cycles shorter than 8 seconds

Press q or Ctrl+C to end any session. Exit is always immediate."""

@dataclass
class Config:
    duration_s: int
    inhale_s: int
    exhale_s: int
    preset_name: str       # 'morning', 'evening', 'long', or 'custom'
    sound_enabled: bool
    quiet: bool

    @property
    def ratio_str(self):
        return '{}-{}'.format(self.inhale_s, self.exhale_s)

@dataclass
class Result:
    breaths: int = 0
    elapsed: float = 0.0
    completed: bool = False
    aborted: bool = False

@dataclass
class Layout:
    width: int
    height: int
    header_row: int
    phase_row: int
    bar_row: int
    footer_row: int
    minimal: bool
    use_colour: bool
    use_unicode: bool

def supports_colour():
    if os.environ.get('NO_COLOR'):
        return False
    return sys.stdout.isatty()

def supports_unicode():
    enc = getattr(sys.stdout, 'encoding', '') or ''
    return 'utf' in enc.lower()

def format_mmss(seconds):
    m, s = divmod(int(seconds), 60)
    return '{:02d}:{:02d}'.format(m, s)

def format_human(seconds):
    m, s = divmod(int(seconds), 60)
    if m > 0:
        return '{} min {} s'.format(m, s)
    return '{} s'.format(s)

def compute_layout():
    size = shutil.get_terminal_size((80, 24))
    w, h = size.columns, size.lines
    minimal = w < MIN_TERM_WIDTH
    mid = h // 2
    return Layout(
        width=w, height=h,
        header_row=max(mid - 4, 1),
        phase_row=max(mid - 1, 3),
        bar_row=max(mid + 1, 5),
        footer_row=min(mid + 4, h),
        minimal=minimal,
        use_colour=supports_colour(),
        use_unicode=supports_unicode(),
    )

class _SystemSoundPlayer:
    """AudioToolbox ctypes player — near-zero latency, no NSRunLoop."""

    def __init__(self):
        self._at = ctypes.cdll.LoadLibrary(
            '/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox')
        self._cf = ctypes.cdll.LoadLibrary(
            '/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        vp, cp, u32 = ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32
        self._cf.CFStringCreateWithCString.restype = vp
        self._cf.CFStringCreateWithCString.argtypes = [vp, cp, u32]
        self._cf.CFURLCreateWithFileSystemPath.restype = vp
        self._cf.CFURLCreateWithFileSystemPath.argtypes = [vp, vp, ctypes.c_int32, ctypes.c_bool]
        self._at.AudioServicesCreateSystemSoundID.argtypes = [vp, ctypes.POINTER(u32)]
        self._at.AudioServicesCreateSystemSoundID.restype = ctypes.c_int32
        self._at.AudioServicesPlaySystemSound.argtypes = [u32]
        self._at.AudioServicesPlaySystemSound.restype = None
        self._ids = {}
        for phase, path in [(INHALE, SOUND_INHALE), (EXHALE, SOUND_EXHALE)]:
            if not os.path.isfile(path):
                raise OSError('missing: ' + path)
            sid = self._register(path)
            if sid is None:
                raise OSError('AudioServices failed: ' + path)
            self._ids[phase] = sid

    def _register(self, path):
        kUTF8 = 0x08000100
        cf_str = self._cf.CFStringCreateWithCString(
            None, path.encode('utf-8'), kUTF8)
        if not cf_str:
            return None
        cf_url = self._cf.CFURLCreateWithFileSystemPath(
            None, cf_str, 0, False)  # 0 = kCFURLPOSIXPathStyle
        if not cf_url:
            return None
        sound_id = ctypes.c_uint32(0)
        err = self._at.AudioServicesCreateSystemSoundID(
            cf_url, ctypes.byref(sound_id))
        if err != 0:
            return None
        return sound_id.value

    def play(self, phase):
        sid = self._ids.get(phase)
        if sid is not None:
            self._at.AudioServicesPlaySystemSound(sid)

_sys_sound_player = None  # set by check_audio()

def check_audio(quiet):
    """Init audio subsystem. Returns 'system', 'afplay', 'bell'."""
    global _sys_sound_player
    try:  # Prefer AudioToolbox: no run loop, near-zero latency
        _sys_sound_player = _SystemSoundPlayer()
        return 'system'
    except (OSError, AttributeError, TypeError):
        pass
    if (os.path.isfile(AFPLAY) and os.access(AFPLAY, os.X_OK)
            and os.path.isfile(SOUND_INHALE)
            and os.path.isfile(SOUND_EXHALE)):
        return 'afplay'
    if not quiet:
        sys.stderr.write('audio unavailable: falling back to terminal bell\n')
    return 'bell'

def play_sound(phase, audio_mode):
    if audio_mode == 'system':
        _sys_sound_player.play(phase)
    elif audio_mode == 'afplay':
        path = SOUND_INHALE if phase == INHALE else SOUND_EXHALE
        try:
            subprocess.Popen(
                [AFPLAY, '-v', AFPLAY_VOL, path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass
    elif audio_mode == 'bell':
        sys.stdout.write('\a')
        sys.stdout.flush()

def setup_raw_tty():
    if not sys.stdin.isatty():
        return None
    try:
        old = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return old
    except termios.error:
        return None

def restore_tty(old_settings):
    if old_settings is not None:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except termios.error:
            pass

def poll_key():
    if not sys.stdin.isatty():
        return None
    try:
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            return sys.stdin.read(1)
    except (OSError, ValueError):
        pass
    return None

def move_to(row, col):
    sys.stdout.write('\033[{};{}H'.format(row, col))

def draw_header(layout, config, elapsed, paused, muted):
    move_to(layout.header_row, 1)
    sys.stdout.write(ANSI_CLR_LINE)
    parts = []
    if paused:
        parts.append('\u23f8' if layout.use_unicode else 'P')
    if muted:
        parts.append('\U0001f507' if layout.use_unicode else 'M')
    if not parts:
        parts.append('\u25cf' if layout.use_unicode else '*')
    indicator = ' '.join(parts)
    line = '  {} \u00b7 {} \u00b7 {}   [{}]'.format(
        config.preset_name, config.ratio_str,
        format_mmss(max(0, config.duration_s - elapsed)),
        indicator,
    )
    sys.stdout.write(line)

def draw_phase(layout, phase):
    move_to(layout.phase_row, 1)
    sys.stdout.write(ANSI_CLR_LINE)
    if layout.use_colour:
        colour = ANSI_CYAN if phase == INHALE else ANSI_GREEN
        styled = colour + phase + ANSI_RESET
    else:
        styled = phase
    if layout.minimal:
        sys.stdout.write('  ' + styled)
    else:
        pad = (layout.width - len(phase)) // 2
        sys.stdout.write(' ' * pad + styled)

def draw_bar(layout, progress, phase):
    move_to(layout.bar_row, 1)
    sys.stdout.write(ANSI_CLR_LINE)
    if phase == INHALE:
        filled = int(progress * BAR_WIDTH)
    else:
        filled = int((1.0 - progress) * BAR_WIDTH)
    filled = max(0, min(BAR_WIDTH, filled))
    empty = BAR_WIDTH - filled
    if layout.use_unicode:
        bar = '\u2588' * filled + '\u2591' * empty
    else:
        bar = '#' * filled + '-' * empty
    if layout.minimal:
        sys.stdout.write('  ' + bar)
    else:
        pad = (layout.width - BAR_WIDTH) // 2
        sys.stdout.write(' ' * pad + bar)

def draw_footer(layout, paused):
    move_to(layout.footer_row, 1)
    sys.stdout.write(ANSI_CLR_LINE)
    if paused:
        text = 'space resume \u00b7 q quit'
    else:
        text = 'space pause \u00b7 s mute \u00b7 q quit'
    if layout.use_colour:
        text = ANSI_DIM + text + ANSI_RESET
    sys.stdout.write('  ' + text)

def render_frame(layout, config, elapsed, phase, progress, paused, muted):
    draw_header(layout, config, elapsed, paused, muted)
    draw_phase(layout, phase)
    draw_bar(layout, progress, phase)
    draw_footer(layout, paused)
    sys.stdout.flush()

_abort = [False]

def _sigint_handler(signum, frame):
    _abort[0] = True

def run_countdown(layout, config):
    """Run the 3-second settle countdown. Returns False if aborted."""
    for i in range(COUNTDOWN_SECS, 0, -1):
        if _abort[0]:
            return False
        move_to(layout.phase_row, 1)
        sys.stdout.write(ANSI_CLR_LINE)
        label = str(i)
        if layout.minimal:
            sys.stdout.write('  ' + label)
        else:
            pad = (layout.width - len(label)) // 2
            sys.stdout.write(' ' * pad + label)
        draw_header(layout, config, 0.0, False, False)
        draw_bar(layout, 0.0, INHALE)
        draw_footer(layout, False)
        sys.stdout.flush()
        for _ in range(FRAME_RATE_HZ):
            if _abort[0]:
                return False
            key = poll_key()
            if key == 'q':
                return False
            time.sleep(FRAME_SLEEP)
    return True

def run_session(config, result):
    is_tty = sys.stdout.isatty() and sys.stdin.isatty()

    # ── Non-TTY path ─────────────────────────────────────────────
    if not is_tty:
        if not config.quiet:
            sys.stderr.write('Warning: not a TTY, running without animation.\n')
        start = time.monotonic()
        cycle_s = config.inhale_s + config.exhale_s
        try:
            time.sleep(config.duration_s)
            result.completed = True
        except KeyboardInterrupt:
            result.aborted = True
        result.elapsed = min(time.monotonic() - start, float(config.duration_s))
        result.breaths = int(result.elapsed // cycle_s)
        return

    audio_mode = check_audio(config.quiet) if config.sound_enabled else 'none'
    layout = compute_layout()
    if layout.minimal and not config.quiet:
        sys.stderr.write('Warning: terminal narrow, running in minimal mode.\n')

    old_termios = setup_raw_tty()
    old_sigint = signal.signal(signal.SIGINT, _sigint_handler)
    _abort[0] = False

    muted = not config.sound_enabled
    total_paused = 0.0

    try:
        sys.stdout.write(ANSI_HIDE_CUR)
        sys.stdout.write(ANSI_CLEAR)
        sys.stdout.flush()

        if not run_countdown(layout, config):
            result.aborted = True
            return

        session_start = time.monotonic()
        next_boundary = session_start  # ideal wall-clock phase edge

        while True:
            elapsed = time.monotonic() - session_start - total_paused
            if elapsed >= config.duration_s:
                result.completed = True
                break
            if _abort[0]:
                result.aborted = True
                break

            for phase in (INHALE, EXHALE):
                phase_dur = config.inhale_s if phase == INHALE else config.exhale_s
                phase_end = next_boundary + phase_dur

                if not muted and audio_mode != 'none':
                    play_sound(phase, audio_mode)

                while True:
                    now = time.monotonic()
                    phase_elapsed = now - next_boundary
                    if now >= phase_end:
                        break

                    if _abort[0]:
                        result.aborted = True
                        result.elapsed = now - session_start - total_paused
                        return

                    key = poll_key()
                    if key == 'q':
                        result.aborted = True
                        result.elapsed = now - session_start - total_paused
                        return
                    elif key == ' ':
                        pause_start = time.monotonic()
                        progress = phase_elapsed / phase_dur
                        elapsed_now = now - session_start - total_paused
                        render_frame(layout, config, elapsed_now, phase,
                                     progress, True, muted)
                        abort_in_pause = False
                        while True:
                            if _abort[0]:
                                abort_in_pause = True
                                break
                            pk = poll_key()
                            if pk == ' ':
                                break
                            elif pk == 'q':
                                abort_in_pause = True
                                break
                            elif pk == 's':
                                muted = not muted
                                render_frame(layout, config, elapsed_now, phase,
                                             progress, True, muted)
                            time.sleep(FRAME_SLEEP)
                        pause_dur = time.monotonic() - pause_start
                        total_paused += pause_dur
                        next_boundary += pause_dur
                        phase_end += pause_dur
                        if abort_in_pause:
                            result.aborted = True
                            result.elapsed = (time.monotonic() - session_start
                                              - total_paused)
                            return
                        continue
                    elif key == 's':
                        muted = not muted

                    progress = phase_elapsed / phase_dur
                    elapsed_now = now - session_start - total_paused
                    render_frame(layout, config, elapsed_now, phase,
                                 progress, False, muted)
                    time.sleep(FRAME_SLEEP)

                # Advance to ideal boundary — no drift accumulation
                next_boundary = phase_end

                # Phase complete — count after exhale (= one full cycle)
                if phase == EXHALE:
                    result.breaths += 1

                elapsed = time.monotonic() - session_start - total_paused
                if elapsed >= config.duration_s:
                    result.completed = True
                    break
                if _abort[0]:
                    result.aborted = True
                    break

            if result.completed or result.aborted:
                break

        result.elapsed = time.monotonic() - session_start - total_paused

    finally:
        sys.stdout.write(ANSI_SHOW_CUR)
        sys.stdout.write(ANSI_RESET)
        move_to(layout.footer_row + 2, 1)
        sys.stdout.flush()
        restore_tty(old_termios)
        signal.signal(signal.SIGINT, old_sigint)

def print_summary(config, result):
    if config.preset_name != 'custom':
        target = '{} min ({} preset, {})'.format(
            config.duration_s // 60, config.preset_name, config.ratio_str)
    else:
        target = '{} min (custom, {})'.format(
            config.duration_s // 60, config.ratio_str)

    pct = min(100, int(result.elapsed / config.duration_s * 100)) if config.duration_s > 0 else 100
    status = 'completed' if result.completed else 'ended early (user)'

    print('Session summary')
    print('\u2500' * 15)
    print('Target:    {}'.format(target))
    print('Completed: {} ({}%)'.format(format_human(result.elapsed), pct))
    print('Breaths:   {} full cycles'.format(result.breaths))
    print('Status:    {}'.format(status))

def log_session(config, result, session_start_time):
    """Append one CSV row to ~/.breathe_log.csv. Never raises."""
    try:
        write_header = not os.path.isfile(LOG_FILE)
        with open(LOG_FILE, 'a') as f:
            if write_header:
                f.write(LOG_HEADER + '\n')
            pct = min(100, int(result.elapsed / config.duration_s * 100)) if config.duration_s > 0 else 100
            status = 'completed' if result.completed else 'ended early (user)'
            row = '{},{},{},{},{},{},{},{},{}'.format(
                time.strftime('%Y-%m-%d', session_start_time),
                time.strftime('%H:%M:%S', session_start_time),
                config.preset_name,
                config.ratio_str,
                config.duration_s,
                int(result.elapsed),
                result.breaths,
                pct,
                status,
            )
            f.write(row + '\n')
    except OSError as e:
        sys.stderr.write('Warning: could not write session log: {}\n'.format(e))

def print_log_path():
    if os.path.isfile(LOG_FILE):
        print(LOG_FILE)
    else:
        print('{} (no sessions logged yet)'.format(LOG_FILE))

def print_safety():
    print(SAFETY_TEXT)

def print_presets():
    print('Available presets:\n')
    fmt = '  {:<10} {:>8}   {:<20} {}'
    print(fmt.format('Name', 'Duration', 'Ratio (in-ex)', 'Target use'))
    print(fmt.format('\u2500' * 10, '\u2500' * 8, '\u2500' * 20, '\u2500' * 24))
    for name, p in PRESETS.items():
        bpm = 60.0 / (p['inhale_s'] + p['exhale_s'])
        ratio = '{}s-{}s ({:.0f} bpm)'.format(p['inhale_s'], p['exhale_s'], bpm)
        print(fmt.format(name, '{} min'.format(p['duration_min']),
                         ratio, PRESET_DESCRIPTIONS[name]))

def _die(msg):
    sys.stderr.write('Error: ' + msg + '\n')
    sys.exit(1)

def parse_ratio(ratio_str):
    _fmt_err = 'Ratio must be in the form `inhale-exhale` (e.g. `5-5` or `4-6`).'
    parts = ratio_str.split('-')
    if len(parts) > 2:
        _die('Three-number ratios imply a breath hold. '
             'This app does not support breath retention. See `breathe --safety`.')
    if len(parts) != 2:
        _die(_fmt_err)
    try:
        inhale, exhale = int(parts[0]), int(parts[1])
    except ValueError:
        _die(_fmt_err)
    if inhale + exhale < MIN_CYCLE_SECS:
        _die('Total breath cycle must be \u2265 8 seconds (no rapid breathing).')
    if not (3 <= inhale <= 10):
        _die('Inhale must be 3\u201310 seconds.')
    if not (3 <= exhale <= 10):
        _die('Exhale must be 3\u201310 seconds.')
    return inhale, exhale

def build_parser():
    parser = argparse.ArgumentParser(
        prog='breathe',
        description='Paced breathing for HFrEF vagal training.',
        epilog='Example: breathe --preset morning',
    )
    parser.add_argument('--version', action='version',
                        version='breathe {}'.format(VERSION))
    parser.add_argument('--safety', action='store_true',
                        help='Show safety information and exit')
    parser.add_argument('--list-presets', action='store_true',
                        help='Show available presets and exit')
    parser.add_argument('--preset', '-p', choices=list(PRESETS.keys()),
                        help='Use a named preset (morning, evening, long)')
    parser.add_argument('--duration', '-d', type=int, metavar='MINUTES',
                        help='Session duration in minutes (1\u201360, default: 10)')
    parser.add_argument('--ratio', '-r', metavar='IN-EX',
                        help='Breath ratio as inhale-exhale (e.g. 5-5 or 4-6)')
    parser.add_argument('--no-sound', '-n', action='store_true',
                        help='Disable audio cues')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress startup warnings')
    parser.add_argument('--log', action='store_true',
                        help='Show log file path and exit')
    parser.add_argument('--no-log', action='store_true',
                        help='Suppress session logging for this run')
    return parser

def main():
    if sys.version_info < (3, 7):
        sys.stderr.write('Error: breathe requires Python 3.7+\n')
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()

    if args.safety:
        print_safety()
        sys.exit(0)

    if args.log:
        print_log_path()
        sys.exit(0)

    if args.list_presets:
        print_presets()
        sys.exit(0)

    # Build config from args
    if args.preset:
        if args.duration is not None or args.ratio is not None:
            _die('--preset cannot be combined with --duration or --ratio.')
        p = PRESETS[args.preset]
        inhale_s, exhale_s = p['inhale_s'], p['exhale_s']
        duration_min = p['duration_min']
        preset_name = args.preset
    elif args.duration is not None or args.ratio is not None:
        inhale_s, exhale_s = 5, 5
        duration_min = 10
        preset_name = 'custom'
        if args.ratio:
            inhale_s, exhale_s = parse_ratio(args.ratio)
        if args.duration is not None:
            duration_min = args.duration
    else:
        # No args: auto-select preset by time of day
        hour = time.localtime().tm_hour
        if hour < 12:
            preset_name = 'morning'
        elif hour < 17:
            preset_name = 'long'
        else:
            preset_name = 'evening'
        p = PRESETS[preset_name]
        inhale_s, exhale_s = p['inhale_s'], p['exhale_s']
        duration_min = p['duration_min']

    if not (1 <= duration_min <= 60):
        _die('Duration must be 1\u201360 minutes.')

    config = Config(
        duration_s=duration_min * 60,
        inhale_s=inhale_s,
        exhale_s=exhale_s,
        preset_name=preset_name,
        sound_enabled=not args.no_sound,
        quiet=args.quiet,
    )

    result = Result()
    exc_info = None
    session_start_time = time.localtime()

    try:
        run_session(config, result)
    except KeyboardInterrupt:
        result.aborted = True
    except Exception:
        exc_info = sys.exc_info()

    print_summary(config, result)

    if not args.no_log:
        log_session(config, result, session_start_time)

    if exc_info is not None:
        import traceback
        traceback.print_exception(*exc_info)
        sys.exit(1)

if __name__ == '__main__':
    main()
