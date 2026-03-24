"""
Settings dialog for configuring key bindings.
"""
import tkinter as tk
from tkinter import messagebox
import re
import threading
import os
import sys
from config import load_config, save_config


class SettingsDialog:
    def __init__(self, parent=None):
        # Create the root window
        if parent:
            self.dialog = tk.Toplevel(parent)
        else:
            self.dialog = tk.Tk()
        
        self.dialog.title("cStrafe Settings - Key Bindings")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.attributes('-topmost', True)  # Keep on top

        # Use the same window icon as the app/tray icon.
        try:
            if getattr(sys, 'frozen', False):
                base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, 'images', 'tray_icon.ico')
            if os.path.exists(icon_path):
                self.dialog.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not set settings icon: {e}")
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Load current config
        try:
            self.config = load_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {
                "FORWARD": "W",
                "BACKWARD": "S",
                "LEFT": "A",
                "RIGHT": "D"
            }
        
        # Title label
        title_label = tk.Label(
            self.dialog,
            text="Directional movement keys",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame for inputs
        input_frame = tk.Frame(self.dialog)
        input_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Create input fields for each key
        self.entries = {}
        vcmd = (self.dialog.register(self._validate_key_entry), "%P")
        defaults = {
            "FORWARD": "W",
            "BACKWARD": "S",
            "LEFT": "A",
            "RIGHT": "D"
        }
        labels_info = [
            ("FORWARD", "Forward"),
            ("BACKWARD", "Backward"),
            ("LEFT", "Left"),
            ("RIGHT", "Right")
        ]
        
        for i, (key, label) in enumerate(labels_info):
            # Label
            label_widget = tk.Label(
                input_frame,
                text=label + ":",
                font=("Arial", 11),
                anchor="w"
            )
            label_widget.grid(row=i, column=0, sticky="w", pady=5)
            
            # Entry
            entry = tk.Entry(
                input_frame,
                font=("Arial", 11),
                width=5,
                justify="center",
                insertwidth=0,
                insertontime=0,
                insertofftime=0,
                highlightthickness=1,
                highlightbackground="#8a8a8a",
                highlightcolor="#8a8a8a",
                validate="key",
                validatecommand=vcmd
            )
            # Some Tk builds still draw a caret unless insert color matches the field background.
            entry.configure(insertbackground=entry.cget("bg"))
            initial_value = str(self.config.get(key, defaults[key])).strip().upper()[:1] or defaults[key]
            entry.insert(0, initial_value)
            entry.bind("<KeyPress>", lambda event, movement_key=key: self._replace_entry_on_keypress(movement_key, event))
            entry.bind("<KeyRelease>", lambda _event, movement_key=key: self._normalize_entry_value(movement_key))
            entry.bind("<<Paste>>", lambda _event, movement_key=key: self._normalize_entry_after_event(movement_key))
            entry.bind("<Control-v>", lambda _event, movement_key=key: self._normalize_entry_after_event(movement_key))
            entry.bind("<Control-V>", lambda _event, movement_key=key: self._normalize_entry_after_event(movement_key))
            entry.bind("<FocusIn>", lambda _event, movement_key=key: self._set_entry_focus_style(movement_key, focused=True))
            entry.bind("<FocusOut>", lambda _event, movement_key=key: self._set_entry_focus_style(movement_key, focused=False))
            entry.grid(row=i, column=1, sticky="w", padx=10, pady=5)
            self.entries[key] = entry
        
        # Info text
        info_label = tk.Label(
            self.dialog,
            text="Enter single alphanumeric characters only\n(A-Z, 0-9)",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=15)
        
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self.save_settings,
            width=10,
            bg="#4CAF50",
            fg="white"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_settings,
            width=15
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=10
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    @staticmethod
    def _validate_key_entry(proposed: str) -> bool:
        """Allow empty input while editing, but cap each key field to 1 character."""
        return len(proposed) <= 1

    def _normalize_entry_after_event(self, key: str) -> None:
        """Normalize after paste events once Tk updates the entry widget."""
        self.dialog.after_idle(lambda movement_key=key: self._normalize_entry_value(movement_key))

    def _set_entry_focus_style(self, key: str, focused: bool) -> None:
        """Highlight focused entry in red and restore neutral border on blur."""
        entry = self.entries[key]
        if focused:
            entry.config(highlightthickness=2, highlightbackground="#c62828", highlightcolor="#c62828")
        else:
            entry.config(highlightthickness=1, highlightbackground="#8a8a8a", highlightcolor="#8a8a8a")

    def _replace_entry_on_keypress(self, key: str, event) -> str | None:
        """Replace the current value with the typed character so users don't need backspace."""
        # Let control/navigation keys behave normally.
        if event.keysym in {"BackSpace", "Delete", "Left", "Right", "Tab", "ISO_Left_Tab", "Home", "End"}:
            return None
        if event.keysym in {"Return", "KP_Enter", "Escape"}:
            return "break"

        typed_char = event.char
        if not typed_char:
            return "break"

        entry = self.entries[key]
        entry.delete(0, tk.END)
        entry.insert(0, typed_char[:1].upper())
        return "break"

    def _normalize_entry_value(self, key: str) -> None:
        """Normalize entry values so UI always shows a single uppercase character."""
        entry = self.entries[key]
        current_value = entry.get()
        normalized_value = current_value[:1].upper()
        if current_value != normalized_value:
            entry.delete(0, tk.END)
            entry.insert(0, normalized_value)
    
    def validate_input(self) -> bool:
        """Validate that all inputs are single alphanumeric characters."""
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror(
                    "Invalid Input",
                    f"{key} cannot be empty."
                )
                entry.focus_set()
                return False
            if len(value) > 1:
                messagebox.showerror(
                    "Invalid Input",
                    f"{key} must be a single character."
                )
                entry.focus_set()
                return False
            if not re.match(r'^[A-Za-z0-9]$', value):
                messagebox.showerror(
                    "Invalid Input",
                    f"{key} must be alphanumeric (A-Z, 0-9)."
                )
                entry.focus_set()
                return False
        
        # Check for duplicate keys
        values = [entry.get().strip().upper() for entry in self.entries.values()]
        if len(values) != len(set(values)):
            messagebox.showerror(
                "Duplicate Keys",
                "Each key must be unique."
            )
            return False
        
        return True
    
    def save_settings(self):
        """Save the settings and close the dialog."""
        if not self.validate_input():
            return
        
        new_config = {
            key: entry.get().strip().upper()
            for key, entry in self.entries.items()
        }
        
        if save_config(new_config):
            messagebox.showinfo(
                "Success",
                "Key bindings saved successfully!\n\n"
                "The new settings will take effect when you:\n"
                "• Restart the application, OR\n"
                "• Press F8 to stop and restart the listener\n\n"
                "New settings:\n"
                f"  Forward: {new_config['FORWARD']}\n"
                f"  Backward: {new_config['BACKWARD']}\n"
                f"  Left: {new_config['LEFT']}\n"
                f"  Right: {new_config['RIGHT']}"
            )
            self.dialog.destroy()
        else:
            messagebox.showerror(
                "Error",
                "Failed to save settings.\n\n"
                "Please make sure you have write permissions\n"
                "in the application directory."
            )
    
    def reset_settings(self):
        """Reset to default settings."""
        if messagebox.askyesno("Confirm", "Reset all keys to defaults?"):
            for key, entry in self.entries.items():
                default_val = {"FORWARD": "W", "BACKWARD": "S", "LEFT": "A", "RIGHT": "D"}[key]
                entry.delete(0, tk.END)
                entry.insert(0, default_val)
    
    def run(self):
        """Display the dialog (handles threading context)."""
        try:
            if self.dialog.master:  # Has parent
                self.dialog.grab_set()
                self.dialog.focus_set()
                self.dialog.wait_window()
            else:  # Standalone
                self.dialog.mainloop()
        except Exception as e:
            print(f"Error displaying settings dialog: {e}")
            messagebox.showerror("Error", f"Failed to open settings dialog: {e}")
