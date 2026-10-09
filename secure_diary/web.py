"""
web.py - Localhost Web Application for Secure Daily Diary

Runs a local HTTP server bound strictly to 127.0.0.1.
Zero external dependencies, works in any modern browser.
Provides complete feature parity with the desktop application:
- AES-256-GCM encrypted local storage
- Master password protection & first-run setup
- Calendar navigation & daily entry editing
- Live full-text search across entries
- Mood tracking & tag management
- Auto-save & idle auto-lock
- Change password & Markdown export
"""

from __future__ import annotations

import datetime
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from .vault import (
    DiaryVault,
    DiaryVaultError,
    InvalidPasswordError,
    VaultAlreadyExistsError,
    VaultLockedError,
    get_default_vault_path,
)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Secure Daily Diary</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent: #10b981;
      --danger: #ef4444;
      --input-bg: #0f172a;
      --input-border: #475569;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }

    /* Header */
    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--card-border);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .logo-area { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.1rem; }
    .logo-icon { font-size: 1.4rem; }
    .header-nav { display: flex; align-items: center; gap: 8px; }
    .btn {
      background: var(--card-bg);
      color: var(--text);
      border: 1px solid var(--input-border);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn:hover { background: #334155; border-color: #64748b; }
    .btn-primary { background: var(--primary); border-color: var(--primary); color: white; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-danger { background: rgba(239, 68, 68, 0.15); border-color: var(--danger); color: #fca5a5; }
    .btn-danger:hover { background: var(--danger); color: white; }
    .save-indicator { font-size: 0.85rem; color: var(--accent); font-weight: 600; display: flex; align-items: center; gap: 4px; }
    .save-indicator.unsaved { color: #f59e0b; }

    /* Main Container */
    .app-layout {
      display: flex;
      flex: 1;
      height: calc(100vh - 61px);
      overflow: hidden;
    }

    /* Sidebar */
    aside {
      width: 320px;
      background: #182234;
      border-right: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 16px;
      overflow-y: auto;
    }
    .search-box input {
      width: 100%;
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.9rem;
    }
    .date-nav-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .date-picker-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
    }
    .date-picker-row input[type="date"] {
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      color: var(--text);
      padding: 6px 8px;
      border-radius: 6px;
      font-size: 0.9rem;
      flex: 1;
      color-scheme: dark;
    }
    .entries-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      overflow-y: auto;
      flex: 1;
    }
    .entry-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .entry-card:hover { border-color: var(--primary); transform: translateY(-1px); }
    .entry-card.active { border-color: var(--primary); background: #1e3a8a33; }
    .entry-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
    .entry-card-date { font-weight: 600; font-size: 0.85rem; color: #93c5fd; }
    .entry-card-title { font-weight: 500; font-size: 0.9rem; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .entry-card-snippet { font-size: 0.8rem; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* Editor Main */
    main {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 20px 32px;
      overflow-y: auto;
      gap: 12px;
    }
    .date-heading-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 8px;
    }
    .date-heading { font-size: 1.6rem; font-weight: 700; color: var(--text); }
    .title-input {
      background: var(--card-bg);
      border: 1px solid var(--input-border);
      color: var(--text);
      font-size: 1.15rem;
      font-weight: 600;
      padding: 8px 14px;
      border-radius: 8px;
      width: 100%;
    }
    .meta-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .mood-selector { display: flex; gap: 4px; }
    .mood-btn {
      background: var(--card-bg);
      border: 1px solid var(--input-border);
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 1.1rem;
      cursor: pointer;
      transition: all 0.15s;
    }
    .mood-btn:hover { background: #334155; }
    .mood-btn.active { background: #2563eb; border-color: #60a5fa; transform: scale(1.1); }
    .tags-input {
      flex: 1;
      min-width: 200px;
      background: var(--card-bg);
      border: 1px solid var(--input-border);
      color: var(--text);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.9rem;
    }

    /* Toolbar */
    .editor-toolbar {
      display: flex;
      gap: 4px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      padding: 4px 8px;
      border-radius: 6px;
      align-items: center;
    }
    .tool-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
    }
    .tool-btn:hover { background: #334155; color: var(--text); }

    /* Content Textarea */
    .editor-textarea {
      flex: 1;
      min-height: 380px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      color: var(--text);
      font-size: 1rem;
      line-height: 1.6;
      padding: 16px;
      resize: none;
      outline: none;
    }
    .editor-textarea:focus { border-color: var(--primary); }

    .editor-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 0.85rem;
    }

    /* Auth Modal Screen */
    .auth-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }
    .auth-modal {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 32px;
      width: 420px;
      max-width: 90vw;
      box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .auth-modal h2 { font-size: 1.4rem; font-weight: 700; text-align: center; }
    .auth-modal p { font-size: 0.9rem; color: var(--text-muted); text-align: center; line-height: 1.4; }
    .auth-modal input {
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 1rem;
      width: 100%;
    }
    .error-msg { color: var(--danger); font-size: 0.85rem; text-align: center; }

    /* Modal Backdrop for Dialogs */
    .dialog-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 90;
    }
    .dialog-overlay.active { display: flex; }
  </style>
</head>
<body>

  <!-- Authentication Overlay -->
  <div class="auth-overlay" id="authOverlay">
    <div class="auth-modal">
      <div style="font-size: 3rem; text-align: center;">🔐</div>
      <h2 id="authHeading">Unlock Secure Diary</h2>
      <p id="authSubheading">Enter your master password to decrypt your journal.</p>

      <input type="password" id="masterPasswordInput" placeholder="Master Password" autofocus />
      <input type="password" id="confirmPasswordInput" placeholder="Confirm Password" style="display:none;" />
      
      <div class="error-msg" id="authErrorMsg"></div>

      <button class="btn btn-primary" style="justify-content: center; padding: 10px;" id="authSubmitBtn">
        Unlock Diary
      </button>
    </div>
  </div>

  <!-- Main App Header -->
  <header>
    <div class="logo-area">
      <span class="logo-icon">📖</span>
      <span>Secure Daily Diary</span>
    </div>

    <div class="header-nav">
      <button class="btn" id="btnPrevDay" title="Previous Day">◀</button>
      <button class="btn" id="btnToday">Today</button>
      <button class="btn" id="btnNextDay" title="Next Day">▶</button>
    </div>

    <div style="display: flex; align-items: center; gap: 12px;">
      <span class="save-indicator" id="saveIndicator">Saved ✓</span>
      <button class="btn" id="btnExport" title="Export Journal">Export</button>
      <button class="btn" id="btnChangePassword" title="Change Password">Password</button>
      <button class="btn btn-danger" id="btnLock" title="Lock Diary">Lock 🔒</button>
    </div>
  </header>

  <!-- Layout -->
  <div class="app-layout">
    <!-- Sidebar -->
    <aside>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="🔍 Search entries..." />
      </div>

      <div class="date-nav-card">
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">CALENDAR JUMP</span>
        <div class="date-picker-row">
          <input type="date" id="datePicker" />
        </div>
      </div>

      <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-top: 4px;">RECENT ENTRIES</span>
      <div class="entries-list" id="entriesList">
        <!-- populated dynamically -->
      </div>
    </aside>

    <!-- Main Editor -->
    <main>
      <div class="date-heading-row">
        <div class="date-heading" id="dateHeading">Loading date...</div>
      </div>

      <input type="text" class="title-input" id="titleInput" placeholder="Entry Title (optional)" />

      <div class="meta-bar">
        <div class="mood-selector" id="moodSelector">
          <button class="mood-btn" data-mood="😊" title="Happy">😊</button>
          <button class="mood-btn" data-mood="😌" title="Calm">😌</button>
          <button class="mood-btn" data-mood="💡" title="Inspired">💡</button>
          <button class="mood-btn" data-mood="⚡" title="Productive">⚡</button>
          <button class="mood-btn" data-mood="💖" title="Grateful">💖</button>
          <button class="mood-btn" data-mood="🧘" title="Reflective">🧘</button>
          <button class="mood-btn" data-mood="😴" title="Tired">😴</button>
          <button class="mood-btn" data-mood="🌧️" title="Down">🌧️</button>
        </div>

        <input type="text" class="tags-input" id="tagsInput" placeholder="Tags: #journal, #work, #ideas" />
      </div>

      <!-- Formatting Toolbar -->
      <div class="editor-toolbar">
        <button class="tool-btn" onclick="insertFormat('**', '**')">B</button>
        <button class="tool-btn" onclick="insertFormat('*', '*')">I</button>
        <button class="tool-btn" onclick="insertFormat('# ', '')">H1</button>
        <button class="tool-btn" onclick="insertFormat('## ', '')">H2</button>
        <button class="tool-btn" onclick="insertFormat('- ', '')">• List</button>
        <button class="tool-btn" onclick="insertFormat('- [ ] ', '')">☑ Check</button>
        <button class="tool-btn" onclick="insertFormat('> ', '')">“ Quote</button>
        <button class="tool-btn" onclick="insertFormat('```\n', '\n```')">{ } Code</button>
        <button class="tool-btn" onclick="insertTimestamp()">🕒 Time</button>
      </div>

      <!-- Editor Content -->
      <textarea class="editor-textarea" id="contentInput" placeholder="What's on your mind today? Write freely—all entries are encrypted locally with AES-256-GCM."></textarea>

      <!-- Footer Info -->
      <div class="editor-footer">
        <span id="wordCountLabel">0 words | 0 characters</span>
        <button class="btn btn-danger" style="padding: 4px 10px; font-size: 0.8rem;" id="btnDeleteEntry">Delete Entry</button>
      </div>
    </main>
  </div>

  <!-- Change Password Dialog -->
  <div class="dialog-overlay" id="changePasswordDialog">
    <div class="auth-modal">
      <h2>Change Master Password</h2>
      <p>Re-encrypts all entries with a new master key.</p>
      <input type="password" id="oldPwdInput" placeholder="Current Master Password" />
      <input type="password" id="newPwdInput" placeholder="New Master Password (min 8 chars)" />
      <input type="password" id="confirmNewPwdInput" placeholder="Confirm New Password" />
      <div class="error-msg" id="changePwdError"></div>
      <div style="display:flex; justify-content: flex-end; gap: 8px;">
        <button class="btn" onclick="closeDialog('changePasswordDialog')">Cancel</button>
        <button class="btn btn-primary" id="btnSubmitChangePwd">Save New Password</button>
      </div>
    </div>
  </div>

  <script>
    let currentDate = new Date().toISOString().split('T')[0];
    let currentMood = '';
    let isDirty = false;
    let autoSaveTimer = null;
    let sessionToken = '';
    let lastActivityTime = Date.now();

    // Elements
    const authOverlay = document.getElementById('authOverlay');
    const masterPasswordInput = document.getElementById('masterPasswordInput');
    const confirmPasswordInput = document.getElementById('confirmPasswordInput');
    const authErrorMsg = document.getElementById('authErrorMsg');
    const authSubmitBtn = document.getElementById('authSubmitBtn');
    const datePicker = document.getElementById('datePicker');
    const dateHeading = document.getElementById('dateHeading');
    const titleInput = document.getElementById('titleInput');
    const tagsInput = document.getElementById('tagsInput');
    const contentInput = document.getElementById('contentInput');
    const wordCountLabel = document.getElementById('wordCountLabel');
    const saveIndicator = document.getElementById('saveIndicator');
    const entriesList = document.getElementById('entriesList');
    const searchInput = document.getElementById('searchInput');

    // Idle monitoring
    ['mousemove', 'keydown', 'click'].forEach(evt => {
      window.addEventListener(evt, () => { lastActivityTime = Date.now(); });
    });
    setInterval(() => {
      if (sessionToken && (Date.now() - lastActivityTime > 5 * 60 * 1000)) {
        lockDiary();
      }
    }, 15000);

    // Initial check
    async function checkStatus() {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (!data.exists) {
        document.getElementById('authHeading').innerText = 'Create Secure Diary';
        document.getElementById('authSubheading').innerText = 'Set a master password. Data will be encrypted with AES-256 locally.';
        confirmPasswordInput.style.display = 'block';
        authSubmitBtn.innerText = 'Create Encrypted Vault';
      }
      datePicker.value = currentDate;
      updateDateHeading(currentDate);
    }
    checkStatus();

    // Auth submit
    authSubmitBtn.addEventListener('click', async () => {
      const password = masterPasswordInput.value;
      const confirm = confirmPasswordInput.value;
      authErrorMsg.innerText = '';

      if (!password) {
        authErrorMsg.innerText = 'Password cannot be empty.';
        return;
      }

      if (confirmPasswordInput.style.display !== 'none') {
        if (password.length < 8) {
          authErrorMsg.innerText = 'Password must be at least 8 characters.';
          return;
        }
        if (password !== confirm) {
          authErrorMsg.innerText = 'Passwords do not match.';
          return;
        }
        const res = await fetch('/api/init', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        });
        const data = await res.json();
        if (data.success) {
          sessionToken = data.token;
          authOverlay.style.display = 'none';
          loadEntriesList();
          loadEntry(currentDate);
        } else {
          authErrorMsg.innerText = data.error || 'Failed to initialize.';
        }
      } else {
        const res = await fetch('/api/unlock', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        });
        const data = await res.json();
        if (data.success) {
          sessionToken = data.token;
          authOverlay.style.display = 'none';
          loadEntriesList();
          loadEntry(currentDate);
        } else {
          authErrorMsg.innerText = 'Incorrect master password.';
        }
      }
    });

    masterPasswordInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') authSubmitBtn.click();
    });
    confirmPasswordInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') authSubmitBtn.click();
    });

    // Date formatting
    function updateDateHeading(dateStr) {
      const d = new Date(dateStr + 'T00:00:00');
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      dateHeading.innerText = d.toLocaleDateString(undefined, options);
    }

    // Load entry
    async function loadEntry(dateStr) {
      currentDate = dateStr;
      datePicker.value = dateStr;
      updateDateHeading(dateStr);

      const res = await fetch(`/api/entry?date=${dateStr}&token=${sessionToken}`);
      const data = await res.json();
      const entry = data.entry;

      titleInput.value = entry ? (entry.title || '') : '';
      tagsInput.value = entry ? (entry.tags ? entry.tags.join(', ') : '') : '';
      contentInput.value = entry ? (entry.content || '') : '';
      setMood(entry ? (entry.mood || '') : '');

      isDirty = false;
      saveIndicator.innerText = 'Saved ✓';
      saveIndicator.classList.remove('unsaved');
      updateWordCount();
    }

    // Save entry
    async function saveEntry() {
      if (!sessionToken) return;
      const tags = tagsInput.value.split(',').map(t => t.trim().replace(/^#/, '')).filter(Boolean);

      const payload = {
        token: sessionToken,
        date: currentDate,
        title: titleInput.value.trim(),
        content: contentInput.value,
        mood: currentMood,
        tags: tags
      };

      const res = await fetch('/api/entry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        isDirty = false;
        saveIndicator.innerText = 'Saved ✓';
        saveIndicator.classList.remove('unsaved');
        loadEntriesList(searchInput.value);
      }
    }

    // Debounced modification
    function markDirty() {
      isDirty = true;
      saveIndicator.innerText = 'Unsaved •';
      saveIndicator.classList.add('unsaved');
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(saveEntry, 1500);
      updateWordCount();
    }

    titleInput.addEventListener('input', markDirty);
    tagsInput.addEventListener('input', markDirty);
    contentInput.addEventListener('input', markDirty);

    function updateWordCount() {
      const text = contentInput.value.trim();
      const words = text ? text.split(/\s+/).length : 0;
      const chars = text.length;
      wordCountLabel.innerText = `${words} words | ${chars} characters`;
    }

    // Mood Selector
    function setMood(emoji) {
      currentMood = (currentMood === emoji) ? '' : emoji;
      document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-mood') === currentMood);
      });
    }

    document.querySelectorAll('.mood-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        setMood(btn.getAttribute('data-mood'));
        markDirty();
      });
    });

    // Entries list
    async function loadEntriesList(query = '') {
      if (!sessionToken) return;
      const res = await fetch(`/api/entries?token=${sessionToken}&query=${encodeURIComponent(query)}`);
      const data = await res.json();
      entriesList.innerHTML = '';

      (data.entries || []).forEach(e => {
        const item = document.createElement('div');
        item.className = 'entry-card' + (e.date === currentDate ? ' active' : '');
        item.innerHTML = `
          <div class="entry-card-header">
            <span class="entry-card-date">${e.date}</span>
            <span>${e.mood || ''}</span>
          </div>
          <div class="entry-card-title">${e.title || 'Untitled'}</div>
          <div class="entry-card-snippet">${(e.content || '').replace(/\n/g, ' ')}</div>
        `;
        item.addEventListener('click', () => {
          if (isDirty) saveEntry();
          loadEntry(e.date);
        });
        entriesList.appendChild(item);
      });
    }

    searchInput.addEventListener('input', (e) => loadEntriesList(e.target.value));
    datePicker.addEventListener('change', (e) => {
      if (isDirty) saveEntry();
      loadEntry(e.target.value);
    });

    // Date nav buttons
    document.getElementById('btnToday').addEventListener('click', () => {
      if (isDirty) saveEntry();
      loadEntry(new Date().toISOString().split('T')[0]);
    });

    document.getElementById('btnPrevDay').addEventListener('click', () => {
      if (isDirty) saveEntry();
      const d = new Date(currentDate + 'T00:00:00');
      d.setDate(d.getDate() - 1);
      loadEntry(d.toISOString().split('T')[0]);
    });

    document.getElementById('btnNextDay').addEventListener('click', () => {
      if (isDirty) saveEntry();
      const d = new Date(currentDate + 'T00:00:00');
      d.setDate(d.getDate() + 1);
      loadEntry(d.toISOString().split('T')[0]);
    });

    // Formatting insertion
    function insertFormat(pre, post) {
      const start = contentInput.selectionStart;
      const end = contentInput.selectionEnd;
      const val = contentInput.value;
      const sel = val.substring(start, end);
      contentInput.value = val.substring(0, start) + pre + sel + post + val.substring(end);
      contentInput.focus();
      contentInput.setSelectionRange(start + pre.length, end + pre.length);
      markDirty();
    }

    function insertTimestamp() {
      const now = new Date();
      const timeStr = `\n**${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}** - `;
      insertFormat(timeStr, '');
    }

    // Delete entry
    document.getElementById('btnDeleteEntry').addEventListener('click', async () => {
      if (!confirm(`Delete diary entry for ${currentDate}? This cannot be undone.`)) return;
      await fetch(`/api/entry?date=${currentDate}&token=${sessionToken}`, { method: 'DELETE' });
      loadEntry(currentDate);
      loadEntriesList();
    });

    // Lock diary
    async function lockDiary() {
      if (isDirty) await saveEntry();
      await fetch(`/api/lock?token=${sessionToken}`, { method: 'POST' });
      sessionToken = '';
      masterPasswordInput.value = '';
      authOverlay.style.display = 'flex';
    }
    document.getElementById('btnLock').addEventListener('click', lockDiary);

    // Export
    document.getElementById('btnExport').addEventListener('click', () => {
      window.location.href = `/api/export?token=${sessionToken}`;
    });

    // Change Password Dialog
    document.getElementById('btnChangePassword').addEventListener('click', () => {
      document.getElementById('changePasswordDialog').classList.add('active');
    });

    function closeDialog(id) {
      document.getElementById(id).classList.remove('active');
    }

    document.getElementById('btnSubmitChangePwd').addEventListener('click', async () => {
      const oldPwd = document.getElementById('oldPwdInput').value;
      const newPwd = document.getElementById('newPwdInput').value;
      const confirmPwd = document.getElementById('confirmNewPwdInput').value;
      const err = document.getElementById('changePwdError');
      err.innerText = '';

      if (newPwd.length < 8) {
        err.innerText = 'New password must be at least 8 characters.';
        return;
      }
      if (newPwd !== confirmPwd) {
        err.innerText = 'New passwords do not match.';
        return;
      }

      const res = await fetch('/api/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: sessionToken, old_password: oldPwd, new_password: newPwd })
      });
      const data = await res.json();
      if (data.success) {
        alert('Master password changed successfully!');
        closeDialog('changePasswordDialog');
      } else {
        err.innerText = data.error || 'Failed to change password.';
      }
    });
  </script>
</body>
</html>
"""


class DiaryWebHandler(http.server.BaseHTTPRequestHandler):
    """Secure HTTP Request Handler bound strictly to localhost."""

    vault: DiaryVault
    active_tokens: Dict[str, float] = {}

    def log_message(self, format, *args):
        # Silence default HTTP access logging for privacy
        pass

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _verify_token(self, token: Optional[str]) -> bool:
        if not token or token not in self.active_tokens:
            return False
        # Update last activity
        self.active_tokens[token] = time.time()
        return self.vault.is_unlocked

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/" or parsed.path == "/index.html":
            body = HTML_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/api/status":
            self._send_json({"exists": self.vault.exists(), "unlocked": self.vault.is_unlocked})
            return

        token = params.get("token", [""])[0]
        if not self._verify_token(token):
            self._send_json({"error": "Unauthorized / Vault locked"}, 401)
            return

        if parsed.path == "/api/entry":
            date_str = params.get("date", [""])[0]
            entry = self.vault.get_entry(date_str)
            self._send_json({"entry": entry})
            return

        if parsed.path == "/api/entries":
            query = params.get("query", [""])[0]
            entries = self.vault.search_entries(query) if query else self.vault.get_all_entries()
            self._send_json({"entries": entries})
            return

        if parsed.path == "/api/export":
            # Direct download of exported markdown
            temp_export = Path("/tmp/diary_export.md")
            self.vault.export_to_markdown(temp_export)
            content = temp_export.read_bytes()
            temp_export.unlink(missing_ok=True)

            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="diary_export.md"')
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if parsed.path == "/api/init":
            password = data.get("password", "")
            try:
                self.vault.initialize_vault(password)
                token = secrets.token_hex(24)
                self.active_tokens[token] = time.time()
                self._send_json({"success": True, "token": token})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 400)
            return

        if parsed.path == "/api/unlock":
            password = data.get("password", "")
            try:
                self.vault.unlock(password)
                token = secrets.token_hex(24)
                self.active_tokens[token] = time.time()
                self._send_json({"success": True, "token": token})
            except InvalidPasswordError:
                self._send_json({"success": False, "error": "Incorrect password"}, 401)
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 500)
            return

        token = data.get("token", "")
        if not self._verify_token(token):
            self._send_json({"error": "Unauthorized"}, 401)
            return

        if parsed.path == "/api/entry":
            date_str = data.get("date", "")
            title = data.get("title", "")
            content = data.get("content", "")
            mood = data.get("mood", "")
            tags = data.get("tags", [])
            saved = self.vault.save_entry(date_str, title, content, mood, tags)
            self._send_json({"success": True, "entry": saved})
            return

        if parsed.path == "/api/lock":
            self.vault.lock()
            self.active_tokens.clear()
            self._send_json({"success": True})
            return

        if parsed.path == "/api/change_password":
            old_pwd = data.get("old_password", "")
            new_pwd = data.get("new_password", "")
            try:
                self.vault.change_password(old_pwd, new_pwd)
                self._send_json({"success": True})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 400)
            return

        self.send_error(404, "Not Found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        token = params.get("token", [""])[0]

        if not self._verify_token(token):
            self._send_json({"error": "Unauthorized"}, 401)
            return

        if parsed.path == "/api/entry":
            date_str = params.get("date", [""])[0]
            deleted = self.vault.delete_entry(date_str)
            self._send_json({"success": deleted})
            return

        self.send_error(404, "Not Found")


def start_web_server(
    db_path: Optional[Path | str] = None,
    port: int = 8765,
    open_browser: bool = True,
):
    """Start local web server on 127.0.0.1:port."""
    vault = DiaryVault(db_path)
    DiaryWebHandler.vault = vault

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), DiaryWebHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"🔒 Secure Daily Diary web server running at: {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        threading.Thread(target=lambda: (time.sleep(0.5), webbrowser.open(url)), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.shutdown()
