import ctypes
import threading
import time
import tkinter as tk
from tkinter import messagebox

from pynput import keyboard, mouse


def _enable_dpi_awareness():
    if hasattr(ctypes, "windll"):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI
            return
        except Exception:
            pass
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _serialize_key(key):
    if isinstance(key, keyboard.KeyCode):
        return {"kind": "char", "value": key.char}
    return {"kind": "key", "value": key.name}


def _deserialize_key(payload):
    if payload["kind"] == "char":
        return keyboard.KeyCode.from_char(payload["value"])
    return keyboard.Key[payload["value"]]


class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面操作记录工具")

        self.status_var = tk.StringVar(value="状态：未录制")
        self.loop_var = tk.StringVar(value="1")

        self.events = []
        self.recording = False
        self.playing = False
        self.ctrl_pressed = False
        self.recording_start = None
        self.stop_requested = False
        self.playback_stop_requested = False
        self.playback_stopped = False
        self.click_settle_delay = 0.01
        self.release_settle_delay = 0.02

        self.keyboard_listener = None
        self.mouse_listener = None
        self.hotkey = None
        self.playback_listener = None
        self.playback_hotkey = None

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, textvariable=self.status_var).grid(row=0, column=0, columnspan=3, sticky="w")

        self.record_button = tk.Button(
            frame,
            text="开始录制",
            width=14,
            command=self.start_recording,
        )
        self.record_button.grid(row=1, column=0, padx=(0, 8), pady=8, sticky="w")

        self.play_button = tk.Button(
            frame,
            text="复现操作",
            width=14,
            command=self.start_playback,
            state=tk.DISABLED,
        )
        self.play_button.grid(row=1, column=1, padx=(0, 8), pady=8, sticky="w")

        tk.Label(frame, text="循环次数：").grid(row=2, column=0, sticky="e")
        self.loop_entry = tk.Entry(frame, textvariable=self.loop_var, width=6)
        self.loop_entry.grid(row=2, column=1, sticky="w")

        hint = "提示：录制中按 Ctrl + T 结束"
        tk.Label(frame, text=hint, fg="#555555").grid(row=3, column=0, columnspan=3, sticky="w")

    def start_recording(self):
        if self.recording or self.playing:
            return
        self.events = []
        self.recording = True
        self.ctrl_pressed = False
        self.stop_requested = False
        self.recording_start = time.monotonic()
        self.status_var.set("状态：录制中")
        self.record_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)

        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self.hotkey = keyboard.HotKey(
            keyboard.HotKey.parse("<ctrl>+t"),
            self._on_stop_hotkey,
        )
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.stop_requested = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        self.status_var.set(f"状态：已录制 {len(self.events)} 个事件")
        self.record_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL if self.events else tk.DISABLED)

    def _record_event(self, payload):
        if not self.recording:
            return
        payload["time"] = time.monotonic() - self.recording_start
        self.events.append(payload)

    def _canonical(self, key):
        if self.keyboard_listener:
            return self.keyboard_listener.canonical(key)
        return key

    def _on_stop_hotkey(self):
        if not self.recording:
            return
        self.stop_requested = True
        self.root.after(0, self.stop_recording)

    def _on_key_press(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_pressed = True
        if self.hotkey:
            self.hotkey.press(self._canonical(key))
        if self.stop_requested:
            return False
        self._record_event({"type": "key_press", "key": _serialize_key(key)})

    def _on_key_release(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_pressed = False
        if self.hotkey:
            self.hotkey.release(self._canonical(key))
        if self.stop_requested:
            return False
        self._record_event({"type": "key_release", "key": _serialize_key(key)})

    def _on_move(self, x, y):
        self._record_event({"type": "mouse_move", "x": x, "y": y})

    def _on_click(self, x, y, button, pressed):
        self._record_event(
            {
                "type": "mouse_click",
                "x": x,
                "y": y,
                "button": button.name,
                "pressed": pressed,
            }
        )

    def _on_scroll(self, x, y, dx, dy):
        self._record_event(
            {
                "type": "mouse_scroll",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
            }
        )

    def _parse_loops(self):
        raw = self.loop_var.get().strip()
        try:
            loops = int(raw)
        except ValueError:
            return None
        return loops if loops > 0 else None

    def start_playback(self):
        if self.recording or self.playing or not self.events:
            return
        loops = self._parse_loops()
        if loops is None:
            messagebox.showerror("输入错误", "循环次数需要为正整数")
            return

        self.playing = True
        self.playback_stop_requested = False
        self.playback_stopped = False
        self.status_var.set("状态：复现中")
        self.record_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.loop_entry.config(state=tk.DISABLED)

        self.playback_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse("<ctrl>+y"),
            self._on_stop_playback_hotkey,
        )
        self.playback_listener = keyboard.Listener(
            on_press=self._on_playback_key_press,
            on_release=self._on_playback_key_release,
        )
        self.playback_listener.start()

        thread = threading.Thread(target=self._playback_worker, args=(loops,), daemon=True)
        thread.start()

    def _on_stop_playback_hotkey(self):
        if not self.playing:
            return
        self.playback_stop_requested = True
        self.playback_stopped = True

    def _on_playback_key_press(self, key):
        if self.playback_hotkey:
            self.playback_hotkey.press(self._canonical(key))
        if self.playback_stop_requested:
            return False

    def _on_playback_key_release(self, key):
        if self.playback_hotkey:
            self.playback_hotkey.release(self._canonical(key))
        if self.playback_stop_requested:
            return False

    def _sleep_with_cancel(self, duration):
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time:
            if self.playback_stop_requested:
                return False
            remaining = end_time - time.monotonic()
            time.sleep(min(0.05, max(0.0, remaining)))
        return True

    def _settle_mouse(self):
        if self.click_settle_delay > 0:
            self._sleep_with_cancel(self.click_settle_delay)

    def _settle_after_release(self):
        if self.release_settle_delay > 0:
            self._sleep_with_cancel(self.release_settle_delay)

    def _playback_worker(self, loops):
        try:
            key_controller = keyboard.Controller()
            mouse_controller = mouse.Controller()
            pressed_buttons = set()
            last_mouse_pos = None

            for _ in range(loops):
                last_time = 0.0
                for event in self.events:
                    if self.playback_stop_requested:
                        return
                    delay = event["time"] - last_time
                    if delay > 0:
                        if not self._sleep_with_cancel(delay):
                            return
                    last_time = event["time"]

                    etype = event["type"]
                    if etype == "key_press":
                        key_controller.press(_deserialize_key(event["key"]))
                    elif etype == "key_release":
                        key_controller.release(_deserialize_key(event["key"]))
                    elif etype == "mouse_move":
                        target_pos = (event["x"], event["y"])
                        if pressed_buttons and last_mouse_pos is not None:
                            dx = target_pos[0] - last_mouse_pos[0]
                            dy = target_pos[1] - last_mouse_pos[1]
                            mouse_controller.move(dx, dy)
                        else:
                            mouse_controller.position = target_pos
                        last_mouse_pos = target_pos
                    elif etype == "mouse_click":
                        mouse_controller.position = (event["x"], event["y"])
                        last_mouse_pos = (event["x"], event["y"])
                        self._settle_mouse()
                        button = mouse.Button[event["button"]]
                        if event["pressed"]:
                            pressed_buttons.add(button)
                            mouse_controller.press(button)
                        else:
                            mouse_controller.release(button)
                            pressed_buttons.discard(button)
                            self._settle_after_release()
                    elif etype == "mouse_scroll":
                        mouse_controller.position = (event["x"], event["y"])
                        last_mouse_pos = (event["x"], event["y"])
                        mouse_controller.scroll(event["dx"], event["dy"])
        finally:
            self.root.after(0, self._playback_finished)

    def _playback_finished(self):
        self.playing = False
        if self.playback_stopped:
            self.status_var.set("状态：复现已停止，可修改次数继续复现")
        else:
            self.status_var.set("状态：复现完成，可修改次数继续复现")
        self.record_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL if self.events else tk.DISABLED)
        self.loop_entry.config(state=tk.NORMAL)
        if self.playback_listener:
            self.playback_listener.stop()
        self.playback_listener = None
        self.playback_hotkey = None
        self.playback_stop_requested = False
        self.playback_stopped = False


if __name__ == "__main__":
    _enable_dpi_awareness()
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()

