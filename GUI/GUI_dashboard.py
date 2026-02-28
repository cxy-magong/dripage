#!/usr/bin/env python
"""
Dripage GUI - Browser Management Dashboard (Fixed)

Dashboard-style interface for browser management with proper error handling and debugging.
"""
import os
import sys
from pathlib import Path
import yaml
import traceback
import platform
import subprocess

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List
import threading

# Import browser management functions
try:
    from cli.browser import (
        start_browser,
        stop_browser,
        get_browser_status,
        activate_browser
    )
    CLI_FUNCTIONS_LOADED = True
except Exception as e:
    print(f"Failed to import CLI functions: {e}")
    CLI_FUNCTIONS_LOADED = False


class BrowserCard(ttk.LabelFrame):
    """Browser card widget for displaying browser info and controls."""

    def __init__(self, parent, root: tk.Tk, browser_name: str, description: str, config_path: str,
                 on_start: callable, on_stop: callable, on_activate: callable,
                 on_copy_config_path: callable, on_open_config_editor: callable, **kwargs):
        super().__init__(parent, text=browser_name, padding="15", **kwargs)

        self.root = root  # Store root for main thread UI updates
        self.browser_name = browser_name
        self.description = description
        self.config_path = config_path  # Store config path
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_activate = on_activate
        self.on_copy_config_path = on_copy_config_path
        self.on_open_config_editor = on_open_config_editor

        self.status = "stopped"
        self.setup_ui()

    def setup_ui(self):
        """Setup card UI."""
        # Description
        desc_label = ttk.Label(
            self,
            text=self.description,
            font=("Arial", 9),
            wraplength=300
        )
        desc_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        # Status indicator
        self.status_frame = tk.Frame(self, width=20, height=20, bg="#d0d0d0")
        self.status_frame.grid(row=1, column=0, padx=(0, 10), sticky=tk.NSEW)
        self.status_frame.grid_propagate(False)

        # Status label
        self.status_label = ttk.Label(
            self,
            text="已停止",
            font=("Arial", 8, "bold"),
            foreground="#666666"
        )
        self.status_label.grid(row=1, column=1, padx=(0, 10))

        # Info label (CDP URL, PID, etc. or config path)
        config_info = self._format_config_path(self.config_path)
        self.info_label = ttk.Label(
            self,
            text=config_info,
            font=("Consolas", 8),
            foreground="#888888",
            wraplength=200
        )
        self.info_label.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(0, 10))

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0), sticky=tk.EW)

        # Start/Stop button - Using explicit function reference
        self.action_button = tk.Button(
            button_frame,
            text="启动",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            width=10,
            relief=tk.FLAT,
            command=self._on_action_click,
            cursor="hand2"
        )
        self.action_button.pack(side=tk.LEFT, padx=2)

        # Activate button
        activate_btn = ttk.Button(
            button_frame,
            text="激活",
            width=10,
            command=lambda n=self.browser_name: self.on_activate(n)
        )
        activate_btn.pack(side=tk.LEFT, padx=2)

        # Copy config path button
        copy_path_btn = ttk.Button(
            button_frame,
            text="复制路径",
            width=8,
            command=lambda n=self.browser_name: self.on_copy_config_path(n)
        )
        copy_path_btn.pack(side=tk.LEFT, padx=2)

        # Open config editor button
        open_config_btn = ttk.Button(
            button_frame,
            text="编辑配置",
            width=8,
            command=lambda n=self.browser_name: self.on_open_config_editor(n)
        )
        open_config_btn.pack(side=tk.LEFT, padx=2)

    def _format_config_path(self, config_path: str) -> str:
        """
        Format config path for display.
        Shows absolute path for both relative and absolute config paths.
        """
        if not config_path:
            return "未运行"

        # Convert to absolute path
        path_obj = Path(config_path)

        # If relative, convert to absolute
        if not path_obj.is_absolute():
            absolute_path = (project_root / path_obj).resolve()
        else:
            absolute_path = path_obj.resolve()

        # Format for display (shorten if too long)
        path_str = str(absolute_path)

        # Show "..." if path is too long
        if len(path_str) > 40:
            # Show start and end of path
            start = path_str[:15]
            end = path_str[-20:]
            return f"配置: {start}...{end}"
        else:
            return f"配置: {path_str}"

    def _on_action_click(self):
        """Handle action button click (start/stop) - explicit method."""
        print(f"Button clicked for {self.browser_name}, current status: {self.status}")
        if self.status == "running":
            self.on_stop(self.browser_name)
        else:
            self.on_start(self.browser_name)

    def _update_status_ui(self, status: str, info: Optional[Dict[str, Any]] = None):
        """Update browser status display on main thread."""
        self.status = status

        if status == "running":
            # Green indicator
            self.status_frame.config(bg="#4CAF50")
            self.status_label.config(text="运行中", foreground="#4CAF50")
            self.action_button.config(text="停止", bg="#f44336")

            if info:
                cdp_url = info.get('cdp_url', 'N/A')
                pid = info.get('pid', 'N/A')
                address = info.get('address', 'N/A')
                self.info_label.config(text=f"CDP: {cdp_url}\nPID: {pid}\n地址: {address}")
        else:
            # Gray indicator
            self.status_frame.config(bg="#d0d0d0")
            self.status_label.config(text="已停止", foreground="#666666")
            self.action_button.config(text="启动", bg="#4CAF50")
            # Show config path when stopped
            config_info = self._format_config_path(self.config_path)
            self.info_label.config(text=config_info)

    def update_status(self, status: str, info: Optional[Dict[str, Any]] = None):
        """Update browser status display - calls on main thread."""
        print(f"Updating {self.browser_name} status to: {status}")
        # Schedule UI update on main thread
        self.root.after(0, lambda: self._update_status_ui(status, info))


class BrowserDashboard:
    """Main dashboard application for browser management."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dripage 浏览器管理面板")
        self.root.geometry("1200x800")

        # Auto-refresh flag
        self.auto_refresh_enabled = True

        # Store browser cards
        self.browser_cards: Dict[str, BrowserCard] = {}

        # Load browser configurations
        self.browser_configs = self.load_browser_configs()
        print(f"Loaded {len(self.browser_configs)} browser configurations")

        # Setup UI
        self.setup_ui()

        # Bind window activation events
        self.setup_window_events()

        # Initial status refresh (blocking, immediate)
        print("Performing initial status refresh...")
        self.refresh_status_sync()

        # Start auto-refresh
        print("Starting auto-refresh...")
        self.start_auto_refresh()

    def load_browser_configs(self) -> List[Dict[str, Any]]:
        """Load browser configurations from browsers.yaml."""
        try:
            config_path = project_root / "config" / "browsers.yaml"
            print(f"Loading config from: {config_path}")

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            browsers = config.get('browsers', [])
            print(f"Found {len(browsers)} browsers in config")
            return browsers
        except Exception as e:
            print(f"Error loading browser configs: {e}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"加载浏览器配置失败: {e}")
            return []

    def setup_window_events(self):
        """Setup window activation events."""
        print("Setting up window events...")
        self.root.bind("<Activate>", self._on_window_activate)
        self.root.bind("<FocusIn>", self._on_window_activate)
        self.root.bind("<Map>", self._on_window_activate)

    def _on_window_activate(self, event=None):
        """Handle window activation event."""
        print("Window activated - refreshing status...")
        self.refresh_status()
        if hasattr(self, 'status_bar'):
            self.root.after(0, lambda: self._update_status_bar("窗口已激活 - 正在刷新状态..."))

    def setup_ui(self):
        """Setup dashboard UI."""
        print("Setting up UI...")
        # Create main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="浏览器管理面板",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # Status summary
        self.status_summary = ttk.Label(
            header_frame,
            text="加载中...",
            font=("Arial", 10),
            foreground="#666666"
        )
        self.status_summary.pack(side=tk.RIGHT)

        # Browser cards container with scrollbar
        canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 20))

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Create browser cards
        for idx, browser_config in enumerate(self.browser_configs):
            name = browser_config.get('name', f'browser_{idx}')
            description = browser_config.get('description', 'No description')
            ini_file = browser_config.get('ini_file', '')

            print(f"Creating card for: {name}")

            card = BrowserCard(
                scrollable_frame,
                root=self.root,  # Pass root for main thread UI updates
                browser_name=name,
                description=description,
                config_path=ini_file,  # Pass config file path
                on_start=self._start_browser,
                on_stop=self._stop_browser,
                on_activate=self._activate_browser,
                on_copy_config_path=self._copy_config_path,
                on_open_config_editor=self._open_config_editor
            )

            # Store config data in card
            card.config_data = browser_config

            # Position in grid (3 columns)
            row = idx // 3
            col = idx % 3
            card.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Store reference
            self.browser_cards[name] = card

        # Configure grid weights for columns
        for col in range(3):
            scrollable_frame.columnconfigure(col, weight=1)

        # Status bar
        self.status_bar = ttk.Label(
            main_frame,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Consolas", 8)
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))

    def _update_status_bar(self, message: str):
        """Update status bar on main thread."""
        self.status_bar.config(text=message)

    def _update_summary(self, message: str):
        """Update summary on main thread."""
        self.status_summary.config(text=message)

        print("UI setup complete")

    def _start_browser(self, browser_name: str):
        """Start a browser instance - wrapper method."""
        print(f"Start button clicked for: {browser_name}")
        if hasattr(self, 'status_bar'):
            self.root.after(0, lambda: self._update_status_bar(f"正在启动 {browser_name}..."))

        def _start():
            try:
                result = start_browser(name=browser_name, config_override={})
                if result['success']:
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✓ {browser_name} 已启动"))
                    self.refresh_status()
                else:
                    error_msg = result['message']
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✗ 启动 {browser_name} 失败: {error_msg}"))
                    messagebox.showerror("错误", f"启动 {browser_name} 失败:\n{error_msg}")
            except Exception as e:
                print(f"Error starting browser: {e}")
                print(traceback.format_exc())
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 异常: {str(e)}"))
                messagebox.showerror("错误", f"异常: {str(e)}")

        threading.Thread(target=_start, daemon=True).start()

    def start_browser(self, browser_name: str):
        """Public method for starting browser."""
        self._start_browser(browser_name)

    def _stop_browser(self, browser_name: str):
        """Stop a browser instance - wrapper method."""
        print(f"Stop button clicked for: {browser_name}")
        if hasattr(self, 'status_bar'):
            self.root.after(0, lambda: self._update_status_bar(f"正在停止 {browser_name}..."))

        def _stop():
            try:
                result = stop_browser(name=browser_name)
                if result['success']:
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✓ {browser_name} 已停止"))
                    self.refresh_status()
                else:
                    error_msg = result['message']
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✗ 停止 {browser_name} 失败: {error_msg}"))
                    messagebox.showerror("错误", f"停止 {browser_name} 失败:\n{error_msg}")
            except Exception as e:
                print(f"Error stopping browser: {e}")
                print(traceback.format_exc())
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 异常: {str(e)}"))
                messagebox.showerror("错误", f"异常: {str(e)}")

        threading.Thread(target=_stop, daemon=True).start()

    def stop_browser(self, browser_name: str):
        """Public method for stopping browser."""
        self._stop_browser(browser_name)

    def refresh_status_sync(self):
        """Refresh all browser statuses synchronously (blocking)."""
        print("Refreshing status (sync)...")
        try:
            if not CLI_FUNCTIONS_LOADED:
                print("CLI functions not loaded - skipping status refresh")
                return

            result = get_browser_status(name=None)
            print(f"Status result: {result}")

            if result['success']:
                data = result['data']
                self.update_browser_cards(data)
                self.update_summary(data)
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar("状态加载成功"))
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"Failed to get status: {error_msg}")
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 获取状态失败: {error_msg}"))
        except Exception as e:
            print(f"Error refreshing status: {e}")
            print(traceback.format_exc())
            if hasattr(self, 'status_bar'):
                self.root.after(0, lambda: self._update_status_bar(f"✗ 刷新状态错误: {str(e)}"))

    def _activate_browser(self, browser_name: str):
        """Activate browser window - wrapper method."""
        print(f"Activate button clicked for: {browser_name}")
        if hasattr(self, 'status_bar'):
            self.root.after(0, lambda: self._update_status_bar(f"正在激活 {browser_name}..."))

        def _activate():
            try:
                result = activate_browser(name=browser_name)
                if result['success']:
                    window_title = result.get('window_title', 'Unknown')
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✓ {browser_name} 已激活: {window_title}"))
                else:
                    error_msg = result.get('error', 'Unknown error')
                    if hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self._update_status_bar(f"✗ 激活 {browser_name} 失败: {error_msg}"))
                    messagebox.showerror("错误", f"激活 {browser_name} 失败:\n{error_msg}")
            except Exception as e:
                print(f"Error activating browser: {e}")
                print(traceback.format_exc())
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 异常: {str(e)}"))
                messagebox.showerror("错误", f"异常: {str(e)}")

        threading.Thread(target=_activate, daemon=True).start()

    def activate_browser(self, browser_name: str):
        """Public method for activating browser."""
        self._activate_browser(browser_name)

    def _get_absolute_config_path(self, config_path: str) -> str:
        """
        Convert config path to absolute path.

        Handles both relative and absolute paths:
        - Relative: config/browser/browser1.ini -> project_root/config/browser/browser1.ini
        - Absolute: G:\\code\\amazone\\...\\config\\dp_conf\\9321.ini
        """
        if not config_path:
            return config_path

        # Convert to Path object
        path_obj = Path(config_path)

        # If already absolute, return it
        if path_obj.is_absolute():
            # Normalize path separators for current OS
            return str(path_obj)

        # If relative, convert to absolute based on project root
        absolute_path = project_root / path_obj

        # Normalize and return
        return str(absolute_path.resolve())

    def _copy_config_path(self, browser_name: str):
        """Copy browser config file path to clipboard."""
        print(f"Copy config path button clicked for: {browser_name}")
        if browser_name in self.browser_cards:
            card = self.browser_cards[browser_name]
            config_data = card.config_data
            config_path = config_data.get('ini_file', '')

            if not config_path:
                messagebox.showwarning("警告", f"{browser_name} 没有配置文件路径")
                return

            # Convert to absolute path
            absolute_path = self._get_absolute_config_path(config_path)

            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(absolute_path)
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✓ 已复制 {browser_name} 的配置路径"))
                print(f"Config path copied: {absolute_path}")
            except Exception as e:
                print(f"Error copying config path: {e}")
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 复制配置路径失败: {str(e)}"))
                messagebox.showerror("错误", f"复制配置路径失败: {str(e)}")

    def _open_config_editor(self, browser_name: str):
        """Open config file in default editor."""
        print(f"Open config editor button clicked for: {browser_name}")
        if browser_name in self.browser_cards:
            card = self.browser_cards[browser_name]
            config_data = card.config_data
            config_path = config_data.get('ini_file', '')

            if not config_path:
                messagebox.showwarning("警告", f"{browser_name} 没有配置文件路径")
                return

            # Convert to absolute path
            absolute_path = self._get_absolute_config_path(config_path)

            # Check if file exists
            if not Path(absolute_path).exists():
                messagebox.showerror("错误", f"配置文件不存在:\n{absolute_path}")
                return

            try:
                # Open config file with default editor
                if platform.system() == 'Windows':
                    os.startfile(absolute_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', absolute_path])
                else:  # Linux
                    subprocess.run(['xdg-open', absolute_path])

                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✓ 已打开 {browser_name} 的配置文件"))
                print(f"Config file opened: {absolute_path}")
            except Exception as e:
                print(f"Error opening config file: {e}")
                if hasattr(self, 'status_bar'):
                    self.root.after(0, lambda: self._update_status_bar(f"✗ 打开配置文件失败: {str(e)}"))
                messagebox.showerror("错误", f"打开配置文件失败: {str(e)}")

    def refresh_status(self):
        """Refresh all browser statuses."""
        if not self.auto_refresh_enabled:
            return

        def _refresh():
            try:
                if not CLI_FUNCTIONS_LOADED:
                    print("CLI functions not loaded - skipping status refresh")
                    return

                result = get_browser_status(name=None)

                if result['success']:
                    data = result['data']
                    self.update_browser_cards(data)
                    self.update_summary(data)
            except Exception as e:
                print(f"Error in async status refresh: {e}")
                # Don't show error for async refresh failures

        threading.Thread(target=_refresh, daemon=True).start()

    def update_browser_cards(self, data: Dict[str, Any]):
        """Update all browser cards with current status."""
        print(f"Updating browser cards with data: {data}")

        if 'browsers' in data:
            browsers = data['browsers']
            print(f"Found {len(browsers)} browsers in status")

            for browser_name, card in self.browser_cards.items():
                if browser_name in browsers:
                    browser_info = browsers[browser_name]
                    status = browser_info.get('status', 'stopped')
                    print(f"Updating {browser_name}: {status}")
                    card.update_status(status, browser_info)
                else:
                    # Browser not found in status, assume stopped
                    print(f"Browser {browser_name} not in status data - marking as stopped")
                    card.update_status('stopped', None)

    def update_summary(self, data: Dict[str, Any]):
        """Update status summary."""
        if 'browsers' in data:
            total = data.get('total', 0)
            running = data.get('running', 0)
            print(f"Summary: {total} total, {running} running")
            # Update on main thread
            self.root.after(0, lambda: self._update_summary(f"总计: {total} | 运行中: {running}"))

    def start_auto_refresh(self):
        """Start auto-refresh of browser status."""
        if self.auto_refresh_enabled:
            print("Auto-refresh tick...")
            self.refresh_status()
            self.root.after(2000, self.start_auto_refresh)


def main():
    """Main entry point."""
    print("Starting Dripage Browser Dashboard...")
    print(f"CLI functions loaded: {CLI_FUNCTIONS_LOADED}")

    if not CLI_FUNCTIONS_LOADED:
        messagebox.showerror(
            "错误",
            "加载CLI浏览器函数失败。\n"
            "请检查dripage是否正确配置。"
        )
        return

    root = tk.Tk()
    app = BrowserDashboard(root)
    root.mainloop()


if __name__ == '__main__':
    main()
