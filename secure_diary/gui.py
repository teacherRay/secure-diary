"""
gui.py - Libadwaita / GTK 4 Desktop Interface for Secure Daily Diary

Features:
- Master password unlock and initial setup wizard
- Calendar date navigation and entry browsing
- Full-text encrypted search with live filtering
- Mood tracker and tag management
- Auto-save with debouncing & word count metrics
- Inactivity auto-lock timer (configurable)
- Password change with seamless re-encryption
- Decrypted Markdown journal export
"""

from __future__ import annotations

import datetime
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango

from .vault import (
    DiaryVault,
    DiaryVaultError,
    InvalidPasswordError,
    VaultAlreadyExistsError,
    VaultLockedError,
    get_default_vault_path,
)

MOOD_OPTIONS = [
    ("😊", "Happy"),
    ("😌", "Calm"),
    ("💡", "Inspired"),
    ("⚡", "Productive"),
    ("💖", "Grateful"),
    ("🧘", "Reflective"),
    ("😴", "Tired"),
    ("🌧️", "Down"),
]

APP_CSS = b"""
window {
    font-size: 14px;
}

.auth-card {
    background: alpha(@theme_bg_color, 0.9);
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 8px 24px alpha(black, 0.15);
}

.editor-title {
    font-size: 18px;
    font-weight: bold;
    border-radius: 8px;
    padding: 6px 12px;
}

.editor-tags {
    font-size: 13px;
    border-radius: 8px;
    padding: 4px 10px;
}

.diary-text-view {
    font-family: sans-serif;
    font-size: 15px;
    line-height: 1.6;
    padding: 16px;
    border-radius: 8px;
}

.sidebar-box {
    border-right: 1px solid alpha(@borders, 0.5);
    background: alpha(@theme_bg_color, 0.6);
}

.mood-btn {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 14px;
}

.mood-btn.active {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
    font-weight: bold;
}

.toolbar-btn {
    min-width: 32px;
    padding: 4px 8px;
    font-weight: bold;
}

.badge-saved {
    color: #2ec27e;
    font-weight: bold;
    font-size: 12px;
}

.badge-unsaved {
    color: #e5a50a;
    font-weight: bold;
    font-size: 12px;
}

.entry-list-item {
    padding: 8px 12px;
    border-radius: 8px;
}

.entry-date-label {
    font-weight: bold;
    font-size: 13px;
}

.entry-snippet-label {
    font-size: 12px;
    color: alpha(@theme_fg_color, 0.7);
}
"""


class DiaryApplication(Adw.Application):
    """Main Adwaita application for Secure Daily Diary."""

    def __init__(self, db_path: Optional[Path | str] = None):
        super().__init__(
            application_id="org.secure.DailyDiary",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.vault = DiaryVault(db_path)
        self.window: Optional[DiaryWindow] = None

    def do_activate(self):
        if not self.window:
            self._load_css()
            self.window = DiaryWindow(application=self, vault=self.vault)
        self.window.present()

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )


class DiaryWindow(Adw.ApplicationWindow):
    """Primary application window handling authentication, calendar, and diary editing."""

    def __init__(self, vault: DiaryVault, **kwargs):
        super().__init__(**kwargs)
        self.vault = vault
        self.set_title("Secure Daily Diary")
        self.set_default_size(1050, 720)

        # State tracking
        self.current_date = datetime.date.today().isoformat()
        self.current_mood = ""
        self.is_dirty = False
        self.auto_save_timeout_id: Optional[int] = None
        self.last_user_activity = time.time()
        self.auto_lock_minutes = int(self.vault.get_setting("auto_lock_minutes", "5"))

        # Root navigation stack (auth view vs main diary view)
        self.main_stack = Gtk.Stack()
        self.main_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Build views
        self.auth_view = self._build_auth_view()
        self.diary_view = self._build_diary_view()

        self.main_stack.add_named(self.auth_view, "auth")
        self.main_stack.add_named(self.diary_view, "diary")

        self.set_content(self.main_stack)

        # Activity monitoring for auto-lock
        self._setup_activity_monitoring()

        # Initial view selection
        self.show_auth_view()

    # -------------------------------------------------------------------------
    # Activity & Auto-Lock Monitoring
    # -------------------------------------------------------------------------
    def _setup_activity_monitoring(self):
        # Key controller
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_user_interaction)
        self.add_controller(key_ctrl)

        # Motion controller
        motion_ctrl = Gtk.EventControllerMotion()
        motion_ctrl.connect("motion", self._on_user_interaction)
        self.add_controller(motion_ctrl)

        # Periodic check timer (every 10 seconds)
        GLib.timeout_add_seconds(10, self._check_idle_timeout)

    def _on_user_interaction(self, *args) -> bool:
        self.last_user_activity = time.time()
        return False

    def _check_idle_timeout(self) -> bool:
        if not self.vault.is_unlocked:
            return True  # keep timer running
        
        if self.auto_lock_minutes <= 0:
            return True  # auto-lock disabled

        idle_seconds = time.time() - self.last_user_activity
        if idle_seconds >= (self.auto_lock_minutes * 60):
            # Save unsaved changes before locking
            if self.is_dirty:
                self._save_current_entry()
            self.lock_diary()
        return True

    # -------------------------------------------------------------------------
    # Authentication & Setup View
    # -------------------------------------------------------------------------
    def _build_auth_view(self) -> Gtk.Widget:
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        center_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        center_box.set_size_request(420, -1)
        center_box.add_css_class("auth-card")

        # Icon
        icon_image = Gtk.Image.new_from_icon_name("document-encrypt-symbolic")
        icon_image.set_pixel_size(64)
        center_box.append(icon_image)

        # Heading & description
        self.auth_title = Gtk.Label(label="Secure Daily Diary")
        self.auth_title.add_css_class("title-1")
        center_box.append(self.auth_title)

        self.auth_subtitle = Gtk.Label(
            label="AES-256-GCM Encrypted Local Journal",
            wrap=True,
            justify=Gtk.Justification.CENTER,
        )
        self.auth_subtitle.add_css_class("dim-label")
        center_box.append(self.auth_subtitle)

        # Password Entry
        self.pwd_entry = Gtk.PasswordEntry(placeholder_text="Master Password", show_peek_icon=True)
        self.pwd_entry.connect("activate", lambda _: self._on_auth_submit())
        center_box.append(self.pwd_entry)

        # Confirm Password Entry (only for setup)
        self.confirm_pwd_entry = Gtk.PasswordEntry(placeholder_text="Confirm Master Password", show_peek_icon=True)
        self.confirm_pwd_entry.connect("activate", lambda _: self._on_auth_submit())
        center_box.append(self.confirm_pwd_entry)

        # Error label
        self.auth_error_label = Gtk.Label(label="", wrap=True)
        self.auth_error_label.add_css_class("error")
        center_box.append(self.auth_error_label)

        # Action Button
        self.auth_btn = Gtk.Button(label="Unlock Diary")
        self.auth_btn.add_css_class("suggested-action")
        self.auth_btn.add_css_class("pill")
        self.auth_btn.connect("clicked", lambda _: self._on_auth_submit())
        center_box.append(self.auth_btn)

        scrolled.set_child(center_box)
        return scrolled

    def show_auth_view(self):
        """Configure auth screen according to whether vault exists."""
        vault_exists = self.vault.exists()
        self.pwd_entry.set_text("")
        self.confirm_pwd_entry.set_text("")
        self.auth_error_label.set_text("")

        if vault_exists:
            self.auth_title.set_text("Unlock Your Diary")
            self.auth_subtitle.set_text("Enter your master password to decrypt your entries")
            self.confirm_pwd_entry.set_visible(False)
            self.auth_btn.set_label("Unlock Diary")
        else:
            self.auth_title.set_text("Create Secure Diary")
            self.auth_subtitle.set_text(
                "Set a master password. Your diary entries will be encrypted with AES-256 "
                "and stored locally. There is no cloud recovery."
            )
            self.confirm_pwd_entry.set_visible(True)
            self.auth_btn.set_label("Create Encrypted Diary")

        self.main_stack.set_visible_child_name("auth")
        self.pwd_entry.grab_focus()

    def _on_auth_submit(self):
        password = self.pwd_entry.get_text()
        self.auth_error_label.set_text("")

        if not password:
            self.auth_error_label.set_text("Password cannot be empty.")
            return

        if not self.vault.exists():
            # Setup mode
            confirm = self.confirm_pwd_entry.get_text()
            if len(password) < 8:
                self.auth_error_label.set_text("Password must be at least 8 characters long.")
                return
            if password != confirm:
                self.auth_error_label.set_text("Passwords do not match.")
                return

            try:
                self.vault.initialize_vault(password)
                self._on_unlocked_success()
            except Exception as e:
                self.auth_error_label.set_text(f"Initialization error: {e}")
        else:
            # Unlock mode
            try:
                self.vault.unlock(password)
                self._on_unlocked_success()
            except InvalidPasswordError:
                self.auth_error_label.set_text("Incorrect master password. Please try again.")
            except Exception as e:
                self.auth_error_label.set_text(f"Unlock error: {e}")

    def _on_unlocked_success(self):
        self.last_user_activity = time.time()
        self.main_stack.set_visible_child_name("diary")
        self._refresh_entries_list()
        self.jump_to_date(datetime.date.today().isoformat())

    def lock_diary(self):
        """Lock the vault and return to unlock screen."""
        if self.is_dirty:
            self._save_current_entry()
        self.vault.lock()
        self.show_auth_view()

    # -------------------------------------------------------------------------
    # Main Diary View
    # -------------------------------------------------------------------------
    def _build_diary_view(self) -> Gtk.Widget:
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # HeaderBar
        header = Adw.HeaderBar()
        root_box.append(header)

        # Left Header Controls: Today, Prev/Next day
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        btn_today = Gtk.Button(label="Today")
        btn_today.set_tooltip_text("Jump to Today (Ctrl+T)")
        btn_today.connect("clicked", lambda _: self.jump_to_date(datetime.date.today().isoformat()))
        left_box.append(btn_today)

        btn_prev = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        btn_prev.set_tooltip_text("Previous Day")
        btn_prev.connect("clicked", lambda _: self._navigate_day(-1))
        left_box.append(btn_prev)

        btn_next = Gtk.Button.new_from_icon_name("go-next-symbolic")
        btn_next.set_tooltip_text("Next Day")
        btn_next.connect("clicked", lambda _: self._navigate_day(1))
        left_box.append(btn_next)

        header.pack_start(left_box)

        # Title: Current formatted date
        self.header_title = Adw.WindowTitle(
            title="Secure Daily Diary",
            subtitle=datetime.date.today().strftime("%A, %B %d, %Y")
        )
        header.set_title_widget(self.header_title)

        # Right Header Controls: Save status, Save btn, Lock, Menu
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.save_status_label = Gtk.Label(label="Saved ✓")
        self.save_status_label.add_css_class("badge-saved")
        right_box.append(self.save_status_label)

        btn_save = Gtk.Button.new_from_icon_name("document-save-symbolic")
        btn_save.set_tooltip_text("Save Entry (Ctrl+S)")
        btn_save.connect("clicked", lambda _: self._save_current_entry())
        right_box.append(btn_save)

        btn_lock = Gtk.Button.new_from_icon_name("system-lock-screen-symbolic")
        btn_lock.set_tooltip_text("Lock Diary (Ctrl+L)")
        btn_lock.connect("clicked", lambda _: self.lock_diary())
        right_box.append(btn_lock)

        # Menu Button
        menu_btn = self._build_app_menu()
        right_box.append(menu_btn)

        header.pack_end(right_box)

        # Split Paned: Sidebar + Editor
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(330)
        paned.set_vexpand(True)

        sidebar = self._build_sidebar()
        editor = self._build_editor()

        paned.set_start_child(sidebar)
        paned.set_end_child(editor)

        root_box.append(paned)
        return root_box

    def _build_app_menu(self) -> Gtk.MenuButton:
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        
        popover = Gtk.Popover()
        menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        menu_box.set_margin_top(8)
        menu_box.set_margin_bottom(8)
        menu_box.set_margin_start(8)
        menu_box.set_margin_end(8)

        # Change Password
        btn_ch_pwd = Gtk.Button(label="Change Password...")
        btn_ch_pwd.connect("clicked", lambda b: [popover.popdown(), self._show_change_password_dialog()])
        menu_box.append(btn_ch_pwd)

        # Export Markdown
        btn_export = Gtk.Button(label="Export to Markdown...")
        btn_export.connect("clicked", lambda b: [popover.popdown(), self._show_export_dialog()])
        menu_box.append(btn_export)

        # Auto-Lock Settings
        btn_autolock = Gtk.Button(label="Auto-Lock Timer...")
        btn_autolock.connect("clicked", lambda b: [popover.popdown(), self._show_autolock_dialog()])
        menu_box.append(btn_autolock)

        # About
        btn_about = Gtk.Button(label="About Secure Diary")
        btn_about.connect("clicked", lambda b: [popover.popdown(), self._show_about_dialog()])
        menu_box.append(btn_about)

        popover.set_child(menu_box)
        menu_button.set_popover(popover)
        return menu_button

    # -------------------------------------------------------------------------
    # Sidebar: Calendar + Search + Entries List
    # -------------------------------------------------------------------------
    def _build_sidebar(self) -> Gtk.Widget:
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar_box.add_css_class("sidebar-box")
        sidebar_box.set_margin_start(8)
        sidebar_box.set_margin_end(8)
        sidebar_box.set_margin_top(8)
        sidebar_box.set_margin_bottom(8)

        # Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search diary entries...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        sidebar_box.append(self.search_entry)

        # Calendar Widget
        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected", self._on_calendar_day_selected)
        sidebar_box.append(self.calendar)

        # Entries List Header
        list_header = Gtk.Label(label="Recent Journal Entries", halign=Gtk.Align.START)
        list_header.add_css_class("heading")
        sidebar_box.append(list_header)

        # Scrolled Entries ListBox
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.entries_listbox = Gtk.ListBox()
        self.entries_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.entries_listbox.connect("row-selected", self._on_entry_row_selected)
        scrolled.set_child(self.entries_listbox)
        sidebar_box.append(scrolled)

        return sidebar_box

    def _refresh_entries_list(self, query: str = ""):
        """Populate the sidebar entries list box."""
        # Clear existing rows
        while child := self.entries_listbox.get_first_child():
            self.entries_listbox.remove(child)

        if not self.vault.is_unlocked:
            return

        entries = self.vault.search_entries(query) if query else self.vault.get_all_entries()

        for entry in entries:
            row = Gtk.ListBoxRow()
            row.add_css_class("entry-list-item")
            row._date_str = entry.get("date", "")

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            
            # Top row: Mood + Date + Title
            top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            mood = entry.get("mood", "")
            if mood:
                mood_lbl = Gtk.Label(label=mood)
                top_box.append(mood_lbl)

            date_str = entry.get("date", "")
            try:
                dt = datetime.date.fromisoformat(date_str)
                fmt_date = dt.strftime("%b %d, %Y")
            except Exception:
                fmt_date = date_str

            date_lbl = Gtk.Label(label=fmt_date, halign=Gtk.Align.START)
            date_lbl.add_css_class("entry-date-label")
            top_box.append(date_lbl)

            title = entry.get("title", "")
            if title:
                title_lbl = Gtk.Label(label=f"— {title}", halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.END)
                top_box.append(title_lbl)

            box.append(top_box)

            # Snippet preview
            content = entry.get("content", "").strip().replace("\n", " ")
            snippet = (content[:60] + "...") if len(content) > 60 else content
            if snippet:
                snip_lbl = Gtk.Label(label=snippet, halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.END)
                snip_lbl.add_css_class("entry-snippet-label")
                box.append(snip_lbl)

            row.set_child(box)
            self.entries_listbox.append(row)

    def _on_search_changed(self, entry: Gtk.SearchEntry):
        query = entry.get_text()
        self._refresh_entries_list(query)

    def _on_calendar_day_selected(self, cal: Gtk.Calendar):
        dt = cal.get_date()
        date_str = dt.format("%Y-%m-%d")
        if date_str != self.current_date:
            self.jump_to_date(date_str)

    def _on_entry_row_selected(self, listbox: Gtk.ListBox, row: Optional[Gtk.ListBoxRow]):
        if row and hasattr(row, "_date_str"):
            self.jump_to_date(row._date_str)

    # -------------------------------------------------------------------------
    # Editor Pane
    # -------------------------------------------------------------------------
    def _build_editor(self) -> Gtk.Widget:
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        editor_box.set_margin_start(16)
        editor_box.set_margin_end(16)
        editor_box.set_margin_top(12)
        editor_box.set_margin_bottom(12)

        # Title entry
        self.title_entry = Gtk.Entry()
        self.title_entry.set_placeholder_text("Entry Title (e.g. Daily Highlights, Goals, Reflections)")
        self.title_entry.add_css_class("editor-title")
        self.title_entry.connect("changed", self._on_editor_modified)
        editor_box.append(self.title_entry)

        # Mood & Tags row
        meta_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Mood Selector Buttons
        mood_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.mood_buttons: Dict[str, Gtk.Button] = {}

        for emoji, label in MOOD_OPTIONS:
            btn = Gtk.Button(label=emoji)
            btn.set_tooltip_text(label)
            btn.add_css_class("mood-btn")
            btn.connect("clicked", lambda b, e=emoji: self._set_mood(e))
            mood_box.append(btn)
            self.mood_buttons[emoji] = btn

        meta_row.append(mood_box)

        # Tags Entry
        self.tags_entry = Gtk.Entry()
        self.tags_entry.set_hexpand(True)
        self.tags_entry.set_placeholder_text("Tags: #work, #health, #ideas")
        self.tags_entry.add_css_class("editor-tags")
        self.tags_entry.connect("changed", self._on_editor_modified)
        meta_row.append(self.tags_entry)

        editor_box.append(meta_row)

        # Markdown Formatting Toolbar
        toolbar = self._build_formatting_toolbar()
        editor_box.append(toolbar)

        # Text View Area
        scrolled_text = Gtk.ScrolledWindow()
        scrolled_text.set_vexpand(True)
        scrolled_text.set_hexpand(True)

        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.add_css_class("diary-text-view")
        self.text_view.set_left_margin(16)
        self.text_view.set_right_margin(16)
        self.text_view.set_top_margin(16)
        self.text_view.set_bottom_margin(16)

        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.connect("changed", self._on_text_buffer_changed)

        scrolled_text.set_child(self.text_view)
        editor_box.append(scrolled_text)

        # Footer Status: Word Count + Delete Entry
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.word_count_label = Gtk.Label(label="0 words | 0 characters", halign=Gtk.Align.START)
        self.word_count_label.add_css_class("dim-label")
        footer_box.append(self.word_count_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        footer_box.append(spacer)

        btn_delete = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        btn_delete.set_tooltip_text("Delete entry for this day")
        btn_delete.add_css_class("destructive-action")
        btn_delete.connect("clicked", lambda _: self._confirm_delete_entry())
        footer_box.append(btn_delete)

        editor_box.append(footer_box)

        return editor_box

    def _build_formatting_toolbar(self) -> Gtk.Widget:
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        actions = [
            ("Bold", "**", "**", "format-text-bold-symbolic"),
            ("Italic", "*", "*", "format-text-italic-symbolic"),
            ("Heading 1", "# ", "", "format-text-larger-symbolic"),
            ("Heading 2", "## ", "", None),
            ("Bullet List", "- ", "", "view-list-bullet-symbolic"),
            ("Checklist", "- [ ] ", "", None),
            ("Quote", "> ", "", None),
            ("Code", "```\n", "\n```", "format-text-code-symbolic"),
        ]

        for label, prefix, suffix, icon_name in actions:
            if icon_name:
                btn = Gtk.Button.new_from_icon_name(icon_name)
            else:
                btn = Gtk.Button(label=label)
            btn.set_tooltip_text(label)
            btn.add_css_class("toolbar-btn")
            btn.connect("clicked", lambda b, p=prefix, s=suffix: self._insert_format(p, s))
            toolbar.append(btn)

        # Timestamp insertion button
        btn_time = Gtk.Button(label="🕒 Time")
        btn_time.set_tooltip_text("Insert current timestamp")
        btn_time.add_css_class("toolbar-btn")
        btn_time.connect(
            "clicked",
            lambda _: self._insert_format(f"\n**{datetime.datetime.now().strftime('%H:%M')}** - ", "")
        )
        toolbar.append(btn_time)

        return toolbar

    def _insert_format(self, prefix: str, suffix: str):
        buf = self.text_buffer
        if buf.get_has_selection():
            start, end = buf.get_selection_bounds()
            selected_text = buf.get_text(start, end, True)
            replacement = f"{prefix}{selected_text}{suffix}"
            buf.delete(start, end)
            buf.insert(start, replacement)
        else:
            insert_iter = buf.get_iter_at_mark(buf.get_insert())
            buf.insert(insert_iter, f"{prefix}{suffix}")
            if suffix:
                insert_iter.backward_chars(len(suffix))
                buf.place_cursor(insert_iter)
        self.text_view.grab_focus()

    def _set_mood(self, emoji: str):
        if self.current_mood == emoji:
            self.current_mood = ""  # toggle off
        else:
            self.current_mood = emoji

        for e, btn in self.mood_buttons.items():
            if e == self.current_mood:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")

        self._on_editor_modified()

    def _on_editor_modified(self, *args):
        self.is_dirty = True
        self.save_status_label.set_text("Unsaved changes •")
        self.save_status_label.remove_css_class("badge-saved")
        self.save_status_label.add_css_class("badge-unsaved")

        # Debounced auto-save (1.5 seconds)
        if self.auto_save_timeout_id is not None:
            GLib.source_remove(self.auto_save_timeout_id)
        self.auto_save_timeout_id = GLib.timeout_add_seconds(2, self._debounced_auto_save)

    def _debounced_auto_save(self) -> bool:
        self.auto_save_timeout_id = None
        if self.is_dirty and self.vault.is_unlocked:
            self._save_current_entry()
        return False

    def _on_text_buffer_changed(self, buf: Gtk.TextBuffer):
        self._update_word_count()
        self._on_editor_modified()

    def _update_word_count(self):
        start = self.text_buffer.get_start_iter()
        end = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_text(start, end, True)
        
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.word_count_label.set_text(f"{words} words | {chars} characters")

    # -------------------------------------------------------------------------
    # Navigation & Persistence
    # -------------------------------------------------------------------------
    def jump_to_date(self, date_str: str):
        """Navigate to a specific date and load its entry."""
        if self.is_dirty:
            self._save_current_entry()

        self.current_date = date_str

        # Update Header Title
        try:
            dt = datetime.date.fromisoformat(date_str)
            title_text = dt.strftime("%A, %B %d, %Y")
            self.header_title.set_subtitle(title_text)
            
            # Sync calendar widget
            g_dt = GLib.DateTime.new_local(dt.year, dt.month, dt.day, 12, 0, 0)
            self.calendar.set_date(g_dt)
        except Exception:
            self.header_title.set_subtitle(date_str)

        # Load entry from vault
        entry = self.vault.get_entry(date_str)
        self._load_entry_into_editor(entry)

    def _navigate_day(self, delta_days: int):
        try:
            dt = datetime.date.fromisoformat(self.current_date)
            new_dt = dt + datetime.timedelta(days=delta_days)
            self.jump_to_date(new_dt.isoformat())
        except Exception:
            pass

    def _load_entry_into_editor(self, entry: Optional[Dict[str, Any]]):
        # Temporarily block change handlers while setting values
        self.title_entry.handler_block_by_func(self._on_editor_modified)
        self.tags_entry.handler_block_by_func(self._on_editor_modified)
        self.text_buffer.handler_block_by_func(self._on_text_buffer_changed)

        if entry:
            self.title_entry.set_text(entry.get("title", ""))
            tags = entry.get("tags", [])
            self.tags_entry.set_text(", ".join(tags))
            self.text_buffer.set_text(entry.get("content", ""))
            self._set_mood(entry.get("mood", ""))
        else:
            self.title_entry.set_text("")
            self.tags_entry.set_text("")
            self.text_buffer.set_text("")
            self._set_mood("")

        self.title_entry.handler_unblock_by_func(self._on_editor_modified)
        self.tags_entry.handler_unblock_by_func(self._on_editor_modified)
        self.text_buffer.handler_unblock_by_func(self._on_text_buffer_changed)

        self.is_dirty = False
        self.save_status_label.set_text("Saved ✓")
        self.save_status_label.remove_css_class("badge-unsaved")
        self.save_status_label.add_css_class("badge-saved")
        self._update_word_count()

    def _save_current_entry(self):
        if not self.vault.is_unlocked:
            return

        start = self.text_buffer.get_start_iter()
        end = self.text_buffer.get_end_iter()
        content = self.text_buffer.get_text(start, end, True)
        title = self.title_entry.get_text().strip()
        tags_raw = self.tags_entry.get_text()
        tags = [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()]

        # If everything is empty and entry didn't exist, skip saving empty shell
        existing = self.vault.get_entry(self.current_date)
        if not content.strip() and not title and not self.current_mood and not tags and not existing:
            self.is_dirty = False
            self.save_status_label.set_text("Empty")
            return

        self.vault.save_entry(
            date_str=self.current_date,
            title=title,
            content=content,
            mood=self.current_mood,
            tags=tags,
        )

        self.is_dirty = False
        self.save_status_label.set_text("Saved ✓")
        self.save_status_label.remove_css_class("badge-unsaved")
        self.save_status_label.add_css_class("badge-saved")
        self._refresh_entries_list(self.search_entry.get_text())

    def _confirm_delete_entry(self):
        if not self.vault.get_entry(self.current_date):
            return

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Delete Diary Entry?",
            body=f"Are you sure you want to delete the entry for {self.current_date}? This cannot be undone.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dlg, response_id):
            if response_id == "delete":
                self.vault.delete_entry(self.current_date)
                self.jump_to_date(self.current_date)
                self._refresh_entries_list()

        dialog.connect("response", on_response)
        dialog.present()

    # -------------------------------------------------------------------------
    # Dialogs: Password Change, Export, Settings, About
    # -------------------------------------------------------------------------
    def _show_change_password_dialog(self):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Change Master Password",
            body="Re-encrypts all journal entries with a new master password.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("change", "Change Password")
        dialog.set_response_appearance("change", Adw.ResponseAppearance.SUGGESTED)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(8)

        old_pwd = Gtk.PasswordEntry(placeholder_text="Current Master Password", show_peek_icon=True)
        box.append(old_pwd)

        new_pwd = Gtk.PasswordEntry(placeholder_text="New Master Password", show_peek_icon=True)
        box.append(new_pwd)

        confirm_pwd = Gtk.PasswordEntry(placeholder_text="Confirm New Master Password", show_peek_icon=True)
        box.append(confirm_pwd)

        err_label = Gtk.Label(label="", wrap=True)
        err_label.add_css_class("error")
        box.append(err_label)

        dialog.set_extra_child(box)

        def on_response(dlg, resp):
            if resp != "change":
                return
            if len(new_pwd.get_text()) < 8:
                err_label.set_text("New password must be at least 8 characters.")
                return
            if new_pwd.get_text() != confirm_pwd.get_text():
                err_label.set_text("New passwords do not match.")
                return

            try:
                self.vault.change_password(old_pwd.get_text(), new_pwd.get_text())
                dlg.close()
                self._show_info_dialog("Password Changed", "Your master password has been successfully updated.")
            except InvalidPasswordError:
                err_label.set_text("Current master password is incorrect.")
            except Exception as e:
                err_label.set_text(f"Error: {e}")

        dialog.connect("response", on_response)
        dialog.present()

    def _show_export_dialog(self):
        default_export_dir = Path.home() / "Documents"
        default_export_dir.mkdir(parents=True, exist_ok=True)
        default_export_path = default_export_dir / f"diary_export_{datetime.date.today().isoformat()}.md"

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Export Decrypted Diary",
            body=f"Export all entries to a clean Markdown file.\n\nFile will be saved to:\n{default_export_path}",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("export", "Export Now")
        dialog.set_response_appearance("export", Adw.ResponseAppearance.SUGGESTED)

        def on_response(dlg, resp):
            if resp == "export":
                try:
                    count = self.vault.export_to_markdown(default_export_path)
                    self._show_info_dialog(
                        "Export Complete",
                        f"Successfully exported {count} entries to:\n{default_export_path}"
                    )
                except Exception as e:
                    self._show_info_dialog("Export Failed", f"Failed to export: {e}")

        dialog.connect("response", on_response)
        dialog.present()

    def _show_autolock_dialog(self):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Auto-Lock Timer",
            body="Automatically lock the diary after a period of inactivity to protect your privacy.",
        )
        dialog.add_response("close", "Save & Close")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(16)
        box.set_margin_end(16)

        # Options: 1, 5, 15, 30, Never (0)
        options = [("1", "1 Minute"), ("5", "5 Minutes"), ("15", "15 Minutes"), ("30", "30 Minutes"), ("0", "Never")]
        dropdown = Gtk.DropDown.new_from_strings([lbl for _, lbl in options])
        
        current_val = str(self.auto_lock_minutes)
        for idx, (val, _) in enumerate(options):
            if val == current_val:
                dropdown.set_selected(idx)
                break

        box.append(dropdown)
        dialog.set_extra_child(box)

        def on_response(dlg, resp):
            selected_idx = dropdown.get_selected()
            selected_val = int(options[selected_idx][0])
            self.auto_lock_minutes = selected_val
            self.vault.set_setting("auto_lock_minutes", str(selected_val))

        dialog.connect("response", on_response)
        dialog.present()

    def _show_about_dialog(self):
        dialog = Adw.AboutWindow(
            transient_for=self,
            application_name="Secure Daily Diary",
            version="1.0",
            developer_name="Antigravity Pair Programmer",
            comments="A private, encrypted daily diary. Data is protected with AES-256-GCM and stored 100% locally.",
            website="https://github.com",
            issue_url="https://github.com",
            license_type=Gtk.License.MIT_X11,
        )
        dialog.present()

    def _show_info_dialog(self, title: str, message: str):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=title,
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.present()


def main(db_path: Optional[Path | str] = None):
    app = DiaryApplication(db_path)
    return app.run(sys.argv[:1])


if __name__ == "__main__":
    main()
