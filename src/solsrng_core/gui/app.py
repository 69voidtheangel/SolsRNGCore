from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from solsrng_core.antiafk import AntiAFKController, WindowError
from solsrng_core.config import (
    BIOMES,
    EVENT_BIOMES,
    NORMAL_BIOMES,
    RARE_LIST,
    AppConfig,
    WebhookProfile,
    load_config,
    save_config,
)
from solsrng_core.discord import DiscordWebhook
from solsrng_core.logwatcher import SoberBiomeWatcher
from .themes import THEMES

ROOT = Path(__file__).resolve().parents[3]
LOGO = ROOT / "assets" / "solsrng_core_logo.svg"


class SidebarButton(QPushButton):
    def __init__(self, text: str, page: int):
        super().__init__(text)
        self.page = page
        self.setCheckable(True)
        self.setProperty("navButton", True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config: AppConfig = load_config()
        self.afk: AntiAFKController | None = None
        self.biome_watcher = SoberBiomeWatcher(
            self._biome_detected,
            self.log,
        )
        self._loading = True
        self._buttons: list[SidebarButton] = []

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self._autosave)

        self.setWindowTitle("Sol's RNG Core")
        self.setWindowIcon(QIcon(str(LOGO)))
        self.resize(1120, 760)
        self.setMinimumSize(980, 680)

        self._build()
        self.biome_watcher.start()
        self._apply_theme(self.config.theme, autosave=False)
        self._loading = False

    # ---------- window / layout ----------

    def _build(self):
        outer = QWidget()
        root = QHBoxLayout(outer)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        root.addWidget(self._sidebar(), 0)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._discord_page())
        self.pages.addWidget(self._biomes_page())
        self.pages.addWidget(self._settings_page())
        root.addWidget(self.pages, 1)

        self.setCentralWidget(outer)
        self._set_page(0)

    def _sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidebar")
        panel.setFixedWidth(220)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        brand = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            QPixmap(str(LOGO)).scaled(
                46,
                46,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        brand.addWidget(icon)

        text = QLabel(
            "<b>Sol's RNG Core</b><br>"
            "<span class='muted'>Detect • Notify • Automate</span>"
        )
        text.setTextFormat(Qt.TextFormat.RichText)
        brand.addWidget(text)
        layout.addLayout(brand)

        status = QLabel("●  Core online")
        status.setObjectName("statusPill")
        layout.addWidget(status)
        layout.addSpacing(12)

        names = [
            "◈  Dashboard",
            "◎  Discord",
            "✦  Biomes",
            "⚙  Settings",
        ]
        for index, name in enumerate(names):
            button = SidebarButton(name, index)
            button.clicked.connect(
                lambda _checked=False, i=index: self._set_page(i)
            )
            self._buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()

        footer = QLabel(
            "Moonlit edition\n"
            "Profile settings save automatically."
        )
        footer.setObjectName("sidebarFooter")
        footer.setWordWrap(True)
        layout.addWidget(footer)

        return panel

    def _set_page(self, index: int):
        if index < 0 or index >= self.pages.count():
            return
        if not self._loading:
            self._collect()
            self._save_now()
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self._buttons):
            button.setChecked(i == index)

    def _brand_header(self, title: str, subtitle: str) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 4)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return box

    def _card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        if title:
            label = QLabel(title)
            label.setObjectName("cardTitle")
            layout.addWidget(label)
        return frame, layout

    # ---------- dashboard ----------

    def _dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.addWidget(
            self._brand_header(
                "Dashboard",
                "Keep the game focused, automate Anti-AFK, and test your active Discord profile.",
            )
        )

        top = QHBoxLayout()
        top.setSpacing(14)

        afk_card, afk_layout = self._card("Anti-AFK")
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Status"))
        self.afk_status = QLabel("STOPPED")
        self.afk_status.setObjectName("statusValue")
        status_row.addWidget(self.afk_status)
        status_row.addStretch()
        afk_layout.addLayout(status_row)

        buttons = QGridLayout()
        buttons.setHorizontalSpacing(8)
        buttons.setVerticalSpacing(8)

        for label, fn, row, col in [
            ("Start", self.start_afk, 0, 0),
            ("Stop + Restore", self.stop_afk, 0, 1),
            ("Swap to Game", self.swap_game, 1, 0),
            ("Open Previous", self.restore_window, 1, 1),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            buttons.addWidget(b, row, col)
        afk_layout.addLayout(buttons)
        top.addWidget(afk_card, 1)

        profile_card, profile_layout = self._card("Active Discord Profile")
        self.dashboard_profile = QLabel("Main Server")
        self.dashboard_profile.setObjectName("metricValue")
        profile_layout.addWidget(self.dashboard_profile)
        self.dashboard_webhook = QLabel("Webhook not configured")
        self.dashboard_webhook.setWordWrap(True)
        profile_layout.addWidget(self.dashboard_webhook)
        test = QPushButton("Send Test Webhook")
        test.clicked.connect(self.test_webhook)
        save = QPushButton("Save Everything")
        save.clicked.connect(self.save_all)
        profile_layout.addWidget(test)
        profile_layout.addWidget(save)
        top.addWidget(profile_card, 1)
        layout.addLayout(top)

        log_card, log_layout = self._card("Activity")
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(500)
        log_layout.addWidget(self.log_box)
        layout.addWidget(log_card, 1)
        return page

    # ---------- discord ----------

    def _discord_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.addWidget(
            self._brand_header(
                "Discord",
                "Every profile has its own webhook, Roblox private-server link, notification rules, images, and biome roles.",
            )
        )

        profile_card, profile_layout = self._card("Webhook Profiles")
        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Profile"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self._profile_changed)
        profile_row.addWidget(self.profile_combo, 1)

        for label, fn in [
            ("+ Add", self._add_profile),
            ("Rename", self._rename_profile),
            ("Remove", self._remove_profile),
        ]:
            b = QPushButton(label)
            b.clicked.connect(fn)
            profile_row.addWidget(b)

        profile_layout.addLayout(profile_row)
        layout.addWidget(profile_card)

        details_card, details_layout = self._card("Profile Settings")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.webhook_enabled = QCheckBox("Enabled")
        self.webhook_url = QLineEdit()
        self.webhook_url.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.private_server = QLineEdit()
        self.private_server.setPlaceholderText("Optional Roblox private-server URL")
        self.image_dir = QLineEdit()
        self.image_dir.setPlaceholderText("library/biomes")
        self.rare_fallback = QCheckBox("Use @everyone when a rare biome has no role ID")

        grid.addWidget(self.webhook_enabled, 0, 0)
        grid.addWidget(self.webhook_url, 0, 1, 1, 2)
        grid.addWidget(QLabel("Roblox private server"), 1, 0)
        grid.addWidget(self.private_server, 1, 1, 1, 2)
        grid.addWidget(QLabel("Biome images"), 2, 0)
        grid.addWidget(self.image_dir, 2, 1)
        grid.addWidget(self.rare_fallback, 2, 2)

        details_layout.addLayout(grid)
        layout.addWidget(details_card)

        roles_card, roles_layout = self._card("Per-Biome Roles")
        hint = QLabel(
            "One Discord role per biome. Put the numeric role ID in the middle column. "
            "There is no random role mode."
        )
        hint.setObjectName("cardHint")
        hint.setWordWrap(True)
        roles_layout.addWidget(hint)

        self.roles_table = QTableWidget(len(BIOMES), 3)
        self.roles_table.setObjectName("rolesTable")
        self.roles_table.setHorizontalHeaderLabels([
            "Biome",
            "Discord Role ID",
            "Notify",
        ])
        self.roles_table.setAlternatingRowColors(True)
        self.roles_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.roles_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.SelectedClicked
        )
        self.roles_table.verticalHeader().setVisible(False)
        self.roles_table.horizontalHeader().setStretchLastSection(False)
        self.roles_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.roles_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.roles_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.roles_table.itemChanged.connect(self._roles_changed)
        roles_layout.addWidget(self.roles_table, 1)

        controls = QHBoxLayout()
        for label, biomes in [
            ("Enable Normal", NORMAL_BIOMES),
            ("Enable Events", EVENT_BIOMES),
            ("Enable Rare", RARE_LIST),
            ("Enable All", BIOMES),
        ]:
            b = QPushButton(label)
            b.clicked.connect(
                lambda _checked=False, names=biomes: self._set_biomes(names)
            )
            controls.addWidget(b)
        controls.addStretch()
        save = QPushButton("Save Profile")
        save.clicked.connect(self.save_all)
        controls.addWidget(save)
        roles_layout.addLayout(controls)

        layout.addWidget(roles_card, 1)

        self._refresh_profiles()
        return page

    def _refresh_profiles(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile in self.config.profiles:
            self.profile_combo.addItem(profile.name)
        index = max(0, min(self.config.active_profile, len(self.config.profiles) - 1))
        self.profile_combo.setCurrentIndex(index)
        self.profile_combo.blockSignals(False)
        self._load_profile_fields()

    def _current_profile(self) -> WebhookProfile:
        index = self.profile_combo.currentIndex()
        return self.config.profiles[index]

    def _load_profile_fields(self):
        if not hasattr(self, "profile_combo"):
            return
        profile = self._current_profile()
        self.config.active_profile = self.profile_combo.currentIndex()

        widgets = [
            self.webhook_enabled,
            self.webhook_url,
            self.private_server,
            self.image_dir,
            self.rare_fallback,
            self.roles_table,
        ]
        for widget in widgets:
            widget.blockSignals(True)

        self.webhook_enabled.setChecked(profile.enabled)
        self.webhook_url.setText(profile.url)
        self.private_server.setText(profile.roblox_private_server_url)
        self.image_dir.setText(profile.biome_image_dir)
        self.rare_fallback.setChecked(profile.rare_everyone_fallback)

        self.roles_table.setRowCount(len(BIOMES))
        notify = set(profile.notify_biomes)
        for row, biome in enumerate(BIOMES):
            biome_item = QTableWidgetItem(biome)
            biome_item.setFlags(
                biome_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.roles_table.setItem(row, 0, biome_item)

            role_item = QTableWidgetItem(profile.biome_roles.get(biome, ""))
            role_item.setData(Qt.ItemDataRole.UserRole, "role ID")
            role_item.setToolTip("Paste the numeric Discord role ID")
            self.roles_table.setItem(row, 1, role_item)

            notify_item = QTableWidgetItem()
            notify_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            notify_item.setCheckState(
                Qt.CheckState.Checked
                if biome in notify
                else Qt.CheckState.Unchecked
            )
            self.roles_table.setItem(row, 2, notify_item)

        for widget in widgets:
            widget.blockSignals(False)

        self._update_dashboard_profile()

    def _save_profile_fields(self):
        profile = self._current_profile()
        profile.enabled = self.webhook_enabled.isChecked()
        profile.url = self.webhook_url.text().strip()
        profile.roblox_private_server_url = self.private_server.text().strip()
        profile.biome_image_dir = self.image_dir.text().strip() or "library/biomes"
        profile.rare_everyone_fallback = self.rare_fallback.isChecked()

        profile.notify_biomes = []
        profile.biome_roles = {biome: "" for biome in BIOMES}
        for row, biome in enumerate(BIOMES):
            role_item = self.roles_table.item(row, 1)
            notify_item = self.roles_table.item(row, 2)
            if role_item is not None:
                profile.biome_roles[biome] = role_item.text().strip()
            if (
                notify_item is not None
                and notify_item.checkState() == Qt.CheckState.Checked
            ):
                profile.notify_biomes.append(biome)

        self.config.active_profile = self.profile_combo.currentIndex()

    def _profile_changed(self, index: int):
        if self._loading or index < 0:
            return
        self._save_profile_fields()
        self._save_now()
        self.config.active_profile = index
        self._load_profile_fields()
        self._save_now()

    def _add_profile(self):
        self._save_profile_fields()
        self._save_now()
        number = len(self.config.profiles) + 1
        self.config.profiles.append(
            WebhookProfile(name=f"Server {number}")
        )
        self.config.active_profile = len(self.config.profiles) - 1
        self._refresh_profiles()
        self._save_now()

    def _remove_profile(self):
        if len(self.config.profiles) <= 1:
            QMessageBox.information(
                self,
                "Webhook Profiles",
                "Keep at least one profile.",
            )
            return
        self._save_profile_fields()
        index = self.profile_combo.currentIndex()
        self.config.profiles.pop(index)
        self.config.active_profile = max(
            0,
            min(index, len(self.config.profiles) - 1),
        )
        self._refresh_profiles()
        self._save_now()

    def _rename_profile(self):
        profile = self._current_profile()
        name, ok = QInputDialog.getText(
            self,
            "Rename Profile",
            "Profile name:",
            text=profile.name,
        )
        if ok and name.strip():
            profile.name = name.strip()
            self._refresh_profiles()
            self.profile_combo.setCurrentIndex(self.config.active_profile)
            self._save_now()

    def _roles_changed(self, _item: QTableWidgetItem):
        if not self._loading:
            self.schedule_save()

    def _set_biomes(self, names: list[str]):
        for row, biome in enumerate(BIOMES):
            item = self.roles_table.item(row, 2)
            if item is None:
                continue
            item.setCheckState(
                Qt.CheckState.Checked
                if biome in names
                else Qt.CheckState.Unchecked
            )
        self._save_profile_fields()
        self._save_now()

    # ---------- biomes ----------

    def _biomes_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.addWidget(
            self._brand_header(
                "Biome Notifications",
                "Quickly control which events the active Discord profile receives.",
            )
        )

        card, card_layout = self._card("Active Profile Biomes")
        self.biome_list = QListWidget()
        self._biome_items: dict[str, QListWidgetItem] = {}

        groups = [
            ("NORMAL", NORMAL_BIOMES),
            ("EVENT", EVENT_BIOMES),
            ("RARE", RARE_LIST),
        ]
        selected = set(self._current_profile().notify_biomes)

        for heading, names in groups:
            header = QListWidgetItem(f"━━ {heading} BIOMES ━━")
            header.setFlags(
                header.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
                & ~Qt.ItemFlag.ItemIsEnabled
            )
            self.biome_list.addItem(header)
            for biome in names:
                item = QListWidgetItem(biome)
                item.setCheckState(
                    Qt.CheckState.Checked
                    if biome in selected
                    else Qt.CheckState.Unchecked
                )
                self.biome_list.addItem(item)
                self._biome_items[biome] = item

        self.biome_list.itemChanged.connect(self._biome_list_changed)
        card_layout.addWidget(self.biome_list)
        layout.addWidget(card, 1)

        hint = QLabel(
            "Role IDs are edited from Discord → Per-Biome Roles. "
            "Changes here are saved automatically to the active profile."
        )
        hint.setObjectName("cardHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        return page

    def _biome_list_changed(self, _item: QListWidgetItem):
        if self._loading:
            return
        profile = self._current_profile()
        profile.notify_biomes = [
            biome
            for biome, item in self._biome_items.items()
            if item.checkState() == Qt.CheckState.Checked
        ]
        self.schedule_save()

    # ---------- settings ----------

    def _settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.addWidget(
            self._brand_header(
                "Settings",
                "Anti-AFK timing, window matching, and the app theme are stored globally.",
            )
        )

        card, card_layout = self._card("Automation")
        grid = QGridLayout()

        self.afk_enabled = QCheckBox()
        self.afk_enabled.setChecked(
            self.config.anti_afk.enabled
        )
        self.afk_enabled.setToolTip(
            "Enable Anti-AFK. Off by default."
        )

        self.interval = QDoubleSpinBox()
        self.interval.setRange(1, 3600)
        self.interval.setDecimals(1)
        self.interval.setValue(self.config.anti_afk.interval_seconds)
        self.interval.setSuffix(" s")

        self.key = QLineEdit(self.config.anti_afk.anti_afk_key)
        self.key.setPlaceholderText("space")

        self.game_title = QLineEdit(self.config.anti_afk.game_title_regex)
        self.game_title.setPlaceholderText("Roblox|Sober|Sol's RNG")

        self.theme = QComboBox()
        self.theme.addItems(list(THEMES))
        self.theme.setCurrentText(self.config.theme)
        self.theme.currentTextChanged.connect(self._theme_changed)

        grid.addWidget(QLabel("Enable Anti-AFK"), 0, 0)
        grid.addWidget(self.afk_enabled, 0, 1)
        grid.addWidget(QLabel("Anti-AFK interval"), 1, 0)
        grid.addWidget(self.interval, 1, 1)
        grid.addWidget(QLabel("Anti-AFK key"), 2, 0)
        grid.addWidget(self.key, 2, 1)
        grid.addWidget(QLabel("Game title regex"), 3, 0)
        grid.addWidget(self.game_title, 3, 1)
        grid.addWidget(QLabel("Theme"), 4, 0)
        grid.addWidget(self.theme, 4, 1)
        card_layout.addLayout(grid)

        self.afk_enabled.stateChanged.connect(
            lambda _value: self.schedule_save()
        )

        save = QPushButton("Save All Settings")
        save.clicked.connect(self.save_all)
        card_layout.addWidget(save)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def _theme_changed(self, name: str):
        self._apply_theme(name)
        self.schedule_save()

    def _apply_theme(self, name: str, autosave: bool = True):
        QApplication.instance().setStyleSheet(
            THEMES.get(name, THEMES["midnight"])
        )
        self.config.theme = name
        if autosave:
            self.schedule_save()

    # ---------- persistence ----------

    def _collect(self):
        if hasattr(self, "profile_combo"):
            self._save_profile_fields()
        if hasattr(self, "afk_enabled"):
            self.config.anti_afk.enabled = (
                self.afk_enabled.isChecked()
            )

        if hasattr(self, "interval"):
            self.config.anti_afk.interval_seconds = self.interval.value()
            self.config.anti_afk.anti_afk_key = self.key.text().strip() or "space"
            self.config.anti_afk.game_title_regex = self.game_title.text().strip()

    def schedule_save(self):
        if not self._loading:
            self.save_timer.start()

    def _autosave(self):
        self._collect()
        self._save_now()

    def _save_now(self):
        try:
            save_config(self.config)
            self._update_dashboard_profile()
        except Exception as exc:
            self.log(f"Save failed: {exc}")

    def save_all(self):
        self._collect()
        self._save_now()
        self.log("All settings saved")

    # ---------- Anti-AFK ----------

    def _new_afk(self):
        return AntiAFKController(
            self.config.anti_afk.interval_seconds,
            self.config.anti_afk.anti_afk_key,
            self.config.anti_afk.game_title_regex,
            self.log,
        )

    def start_afk(self):
        if not self.config.anti_afk.enabled:
            self.afk_status.setText("DISABLED")
            self.log("Anti-AFK is disabled in Settings")
            return

        try:
            self.save_all()
            self.afk = self._new_afk()
            self.afk.start()
            self.afk_status.setText("RUNNING")
        except WindowError as exc:
            QMessageBox.warning(self, "Anti-AFK", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Anti-AFK", str(exc))

    def stop_afk(self):
        if self.afk:
            self.afk.stop(restore=True)
            self.afk = None
        self.afk_status.setText("STOPPED")

    def swap_game(self):
        try:
            self.save_all()
            if not self.afk:
                self.afk = self._new_afk()
            self.afk.swap_to_game()
        except Exception as exc:
            QMessageBox.warning(self, "Swap to Game", str(exc))

    def restore_window(self):
        if self.afk:
            self.afk.restore_previous_window()

    # ---------- Sober biome detection ----------

    def _biome_detected(self, biome: str):
        profile = self._current_profile()

        self.log(
            f"Sober detected biome: {biome}"
        )

        if not profile.enabled:
            self.log(
                f"Discord profile disabled; skipping {biome}"
            )
            return

        result = DiscordWebhook(
            profile
        ).send_biome(biome)

        if result.ok:
            self.log(
                f"Discord notification sent: {biome}"
            )
        else:
            self.log(
                f"Discord notification failed for {biome}: "
                f"{result.error or result.status or 'unknown error'}"
            )

    # ---------- Discord / misc ----------

    def test_webhook(self):
        self.save_all()
        result = DiscordWebhook(self._current_profile()).test()
        self.log(
            f"Webhook: {'OK' if result.ok else 'FAILED'} "
            f"{result.error or result.status or ''}"
        )

    def _update_dashboard_profile(self):
        if not hasattr(self, "dashboard_profile"):
            return
        profile = self._current_profile()
        self.dashboard_profile.setText(profile.name)
        self.dashboard_webhook.setText(
            profile.url if profile.url else "Webhook not configured"
        )

    def log(self, text: str):
        if hasattr(self, "log_box"):
            self.log_box.appendPlainText(text)

    def closeEvent(self, event):
        try:
            if self.afk:
                self.afk.stop(restore=True)
            self.biome_watcher.stop()
            self.save_timer.stop()
            self._collect()
            self._save_now()
        finally:
            event.accept()


def run() -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(LOGO)))
    win = MainWindow()
    win.show()
    return app.exec()
