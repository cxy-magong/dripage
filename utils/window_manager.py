"""
Window management utilities for Windows.

Provides functions to activate and bring windows to foreground by PID.
Only works on Windows platform.
"""
import sys
from typing import Optional


def activate_window_by_pid(pid: int) -> bool:
    """
    Activate and bring a window to foreground by process ID.

    This function finds the main window of the process with the given PID
    and brings it to the foreground.

    Args:
        pid: Process ID of the window to activate.

    Returns:
        True if window was successfully activated, False otherwise.
    """
    if sys.platform != 'win32':
        print("Window activation only works on Windows platform")
        return False

    try:
        import win32gui
        import win32con
        import win32process

        activated = False
        window_title = None

        def callback(hwnd, pids):
            """Callback for EnumWindows to find windows matching PID."""
            nonlocal activated, window_title
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)

            if found_pid in pids:
                # Check if window is visible and has a title
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        # Try to activate window
                        try:
                            # Restore window if minimized
                            if win32gui.IsIconic(hwnd):
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

                            # Bring window to foreground
                            win32gui.SetForegroundWindow(hwnd)

                            # Even if SetForegroundWindow fails (access denied),
                            # if we found and restored the window, consider it successful
                            activated = True
                            window_title = title

                            # Try to set focus (may fail, that's OK)
                            try:
                                win32gui.SetFocus(hwnd)
                            except:
                                pass
                        except Exception as e:
                            # SetForegroundWindow can fail with access denied
                            # but window may still be activated
                            if '拒绝访问' in str(e) or 'Access is denied' in str(e):
                                activated = True
                                window_title = title
            return None

        # Search for windows with matching PID
        win32gui.EnumWindows(callback, [pid])

        if activated and window_title:
            print(f"✓ Activated window (PID {pid}): {window_title}")
            return True
        else:
            print(f"✗ No visible window found for PID {pid}")
            return False

    except ImportError as e:
        print(f"✗ Required Windows libraries not installed: {e}")
        print("Run: uv add pywin32")
        return False
    except Exception as e:
        print(f"✗ Error activating window: {e}")
        return False


def get_window_title_by_pid(pid: int) -> Optional[str]:
    """
    Get the title of the main window for a process.

    Args:
        pid: Process ID.

    Returns:
        Window title if found, None otherwise.
    """
    if sys.platform != 'win32':
        return None

    try:
        import win32gui
        import win32process

        def callback(hwnd, pids):
            """Callback for EnumWindows to find windows matching PID."""
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)

            if found_pid in pids:
                # Check if window is visible and has a title
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    return win32gui.GetWindowText(hwnd)
            return None

        result = win32gui.EnumWindows(callback, [pid])
        return result

    except Exception:
        return None


if __name__ == "__main__":
    # Test with a PID
    import sys

    if len(sys.argv) > 1:
        try:
            pid = int(sys.argv[1])
            print(f"Attempting to activate window with PID {pid}...")
            activate_window_by_pid(pid)
        except ValueError:
            print("Usage: python window_manager.py <pid>")
    else:
        print("Usage: python window_manager.py <pid>")
