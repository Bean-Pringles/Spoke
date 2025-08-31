import sys
import os
import json
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem

class TabWidget(QWidget):
    """Custom tab widget with close button"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 4, 4)
        
        self.title_label = QLabel(title)
        self.title_label.setMaximumWidth(150)
        layout.addWidget(self.title_label)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0);
                color: #666;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

class BookmarksManager(QDialog):
    """Bookmarks management dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks Manager")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add Bookmark")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        
        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.load_bookmarks()
        
        layout.addLayout(toolbar)
        layout.addWidget(self.bookmarks_list)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_bookmark)
        self.edit_btn.clicked.connect(self.edit_bookmark)
        self.delete_btn.clicked.connect(self.delete_bookmark)
        
        self.setLayout(layout)
    
    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as f:
                bookmarks = json.load(f)
            for bookmark in bookmarks:
                item = QListWidgetItem(f"{bookmark['title']} - {bookmark['url']}")
                item.setData(Qt.UserRole, bookmark)
                self.bookmarks_list.addItem(item)
        except FileNotFoundError:
            pass
    
    def add_bookmark(self):
        dialog = AddBookmarkDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_bookmarks()
    
    def edit_bookmark(self):
        current = self.bookmarks_list.currentItem()
        if current:
            bookmark = current.data(Qt.UserRole)
            dialog = AddBookmarkDialog(self, bookmark)
            if dialog.exec_() == QDialog.Accepted:
                self.bookmarks_list.clear()
                self.load_bookmarks()
    
    def delete_bookmark(self):
        current = self.bookmarks_list.currentItem()
        if current:
            bookmark = current.data(Qt.UserRole)
            try:
                with open("bookmarks.json", "r") as f:
                    bookmarks = json.load(f)
                bookmarks = [b for b in bookmarks if b['url'] != bookmark['url']]
                with open("bookmarks.json", "w") as f:
                    json.dump(bookmarks, f, indent=2)
                self.bookmarks_list.clear()
                self.load_bookmarks()
            except FileNotFoundError:
                pass

class AddBookmarkDialog(QDialog):
    """Add/Edit bookmark dialog"""
    def __init__(self, parent=None, bookmark=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bookmark" if not bookmark else "Edit Bookmark")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.url_edit = QLineEdit()
        
        if bookmark:
            self.title_edit.setText(bookmark['title'])
            self.url_edit.setText(bookmark['url'])
        
        layout.addRow("Title:", self.title_edit)
        layout.addRow("URL:", self.url_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_bookmark)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def save_bookmark(self):
        title = self.title_edit.text()
        url = self.url_edit.text()
        
        if not title or not url:
            QMessageBox.warning(self, "Error", "Please fill in both fields")
            return
        
        try:
            with open("bookmarks.json", "r") as f:
                bookmarks = json.load(f)
        except FileNotFoundError:
            bookmarks = []
        
        bookmark = {"title": title, "url": url, "date_added": datetime.now().isoformat()}
        bookmarks.append(bookmark)
        
        with open("bookmarks.json", "w") as f:
            json.dump(bookmarks, f, indent=2)
        
        self.accept()

class HistoryManager(QDialog):
    """History management dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browsing History")
        self.setModal(True)
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search history...")
        search_btn = QPushButton("Search")
        clear_btn = QPushButton("Clear All History")
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        
        # History list
        self.history_list = QListWidget()
        self.load_history()
        
        layout.addLayout(search_layout)
        layout.addWidget(self.history_list)
        
        # Connect signals
        search_btn.clicked.connect(self.search_history)
        clear_btn.clicked.connect(self.clear_history)
        self.history_list.itemDoubleClicked.connect(self.open_url)
        
        self.setLayout(layout)
    
    def load_history(self):
        try:
            conn = sqlite3.connect('browser_history.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS history
                            (url TEXT, title TEXT, visit_time TEXT)''')
            cursor.execute('SELECT * FROM history ORDER BY visit_time DESC LIMIT 100')
            history = cursor.fetchall()
            conn.close()
            
            self.history_list.clear()
            for url, title, visit_time in history:
                item = QListWidgetItem(f"{title} - {url} ({visit_time})")
                item.setData(Qt.UserRole, url)
                self.history_list.addItem(item)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def search_history(self):
        search_term = self.search_edit.text().lower()
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item.setHidden(search_term not in item.text().lower())
    
    def clear_history(self):
        try:
            conn = sqlite3.connect('browser_history.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history')
            conn.commit()
            conn.close()
            self.history_list.clear()
        except Exception as e:
            print(f"Error clearing history: {e}")
    
    def open_url(self, item):
        url = item.data(Qt.UserRole)
        self.accept()
        if hasattr(self.parent(), 'navigate_to_url_direct'):
            self.parent().navigate_to_url_direct(url)

class DownloadsManager(QDialog):
    """Downloads management dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        self.downloads_list = QListWidget()
        layout.addWidget(QLabel("Recent Downloads:"))
        layout.addWidget(self.downloads_list)
        
        self.setLayout(layout)

class SettingsDialog(QDialog):
    """Settings dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Home page setting
        home_layout = QHBoxLayout()
        home_layout.addWidget(QLabel("Home Page:"))
        self.home_edit = QLineEdit("https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0")
        home_layout.addWidget(self.home_edit)
        
        # Search engine setting
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Engine:"))
        self.search_combo = QComboBox()
        self.search_combo.addItems(["Bean Engine", "Google", "DuckDuckGo", "Bing", "Yahoo"])
        search_layout.addWidget(self.search_combo)
        
        # Theme setting
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        theme_layout.addWidget(self.theme_combo)
        
        # JavaScript toggle
        self.js_check = QCheckBox("Enable JavaScript")
        self.js_check.setChecked(True)
        
        # Images toggle
        self.images_check = QCheckBox("Load Images")
        self.images_check.setChecked(True)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(home_layout)
        layout.addLayout(search_layout)
        layout.addLayout(theme_layout)
        layout.addWidget(self.js_check)
        layout.addWidget(self.images_check)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_settings(self):
        settings = {
            'home_page': self.home_edit.text(),
            'search_engine': self.search_combo.currentText(),
            'theme': self.theme_combo.currentText(),
            'javascript': self.js_check.isChecked(),
            'images': self.images_check.isChecked()
        }
        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bean Browser")
        self.setWindowIcon(QIcon())
        self.resize(1200, 800)
        
        # Initialize history database
        self.init_history_db()
        
        # Load settings
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
        # Add initial tab
        self.add_new_tab(QUrl(self.settings.get('home_page', 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0')))
        
        # Apply theme
        self.apply_theme()
    
    def init_history_db(self):
        """Initialize history database"""
        try:
            conn = sqlite3.connect('browser_history.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS history
                            (url TEXT, title TEXT, visit_time TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing history database: {e}")
    
    def load_settings(self):
        """Load application settings"""
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                'home_page': 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0',
                'search_engine': 'Google',
                'theme': 'Light',
                'javascript': True,
                'images': True
            }
    
    def setup_ui(self):
        """Setup main UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(3)
        layout.addWidget(self.progress_bar)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Downloads counter
        self.downloads_count = 0
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab(QUrl(self.settings.get('home_page', 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0'))))
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction("New Window", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        save_page_action = QAction("Save Page", self)
        save_page_action.setShortcut("Ctrl+S")
        save_page_action.triggered.connect(self.save_page)
        file_menu.addAction(save_page_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        dev_tools_action = QAction("Developer Tools", self)
        dev_tools_action.setShortcut("F12")
        dev_tools_action.triggered.connect(self.toggle_dev_tools)
        view_menu.addAction(dev_tools_action)
        
        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")
        
        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)
        
        manage_bookmarks_action = QAction("Manage Bookmarks", self)
        manage_bookmarks_action.triggered.connect(self.show_bookmarks_manager)
        bookmarks_menu.addAction(manage_bookmarks_action)
        
        # History menu
        history_menu = menubar.addMenu("History")
        
        show_history_action = QAction("Show History", self)
        show_history_action.setShortcut("Ctrl+H")
        show_history_action.triggered.connect(self.show_history)
        history_menu.addAction(show_history_action)
        
        clear_history_action = QAction("Clear History", self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        downloads_action = QAction("Downloads", self)
        downloads_action.setShortcut("Ctrl+J")
        downloads_action.triggered.connect(self.show_downloads)
        tools_menu.addAction(downloads_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup navigation toolbar"""
        navtb = QToolBar("Navigation")
        navtb.setMovable(False)
        self.addToolBar(navtb)
        
        # Back button
        self.back_btn = QAction("←", self)
        self.back_btn.setStatusTip("Go back")
        self.back_btn.triggered.connect(self.navigate_back)
        navtb.addAction(self.back_btn)
        
        # Forward button
        self.forward_btn = QAction("→", self)
        self.forward_btn.setStatusTip("Go forward")
        self.forward_btn.triggered.connect(self.navigate_forward)
        navtb.addAction(self.forward_btn)
        
        # Refresh button
        self.refresh_btn = QAction("⟳", self)
        self.refresh_btn.setStatusTip("Refresh page")
        self.refresh_btn.triggered.connect(self.refresh_page)
        navtb.addAction(self.refresh_btn)
        
        # Home button
        self.home_btn = QAction("🏠", self)
        self.home_btn.setStatusTip("Go to home page")
        self.home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(self.home_btn)
        
        navtb.addSeparator()
        
        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Enter URL or search...")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        
        # Bookmark this page button
        self.bookmark_btn = QAction("⭐", self)
        self.bookmark_btn.setStatusTip("Bookmark this page")
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        navtb.addAction(self.bookmark_btn)
        
        navtb.addSeparator()
        
        # Menu button
        self.menu_btn = QAction("☰", self)
        self.menu_btn.setStatusTip("Menu")
        self.menu_btn.triggered.connect(self.show_menu)
        navtb.addAction(self.menu_btn)
    
    def apply_theme(self):
        """Apply selected theme"""
        if self.settings.get('theme') == 'Dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    padding: 8px 12px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QToolBar {
                    background-color: #3c3c3c;
                    border: none;
                }
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("")
    
    def add_new_tab(self, qurl, label="New Tab"):
        """Add a new browser tab"""
        browser = QWebEngineView()
        browser.load(qurl)
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(browser))
        browser.loadFinished.connect(lambda _, browser=browser: self.update_tab_title(browser))
        browser.loadStarted.connect(self.load_started)
        browser.loadProgress.connect(self.load_progress)
        browser.loadFinished.connect(self.load_finished)
        
        # Setup download handling
        browser.page().profile().downloadRequested.connect(self.download_requested)
        
        # Add to tabs
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Add history entry
        self.add_to_history(qurl.toString(), label)
        
        return browser
    
    def close_tab(self, index):
        """Close a tab"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        browser = self.tabs.widget(index)
        if browser:
            self.update_urlbar(browser)
            self.update_buttons(browser)
    
    def update_urlbar(self, browser):
        """Update URL bar with current page URL"""
        if browser == self.tabs.currentWidget():
            self.urlbar.setText(browser.url().toString())
    
    def update_tab_title(self, browser):
        """Update tab title"""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            title = browser.page().title()
            if len(title) > 20:
                title = title[:20] + "..."
            self.tabs.setTabText(index, title)
            
            if browser == self.tabs.currentWidget():
                self.setWindowTitle(f"{browser.page().title()} - Bean Browser")
    
    def update_buttons(self, browser):
        """Update navigation buttons state"""
        self.back_btn.setEnabled(browser.page().history().canGoBack())
        self.forward_btn.setEnabled(browser.page().history().canGoForward())
    
    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        url_text = self.urlbar.text().strip()
        self.navigate_to_url_direct(url_text)
    
    def navigate_to_url_direct(self, url_text):
        """Navigate directly to a URL"""
        if not url_text:
            return
        
        # Handle bookmarks
        if url_text.startswith("bookmark"):
            try:
                line_number = int(url_text[8:])
                with open("bookmarks.json", 'r') as file:
                    bookmarks = json.load(file)
                    if 0 < line_number <= len(bookmarks):
                        url_text = bookmarks[line_number - 1]['url']
                    else:
                        self.status_bar.showMessage("Bookmark doesn't exist", 2000)
                        return
            except Exception as e:
                self.status_bar.showMessage(f"Error reading bookmarks: {e}", 2000)
                return
        
        # Determine if it's a URL or search query
        if self.is_url(url_text):
            if not url_text.startswith(("http://", "https://")):
                url_text = "https://" + url_text
            final_url = QUrl(url_text)
        else:
            # Search query
            search_engines = {
                'Bean Engine': 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0&gsc.q={}',
                'Google': 'https://www.google.com/search?q={}',
                'DuckDuckGo': 'https://duckduckgo.com/?q={}',
                'Bing': 'https://www.bing.com/search?q={}',
                'Yahoo': 'https://search.yahoo.com/search?p={}'
            }
            search_engine = self.settings.get('search_engine', 'Google')
            search_url = search_engines.get(search_engine, search_engines['Google'])
            query = url_text.replace(" ", "+")
            final_url = QUrl(search_url.format(query))
        
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.load(final_url)
            self.add_to_history(final_url.toString(), "Loading...")
    
    def is_url(self, text):
        """Check if text is a URL"""
        return ("." in text and " " not in text) or text.startswith(("http://", "https://", "ftp://"))
    
    def navigate_back(self):
        """Navigate back"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()
    
    def navigate_forward(self):
        """Navigate forward"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()
    
    def refresh_page(self):
        """Refresh current page"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()
    
    def navigate_home(self):
        """Navigate to home page"""
        home_url = self.settings.get('home_page', 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0')
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.load(QUrl(home_url))
    
    def load_started(self):
        """Handle page load start"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
    
    def load_progress(self, progress):
        """Handle page load progress"""
        self.progress_bar.setValue(progress)
    
    def load_finished(self):
        """Handle page load finish"""
        self.progress_bar.setVisible(False)
        current_browser = self.tabs.currentWidget()
        if current_browser:
            self.add_to_history(current_browser.url().toString(), current_browser.page().title())
    
    def add_to_history(self, url, title):
        """Add page to browsing history"""
        try:
            conn = sqlite3.connect('browser_history.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO history VALUES (?, ?, ?)', 
                          (url, title, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error adding to history: {e}")
    
    def download_requested(self, download):
        """Handle download requests"""
        download.accept()
        self.downloads_count += 1
        self.status_bar.showMessage(f"Download started: {download.path()}", 3000)
    
    # Menu actions
    def new_window(self):
        """Open new browser window"""
        new_window = MainWindow()
        new_window.show()
    
    def save_page(self):
        """Save current page"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Page", "", "HTML Files (*.html)")
            if filename:
                # This would require additional implementation
                self.status_bar.showMessage("Save page functionality not fully implemented", 2000)
    
    def show_find_dialog(self):
        """Show find dialog"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            text, ok = QInputDialog.getText(self, 'Find', 'Enter text to find:')
            if ok and text:
                current_browser.findText(text)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def zoom_in(self):
        """Zoom in"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(current_browser.zoomFactor() * 1.1)
    
    def zoom_out(self):
        """Zoom out"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(current_browser.zoomFactor() * 0.9)
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(1.0)
    
    def toggle_dev_tools(self):
        """Toggle developer tools"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            if not hasattr(self, 'dev_tools') or not self.dev_tools.isVisible():
                self.dev_tools = QWebEngineView()
                current_browser.page().setDevToolsPage(self.dev_tools.page())
                self.dev_tools.show()
                self.dev_tools.resize(800, 600)
                self.dev_tools.setWindowTitle("Developer Tools")
            else:
                self.dev_tools.close()
    
    def add_bookmark(self):
        """Add current page to bookmarks"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.page().title()
            
            try:
                with open("bookmarks.json", "r") as f:
                    bookmarks = json.load(f)
            except FileNotFoundError:
                bookmarks = []
            
            bookmark = {
                "title": title,
                "url": url,
                "date_added": datetime.now().isoformat()
            }
            bookmarks.append(bookmark)
            
            with open("bookmarks.json", "w") as f:
                json.dump(bookmarks, f, indent=2)
            
            self.status_bar.showMessage("Bookmark added", 2000)
    
    def show_bookmarks_manager(self):
        """Show bookmarks manager"""
        dialog = BookmarksManager(self)
        dialog.exec_()
    
    def show_history(self):
        """Show history dialog"""
        dialog = HistoryManager(self)
        dialog.exec_()
    
    def clear_history(self):
        """Clear browsing history"""
        reply = QMessageBox.question(self, 'Clear History', 
                                   'Are you sure you want to clear all browsing history?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('browser_history.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history')
                conn.commit()
                conn.close()
                self.status_bar.showMessage("History cleared", 2000)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear history: {e}")
    
    def show_downloads(self):
        """Show downloads manager"""
        dialog = DownloadsManager(self)
        dialog.exec_()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_settings()
            self.apply_theme()
    
    def show_menu(self):
        """Show context menu"""
        menu = QMenu(self)
        
        # Add common actions
        menu.addAction("New Tab", lambda: self.add_new_tab(QUrl(self.settings.get('home_page', 'https://cse.google.com/cse?cx=347ea4ef67cbc42a7#gsc.tab=0'))))
        menu.addAction("New Window", self.new_window)
        menu.addSeparator()
        menu.addAction("Bookmarks", self.show_bookmarks_manager)
        menu.addAction("History", self.show_history)
        menu.addAction("Downloads", self.show_downloads)
        menu.addSeparator()
        menu.addAction("Settings", self.show_settings)
        menu.addAction("About", self.show_about)
        
        # Show menu at cursor position
        menu.exec_(QCursor.pos())
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Bean Browser", 
                         """<h3>Bean Browser</h3>
                         <p>A full-featured web browser built with PyQt5</p>
                         <p><b>Features:</b></p>
                         <ul>
                         <li>Tabbed browsing with close buttons</li>
                         <li>Bookmark management</li>
                         <li>Browsing history</li>
                         <li>Download manager</li>
                         <li>Developer tools</li>
                         <li>Customizable settings</li>
                         <li>Dark/Light themes</li>
                         <li>Full-screen mode</li>
                         <li>Zoom controls</li>
                         <li>Find in page</li>
                         </ul>
                         <p>Built with ❤️ using PyQt5 and QtWebEngine</p>""")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Save any remaining data
        event.accept()

class FindDialog(QDialog):
    """Find in page dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.setModal(False)
        self.resize(300, 100)
        
        layout = QHBoxLayout()
        
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Find in page...")
        
        self.find_next_btn = QPushButton("Next")
        self.find_prev_btn = QPushButton("Previous")
        self.close_btn = QPushButton("Close")
        
        layout.addWidget(self.find_edit)
        layout.addWidget(self.find_next_btn)
        layout.addWidget(self.find_prev_btn)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
        # Connect signals
        self.find_edit.textChanged.connect(self.find_text)
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.close_btn.clicked.connect(self.close)
    
    def find_text(self, text):
        """Find text in current page"""
        if hasattr(self.parent(), 'tabs'):
            current_browser = self.parent().tabs.currentWidget()
            if current_browser and text:
                current_browser.findText(text)
    
    def find_next(self):
        """Find next occurrence"""
        text = self.find_edit.text()
        if hasattr(self.parent(), 'tabs') and text:
            current_browser = self.parent().tabs.currentWidget()
            if current_browser:
                current_browser.findText(text)
    
    def find_previous(self):
        """Find previous occurrence"""
        text = self.find_edit.text()
        if hasattr(self.parent(), 'tabs') and text:
            current_browser = self.parent().tabs.currentWidget()
            if current_browser:
                current_browser.findText(text, QWebEnginePage.FindBackward)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Bean Browser")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Bean Software")
    
    # Set application icon
    app.setWindowIcon(QIcon())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Handle multiple instances
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        window.add_new_tab(QUrl(url))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()