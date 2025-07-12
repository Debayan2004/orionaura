import sys, os, json
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QToolBar, QAction, QLineEdit,
                             QFileDialog, QInputDialog, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import speech_recognition as sr

BOOKMARKS_FILE = "bookmarks.json"
HISTORY_FILE = "history.txt"

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OrionAura Browser")
        self.setWindowIcon(QIcon("orion_logo.png"))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        self.setCentralWidget(self.tabs)

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        # Navigation buttons
        self.add_nav_button("Back", self.go_back)
        self.add_nav_button("Forward", self.go_forward)
        self.add_nav_button("Reload", self.reload_page)
        self.add_nav_button("Home", self.go_home)
        self.add_nav_button("New Tab", self.add_tab)
        self.add_nav_button("Bookmark", self.bookmark_page)
        self.add_nav_button("Voice", self.voice_search)
        self.add_nav_button("Dark Mode", self.toggle_dark_mode)
        self.add_nav_button("History", self.show_history)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.urlbar)

        self.dark_mode = False
        self.add_tab(QUrl.fromLocalFile(os.path.abspath("orionaura.html")))

    def add_nav_button(self, name, callback):
        btn = QAction(name, self)
        btn.triggered.connect(callback)
        self.navbar.addAction(btn)

    def add_tab(self, qurl=None):
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_urlbar)
        browser.loadFinished.connect(self.save_history)
        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_to_url(self):
        url = self.urlbar.text()
        if not url.startswith("http"):
            url = "https://www.google.com/search?q=" + url
        self.current_browser().setUrl(QUrl(url))

    def update_urlbar(self, *args):
        browser = self.current_browser()
        self.urlbar.setText(browser.url().toString())
        self.setWindowTitle(browser.url().toString())

    def go_back(self): self.current_browser().back()
    def go_forward(self): self.current_browser().forward()
    def reload_page(self): self.current_browser().reload()
    def go_home(self):
        self.current_browser().setUrl(QUrl.fromLocalFile(os.path.abspath("orionaura.html")))

    def bookmark_page(self):
        url = self.current_browser().url().toString()
        name, ok = QInputDialog.getText(self, "Bookmark", "Enter name:")
        if ok:
            try:
                with open(BOOKMARKS_FILE, "r") as f:
                    bookmarks = json.load(f)
            except:
                bookmarks = {}
            bookmarks[name] = url
            with open(BOOKMARKS_FILE, "w") as f:
                json.dump(bookmarks, f, indent=4)
            QMessageBox.information(self, "Saved", f"Bookmarked: {name}")

    def save_history(self):
        url = self.current_browser().url().toString()
        with open(HISTORY_FILE, "a") as f:
            f.write(url + "\n")

    def show_history(self):
        if not os.path.exists(HISTORY_FILE):
            QMessageBox.information(self, "No History", "No browsing history found.")
            return
        with open(HISTORY_FILE, "r") as f:
            lines = f.readlines()
        msg = QMessageBox(self)
        msg.setWindowTitle("Browsing History")
        msg.setText("\n".join(lines[-20:]))  # Show last 20 URLs
        msg.exec_()

    def toggle_dark_mode(self):
        if not self.dark_mode:
            self.setStyleSheet("QMainWindow { background-color: #121212; color: white; } QLineEdit { color: white; background: #333; }")
        else:
            self.setStyleSheet("")
        self.dark_mode = not self.dark_mode

    def voice_search(self):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.statusBar().showMessage("Listening...")
                audio = r.listen(source, timeout=5)
                query = r.recognize_google(audio)
                self.statusBar().showMessage("Searching: " + query)
                self.current_browser().setUrl(QUrl("https://www.google.com/search?q=" + query))
        except Exception as e:
            self.statusBar().showMessage("Voice error: " + str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("OrionAura")
    window = Browser()
    window.showMaximized()
    sys.exit(app.exec_())


