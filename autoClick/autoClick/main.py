#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单桌面自动点击工具
功能：
- 选择点击位置（鼠标移动到目标点后捕获）
- 设置点击间隔范围（毫秒）
- 支持点击次数与点击类型
"""

import threading
import time
import random
import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui
from pynput import keyboard


class AutoClickApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("自动点击工具")
        self.root.geometry("420x360")
        self.root.resizable(False, False)

        self.stop_event = threading.Event()
        self.worker = None

        self.position = None

        self._build_ui()
        self.root.bind("<Control-t>", lambda _e: self.stop_clicking())
        self._start_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="点击间隔范围 (毫秒)").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, text="最小:").grid(row=1, column=0, sticky="e")
        ttk.Label(frame, text="最大:").grid(row=2, column=0, sticky="e")
        self.min_ms = tk.StringVar(value="500")
        self.max_ms = tk.StringVar(value="1000")
        ttk.Entry(frame, textvariable=self.min_ms, width=10).grid(row=1, column=1, sticky="w")
        ttk.Entry(frame, textvariable=self.max_ms, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="点击次数 (0=无限)").grid(row=3, column=0, sticky="e")
        self.total_clicks = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=self.total_clicks, width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="点击类型").grid(row=4, column=0, sticky="e")
        self.click_type = tk.StringVar(value="left")
        ttk.Combobox(
            frame,
            textvariable=self.click_type,
            values=["left", "right", "middle"],
            state="readonly",
            width=8,
        ).grid(row=4, column=1, sticky="w")

        ttk.Separator(frame).grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(frame, text="点击位置").grid(row=6, column=0, sticky="e")
        self.position_var = tk.StringVar(value="未选择")
        ttk.Label(frame, textvariable=self.position_var).grid(row=6, column=1, sticky="w")

        ttk.Button(frame, text="选择位置(3秒)", command=self.capture_position).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(6, 2)
        )
        ttk.Button(frame, text="使用当前鼠标位置", command=self.use_current_position).grid(
            row=8, column=0, columnspan=2, sticky="ew"
        )

        ttk.Separator(frame).grid(row=9, column=0, columnspan=2, sticky="ew", pady=10)

        self.start_btn = ttk.Button(frame, text="开始", command=self.start_clicking)
        self.stop_btn = ttk.Button(frame, text="停止", command=self.stop_clicking, state=tk.DISABLED)
        self.start_btn.grid(row=10, column=0, sticky="ew")
        self.stop_btn.grid(row=10, column=1, sticky="ew")

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(frame, textvariable=self.status_var, foreground="#444").grid(
            row=11, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

        for i in range(2):
            frame.columnconfigure(i, weight=1)

    def _start_hotkeys(self) -> None:
        self.hotkey_listener = keyboard.GlobalHotKeys(
            {"<ctrl>+t": lambda: self.root.after(0, self.stop_clicking)}
        )
        self.hotkey_listener.start()

    def _on_close(self) -> None:
        try:
            if hasattr(self, "hotkey_listener"):
                self.hotkey_listener.stop()
        finally:
            self.stop_clicking()
            self.root.destroy()

    def capture_position(self) -> None:
        def worker():
            self._set_status("请在3秒内将鼠标移到目标位置...")
            time.sleep(3)
            pos = pyautogui.position()
            self.root.after(0, lambda: self._set_position(pos))

        threading.Thread(target=worker, daemon=True).start()

    def use_current_position(self) -> None:
        pos = pyautogui.position()
        self._set_position(pos)

    def _set_position(self, pos) -> None:
        self.position = (pos.x, pos.y)
        self.position_var.set(f"({pos.x}, {pos.y})")
        self._set_status("已选择点击位置")

    def start_clicking(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if not self.position:
            messagebox.showwarning("提示", "请先选择点击位置")
            return

        try:
            min_ms = int(self.min_ms.get())
            max_ms = int(self.max_ms.get())
            total = int(self.total_clicks.get())
        except ValueError:
            messagebox.showerror("错误", "间隔和次数必须是整数")
            return

        if min_ms <= 0 or max_ms <= 0:
            messagebox.showerror("错误", "间隔必须大于0")
            return
        if min_ms > max_ms:
            messagebox.showerror("错误", "最小间隔不能大于最大间隔")
            return
        if total < 0:
            messagebox.showerror("错误", "点击次数不能为负数")
            return

        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self._set_status("正在点击...")

        self.worker = threading.Thread(
            target=self._click_loop, args=(min_ms, max_ms, total), daemon=True
        )
        self.worker.start()

    def stop_clicking(self) -> None:
        self.stop_event.set()
        self._set_status("已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def _click_loop(self, min_ms: int, max_ms: int, total: int) -> None:
        count = 0
        button = self.click_type.get()
        while not self.stop_event.is_set() and (total == 0 or count < total):
            if min_ms == max_ms:
                lower = max(1, int(max_ms / 3))
                interval = random.uniform(lower, max_ms) / 1000.0
            else:
                interval = random.uniform(min_ms, max_ms) / 1000.0

            offset_x = random.randint(0, 50)
            offset_y = random.randint(0, 50)
            target_x = self.position[0] + offset_x
            target_y = self.position[1] + offset_y
            pyautogui.click(target_x, target_y, button=button)
            count += 1
            self.root.after(0, lambda c=count: self._set_status(f"已点击 {c} 次"))
            if self.stop_event.wait(interval):
                break

        self.root.after(0, self.stop_clicking)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)


def main() -> None:
    root = tk.Tk()
    app = AutoClickApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

