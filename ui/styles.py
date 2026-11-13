
APP_STYLE = """
* {
    font-family: 'Segoe UI';
}

QMainWindow, QWidget#root {
    background: #171916;
    color: #E8E4D8;
}

QWidget {
    color: #E8E4D8;
}

QLabel#muted {
    color: #A6A493;
}

QLabel#eyebrow {
    color: #A2AA8A;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

QFrame#surface {
    background: #252821;
    border: 1px solid #393D32;
    border-radius: 18px;
}

QFrame#surface2 {
    background: #20231D;
    border: 1px solid #393D32;
    border-radius: 16px;
}

QPushButton {
    background: #30342A;
    border: 1px solid #515747;
    border-radius: 10px;
    padding: 10px 16px;
    color: #EEE9DC;
    font-weight: 600;
}

QPushButton:hover {
    background: #3B4133;
    border-color: #A2AA8A;
}

QPushButton:pressed {
    background: #24271F;
}

QPushButton#primary {
    background: #788568;
    border: 1px solid #9AA587;
    color: #171916;
}

QPushButton#danger {
    background: #A6533D;
    border: 1px solid #C4775B;
    color: #FFF5EA;
}

QPushButton#nav {
    text-align: left;
    padding: 13px 15px;
    background: transparent;
    border: 0;
    color: #B5B2A5;
}

QPushButton#nav:checked {
    background: #30372B;
    color: #E2E6D3;
    border-left: 3px solid #A2AA8A;
}

QLineEdit, QComboBox {
    background: #1D211B;
    border: 1px solid #454B3D;
    border-radius: 9px;
    padding: 9px;
    color: #E8E4D8;
}

QTableWidget {
    background: #20231D;
    alternate-background-color: #292D24;
    border: 1px solid #393D32;
    border-radius: 12px;
    gridline-color: #393D32;
}

QHeaderView::section {
    background: #30342A;
    color: #C4C5B5;
    padding: 9px;
    border: 0;
}
"""
