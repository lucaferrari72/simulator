
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGroupBox,
    QPlainTextEdit,
)

from equipment.equipment_loader import create_equipment_manager

from simulation_engine import SimulationEngine

from scheduling.daily_schedule import DailySchedule
from scheduling.equipment_scheduler import EquipmentScheduler


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Marine Kitchen Simulator")
        self.resize(1200, 850)

        # =====================================
        # EQUIPMENT MANAGER
        # =====================================

        self.manager = create_equipment_manager()

        # =====================================
        # DAILY SCHEDULE
        # =====================================

        self.daily_schedule = DailySchedule()

        # =====================================
        # EQUIPMENT SCHEDULER
        # =====================================

        self.scheduler = EquipmentScheduler(
            self.manager,
            self.daily_schedule
        )

        # =====================================
        # SIMULATION ENGINE
        # =====================================

        self.engine = SimulationEngine(
            equipment_manager=self.manager,
            scheduler=self.scheduler,
            time_scale=self.daily_schedule.get_time_scale(),
            start_seconds=self.daily_schedule.get_start_seconds()
        )

        # =====================================
        # INTERFACE
        # =====================================

        self.create_interface()

        # =====================================
        # SIMULATION TIMER
        # =====================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_simulation
        )

        self.timer.start(1000)

        # Avvio simulazione dopo la creazione
        # completa dell'interfaccia

        self.engine.start()

        self.refresh_interface()

    # =========================================
    # INTERFACE
    # =========================================
    def restore_automatic(self):
        equipment_id = self.get_selected_id()

        if equipment_id is not None:
            self.manager.restore_automatic(equipment_id)
            self.scheduler.update(
                self.engine.simulation_time
            )
        self.refresh_interface()

    def create_interface(self):

        central = QWidget()

        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # =====================================
        # TITLE
        # =====================================

        title = QLabel(
            "MARINE KITCHEN SIMULATOR"
        )

        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px;
        """)

        layout.addWidget(title)

        # =====================================
        # GENERAL SUMMARY
        # =====================================

        summary_group = QGroupBox(
            "RIEPILOGO CUCINA"
        )

        summary_layout = QVBoxLayout()

        self.summary_label = QLabel()

        self.summary_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 8px;
        """)

        summary_layout.addWidget(
            self.summary_label
        )

        summary_group.setLayout(
            summary_layout
        )

        layout.addWidget(summary_group)

        # =====================================
        # SIMULATION STATUS
        # =====================================

        simulation_group = QGroupBox(
            "STATO SIMULAZIONE"
        )

        simulation_layout = QVBoxLayout()

        self.simulation_label = QLabel()

        self.simulation_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2E7D32;
            padding: 8px;
        """)

        simulation_layout.addWidget(
            self.simulation_label
        )

        self.scheduler_label = QLabel()

        self.scheduler_label.setStyleSheet("""
            font-size: 14px;
            padding: 5px;
        """)

        simulation_layout.addWidget(
            self.scheduler_label
        )

        simulation_group.setLayout(
            simulation_layout
        )

        layout.addWidget(simulation_group)

        # =====================================
        # SIMULATION CONTROLS
        # =====================================

        controls_group = QGroupBox(
            "CONTROLLO SIMULAZIONE"
        )

        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("AVVIA")

        self.pause_button = QPushButton("PAUSA")

        self.automation_button = QPushButton(
            "DISATTIVA AUTOMAZIONE"
        )

        self.start_button.clicked.connect(
            self.start_simulation
        )

        self.pause_button.clicked.connect(
            self.pause_simulation
        )

        self.automation_button.clicked.connect(
            self.toggle_automation
        )

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.automation_button)

        controls_group.setLayout(controls_layout)

        layout.addWidget(controls_group)

        # =====================================
        # EQUIPMENT SELECTION
        # =====================================

        selection_group = QGroupBox(
            "APPARECCHIATURE"
        )

        selection_layout = QVBoxLayout()

        self.equipment_combo = QComboBox()

        for equipment_id, equipment in self.manager.equipment.items():

            description = (
                f"{equipment_id} | "
                f"{getattr(equipment, 'manufacturer', 'N/D')} | "
                f"{getattr(equipment, 'model', 'N/D')}"
            )

            self.equipment_combo.addItem(
                description,
                equipment_id
            )

        self.equipment_combo.currentIndexChanged.connect(
            self.refresh_interface
        )

        selection_layout.addWidget(
            self.equipment_combo
        )

        selection_group.setLayout(
            selection_layout
        )

        layout.addWidget(selection_group)

        # =====================================
        # EQUIPMENT DATA
        # =====================================

        data_group = QGroupBox(
            "DATI APPARECCHIATURA SELEZIONATA"
        )

        data_layout = QVBoxLayout()

        self.data_display = QPlainTextEdit()

        self.data_display.setReadOnly(True)

        data_layout.addWidget(
            self.data_display
        )

        data_group.setLayout(data_layout)

        layout.addWidget(data_group)

        # =====================================
        # MANUAL EQUIPMENT CONTROLS
        # =====================================

        manual_group = QGroupBox(
            "COMANDI MANUALI OPERATORE"
        )

        manual_layout = QHBoxLayout()

        self.on_button = QPushButton(
            "ACCENSIONE MANUALE"
        )

        self.off_button = QPushButton(
            "SPEGNIMENTO MANUALE"
        )

        self.on_button.clicked.connect(
            self.turn_on
        )

        self.off_button.clicked.connect(
            self.turn_off
        )

        self.auto_button = QPushButton(
            "RIPRISTINA AUTOMATICO"
        )

        self.auto_button.clicked.connect(
            self.restore_automatic
)

        manual_layout.addWidget(self.on_button)
        manual_layout.addWidget(self.off_button)

        manual_group.setLayout(manual_layout)
        manual_layout.addWidget(self.auto_button)

        layout.addWidget(manual_group)

        # =====================================
        # FOOTER
        # =====================================

        footer = QLabel(
            "SIMULAZIONE SOFTWARE - "
            "NON COLLEGATA A MACCHINE REALI"
        )

        footer.setStyleSheet("""
            color: gray;
            padding: 8px;
        """)

        layout.addWidget(footer)

    # =========================================
    # SELECTED EQUIPMENT
    # =========================================

    def get_selected_id(self):

        return self.equipment_combo.currentData()

    # =========================================
    # MANUAL ON
    # =========================================

    def turn_on(self):

        equipment_id = self.get_selected_id()

        if equipment_id is not None:

            self.manager.turn_on(equipment_id)

        self.refresh_interface()

    # =========================================
    # MANUAL OFF
    # =========================================

    def turn_off(self):

        equipment_id = self.get_selected_id()

        if equipment_id is not None:

            self.manager.turn_off(equipment_id)

        self.refresh_interface()

    # =========================================
    # START
    # =========================================

    def start_simulation(self):

        self.engine.start()

        self.refresh_interface()

    # =========================================
    # PAUSE
    # =========================================

    def pause_simulation(self):

        self.engine.stop()

        self.refresh_interface()

    # =========================================
    # AUTOMATION
    # =========================================

    def toggle_automation(self):

        if self.scheduler.enabled:

            self.scheduler.disable()

        else:

            self.scheduler.enable()

            # Sincronizza subito gli stati
            # con l'orario simulato corrente

            self.scheduler.update(
                self.engine.simulation_time
            )

        self.refresh_interface()

    # =========================================
    # SIMULATION UPDATE
    # =========================================

    def update_simulation(self):

        self.engine.tick()

        self.refresh_interface()

    # =========================================
    # INTERFACE REFRESH
    # =========================================

    def refresh_interface(self):

        # =====================================
        # GENERAL SUMMARY
        # =====================================

        summary = self.manager.get_summary()

        self.summary_label.setText(

            f"Apparecchiature: "
            f"{summary['equipment_count']}    |    "

            f"Attive: "
            f"{summary['active_equipment']}    |    "

            f"Allarmi: "
            f"{summary['alarm_equipment']}\n"

            f"Potenza totale: "
            f"{summary['total_power_kw']:.3f} kW    |    "

            f"Energia totale: "
            f"{summary['total_energy_kwh']:.4f} kWh"
        )

        # =====================================
        # SIMULATION CLOCK
        # =====================================

        status = self.engine.get_status()

        hours = status["simulation_hour"]
        minutes = status["simulation_minute"]
        seconds = status["simulation_second"]

        running_text = (
            "ATTIVA"
            if status["running"]
            else "IN PAUSA"
        )

        self.simulation_label.setText(

            f"SIMULAZIONE {running_text} | "

            f"{hours:02d}:{minutes:02d}:{seconds:02d} | "

            f"VELOCITA': {self.engine.time_scale:.1f}x"
        )

        # =====================================
        # SCHEDULER STATUS
        # =====================================

        scheduler_status = self.scheduler.get_status()

        automation_text = (
            "ATTIVA"
            if scheduler_status["enabled"]
            else "DISATTIVATA"
        )

        self.scheduler_label.setText(

            f"AUTOMAZIONE: {automation_text} | "

            f"APPARECCHIATURE GESTITE: "
            f"{scheduler_status['equipment_count']} | "

            f"TRANSIZIONI: "
            f"{scheduler_status['transitions']}"
        )

        # =====================================
        # SELECTED EQUIPMENT DATA
        # =====================================

        equipment_id = self.get_selected_id()

        if equipment_id is not None:

            data = self.manager.get_equipment_data(
                equipment_id
            )

            category = self.scheduler.equipment_categories.get(
                equipment_id,
                "unknown"
            )

            lines = [
                f"ID: {equipment_id}",
                f"Categoria: {category}",
                ""
            ]

            for key, value in data.items():

                if isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)

                lines.append(
                    f"{key}: {formatted_value}"
                )

            self.data_display.setPlainText(
                "\n".join(lines)
            )

        else:

            self.data_display.clear()

        # =====================================
        # BUTTON STATES
        # =====================================

        self.start_button.setEnabled(
            not status["running"]
        )

        self.pause_button.setEnabled(
            status["running"]
        )

        self.automation_button.setText(
            "DISATTIVA AUTOMAZIONE"
            if scheduler_status["enabled"]
            else "ATTIVA AUTOMAZIONE"
        )

    # =========================================
    # CLOSE APPLICATION
    # =========================================

    def closeEvent(self, event):

        self.engine.stop()

        self.timer.stop()

        event.accept()


# =============================================
# MAIN
# =============================================

def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()

