"""Design system and style definitions for Music Master."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #121214;
    color: #E2E8F0;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    color: #E2E8F0;
}

/* Sidebar navigation */
QFrame#SidebarFrame {
    background-color: #18181B;
    border-right: 1px solid #27272A;
}

QPushButton.NavButton {
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background-color: transparent;
    color: #A1A1AA;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #27272A;
    color: #F4F4F5;
}

QPushButton.NavButton:checked {
    background-color: #3B82F6;
    color: #FFFFFF;
    font-weight: 600;
}

/* Top header */
QFrame#HeaderFrame {
    background-color: #18181B;
    border-bottom: 1px solid #27272A;
}

QLabel#HeaderTitle {
    font-size: 18px;
    font-weight: 700;
    color: #F8FAFC;
}

QLabel#HeaderSubtitle {
    font-size: 12px;
    color: #94A3B8;
}

/* Content Area */
QFrame#ContentFrame {
    background-color: #121214;
}

/* Status Bar */
QStatusBar {
    background-color: #18181B;
    border-top: 1px solid #27272A;
    color: #94A3B8;
    font-size: 11px;
}

/* Cards and Panels */
QFrame.Card {
    background-color: #1E1E24;
    border: 1px solid #2E2E38;
    border-radius: 8px;
}

QLabel.CardTitle {
    font-size: 15px;
    font-weight: 600;
    color: #F1F5F9;
}

/* Common Buttons */
QPushButton.PrimaryButton {
    background-color: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #2563EB;
}

QPushButton.SecondaryButton {
    background-color: #27272A;
    color: #E2E8F0;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #3F3F46;
}

QPushButton.DangerButton {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #DC2626;
}
"""
