from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog
from .widgets import Panel

class EventHistory(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26,22,26,22)
        top = QHBoxLayout()
        title = QLabel("Event history")
        title.setStyleSheet("font-size:27px;font-weight:750;")
        top.addWidget(title)
        top.addStretch()
        export = QPushButton("Export CSV")
        export.clicked.connect(self.export_csv)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        top.addWidget(refresh); top.addWidget(export)
        layout.addLayout(top)
        panel = Panel()
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(["Timestamp","Event","Previous","New state","Details"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        panel.layout.addWidget(self.table)
        layout.addWidget(panel,1)
        self.refresh()
    def refresh(self):
        rows = self.logger.list_events()
        self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            for c,value in enumerate(row):
                self.table.setItem(r,c,QTableWidgetItem(str(value or "")))
    def export_csv(self):
        path,_ = QFileDialog.getSaveFileName(self,"Export event history","events.csv","CSV files (*.csv)")
        if path:
            self.logger.export_csv(path)
