from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


APP_NAME = "Creative Factory Modbus"
WINDOW_TITLE = "Creative Factory Modbus Workbench"
ORGANIZATION_NAME = "Creative Factory"
TAGLINE = "Industrial connectivity for RTU and TCP diagnostics"
CAPABILITY_LABEL = "Factory Floor Ready"
PRODUCT_VERSION = "1.0.0"

BRAND_COLORS = {
    "paper": "#F7F1E8",
    "panel": "#FFFDF8",
    "panel_alt": "#F0E6D8",
    "ink": "#1E2328",
    "muted": "#6C6258",
    "accent": "#D96C1E",
    "accent_deep": "#A34714",
    "accent_soft": "#F5D9C0",
    "border": "#D8C7B4",
    "success_bg": "#DDEBDF",
    "success_fg": "#24553B",
    "warning_bg": "#F6E1CF",
    "warning_fg": "#8A4516",
}

APP_STYLE_SHEET = f"""
QWidget {{
    background: {BRAND_COLORS["paper"]};
    color: {BRAND_COLORS["ink"]};
    font-size: 10pt;
}}

QMainWindow {{
    background: {BRAND_COLORS["paper"]};
}}

QGroupBox {{
    background: {BRAND_COLORS["panel"]};
    border: 1px solid {BRAND_COLORS["border"]};
    border-radius: 18px;
    margin-top: 16px;
    padding: 14px 14px 14px 14px;
    font-weight: 700;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: {BRAND_COLORS["accent"]};
    background: {BRAND_COLORS["panel"]};
}}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QPlainTextEdit,
QTableWidget,
QStackedWidget {{
    background: {BRAND_COLORS["panel"]};
    border: 1px solid {BRAND_COLORS["border"]};
    border-radius: 12px;
    padding: 6px 8px;
    selection-background-color: {BRAND_COLORS["accent"]};
}}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QPlainTextEdit:focus,
QTableWidget:focus {{
    border: 1px solid {BRAND_COLORS["accent"]};
}}

QPushButton {{
    background: {BRAND_COLORS["accent"]};
    color: white;
    border: none;
    border-radius: 12px;
    padding: 9px 16px;
    font-weight: 700;
}}

QPushButton:hover {{
    background: {BRAND_COLORS["accent_deep"]};
}}

QPushButton:disabled {{
    background: #C7B8A6;
    color: #F7F1E8;
}}

QHeaderView::section {{
    background: {BRAND_COLORS["ink"]};
    color: {BRAND_COLORS["paper"]};
    border: none;
    padding: 8px;
    font-weight: 700;
}}

QTableWidget {{
    alternate-background-color: {BRAND_COLORS["panel_alt"]};
    gridline-color: {BRAND_COLORS["border"]};
}}

QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {BRAND_COLORS["border"]};
    background: {BRAND_COLORS["panel"]};
}}

QCheckBox::indicator:checked {{
    background: {BRAND_COLORS["accent"]};
    border: 1px solid {BRAND_COLORS["accent"]};
}}

#brandHeader {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {BRAND_COLORS["panel"]},
        stop: 0.55 #F4E7D7,
        stop: 1 #FBEEDC
    );
    border: 1px solid {BRAND_COLORS["border"]};
    border-radius: 24px;
}}

#brandTitle {{
    font-size: 20px;
    font-weight: 800;
    color: {BRAND_COLORS["ink"]};
}}

#brandSubtitle {{
    color: {BRAND_COLORS["muted"]};
    font-size: 10pt;
}}

#brandPill {{
    background: {BRAND_COLORS["ink"]};
    color: {BRAND_COLORS["paper"]};
    border-radius: 12px;
    padding: 8px 10px;
    font-weight: 700;
    font-size: 9.5pt;
}}

#statusPill {{
    background: {BRAND_COLORS["warning_bg"]};
    color: {BRAND_COLORS["warning_fg"]};
    border-radius: 12px;
    padding: 8px 10px;
    font-weight: 700;
}}

#statusPill[connected="true"] {{
    background: {BRAND_COLORS["success_bg"]};
    color: {BRAND_COLORS["success_fg"]};
}}

#summaryLabel {{
    color: {BRAND_COLORS["ink"]};
    font-weight: 700;
}}

QTabWidget::pane {{
    border: 1px solid {BRAND_COLORS["border"]};
    border-radius: 16px;
    background: {BRAND_COLORS["panel"]};
    top: -1px;
}}

QTabBar::tab {{
    background: {BRAND_COLORS["panel_alt"]};
    color: {BRAND_COLORS["muted"]};
    border: 1px solid {BRAND_COLORS["border"]};
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 8px 14px;
    margin-right: 4px;
    font-weight: 700;
}}

QTabBar::tab:selected {{
    background: {BRAND_COLORS["panel"]};
    color: {BRAND_COLORS["ink"]};
}}
"""


def create_brand_pixmap(size: int = 256) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    canvas = QRectF(0, 0, size, size)
    radius = size * 0.2

    bg_gradient = QLinearGradient(canvas.topLeft(), canvas.bottomRight())
    bg_gradient.setColorAt(0.0, QColor("#232629"))
    bg_gradient.setColorAt(0.55, QColor("#2D3237"))
    bg_gradient.setColorAt(1.0, QColor("#191C1F"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bg_gradient)
    painter.drawRoundedRect(canvas, radius, radius)

    accent_rect = QRectF(size * 0.1, size * 0.1, size * 0.18, size * 0.8)
    accent_gradient = QLinearGradient(accent_rect.topLeft(), accent_rect.bottomRight())
    accent_gradient.setColorAt(0.0, QColor(BRAND_COLORS["accent"]))
    accent_gradient.setColorAt(1.0, QColor("#F49A58"))
    painter.setBrush(accent_gradient)
    painter.drawRoundedRect(accent_rect, size * 0.05, size * 0.05)

    wire_path = QPainterPath()
    wire_path.moveTo(QPointF(size * 0.36, size * 0.34))
    wire_path.cubicTo(
        QPointF(size * 0.48, size * 0.2),
        QPointF(size * 0.68, size * 0.2),
        QPointF(size * 0.8, size * 0.34),
    )
    wire_path.lineTo(QPointF(size * 0.66, size * 0.34))
    wire_path.cubicTo(
        QPointF(size * 0.58, size * 0.28),
        QPointF(size * 0.48, size * 0.28),
        QPointF(size * 0.42, size * 0.36),
    )
    wire_path.cubicTo(
        QPointF(size * 0.36, size * 0.44),
        QPointF(size * 0.36, size * 0.56),
        QPointF(size * 0.42, size * 0.64),
    )
    wire_path.cubicTo(
        QPointF(size * 0.48, size * 0.72),
        QPointF(size * 0.58, size * 0.72),
        QPointF(size * 0.66, size * 0.66),
    )
    wire_path.lineTo(QPointF(size * 0.8, size * 0.66))
    wire_path.cubicTo(
        QPointF(size * 0.68, size * 0.8),
        QPointF(size * 0.48, size * 0.8),
        QPointF(size * 0.36, size * 0.66),
    )
    wire_path.cubicTo(
        QPointF(size * 0.22, size * 0.5),
        QPointF(size * 0.22, size * 0.5),
        QPointF(size * 0.36, size * 0.34),
    )

    painter.setBrush(QColor("#F7F1E8"))
    painter.drawPath(wire_path)

    pen = QPen(QColor(BRAND_COLORS["accent_soft"]), size * 0.04)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawLine(QPointF(size * 0.66, size * 0.5), QPointF(size * 0.86, size * 0.5))

    for center_y in (0.42, 0.5, 0.58):
        painter.setBrush(QColor("#F7F1E8"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(size * 0.88, size * center_y), size * 0.028, size * 0.028)

    painter.setPen(QColor("#F7F1E8"))
    font = QFont("Segoe UI", max(10, int(size * 0.12)))
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(
        QRectF(size * 0.12, size * 0.74, size * 0.76, size * 0.14),
        Qt.AlignmentFlag.AlignCenter,
        "CF",
    )

    painter.end()
    return pixmap


def create_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(create_brand_pixmap(size))
    return icon
