
import asyncio

from equipment.fryer import Fryer

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)

from pymodbus.server import StartAsyncTcpServer


# CONFIGURAZIONE
HOST = "127.0.0.1"
PORT = 5020
UPDATE_INTERVAL = 1.0


# CREAZIONE FRIGGITRICE
fryer = Fryer()


# DATASTORE MODBUS
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 10),
)

context = ModbusServerContext(
    slaves=store,
    single=True,
)


def publish_data():

    # I valori sono convertiti in interi a 16 bit.
    # Il registro 40010 (offset 9) è riservato ai comandi.

    values = [
        round(fryer.current_l1_a * 100),
        round(fryer.current_l2_a * 100),
        round(fryer.current_l3_a * 100),
        round(fryer.power_kw * 100),
        round(fryer.energy_kwh * 100),
        round(fryer.oil_temperature * 10),
        int(fryer.is_on),
        int(fryer.is_heating),
        round(fryer.temperature_setpoint * 10),
    ]

    store.setValues(3, 0, values)


async def simulation_loop():

    previous_command = 0

    print("Simulatore Ambach 44422 avviato")

    while True:

        # LETTURA COMANDO ON/OFF
        command = store.getValues(
            3, 9, count=1
        )[0]

        if command != previous_command:

            if command == 1:
                fryer.turn_on()
                print("COMANDO MODBUS: ACCENSIONE")

            elif command == 0:
                fryer.turn_off()
                print("COMANDO MODBUS: SPEGNIMENTO")

            previous_command = command

        # LETTURA SETPOINT
        setpoint_register = store.getValues(
            3, 8, count=1
        )[0]

        fryer.set_temperature(
            setpoint_register / 10
        )

        # AGGIORNAMENTO MODELLO
        fryer.update(UPDATE_INTERVAL)

        # PUBBLICAZIONE REGISTRI
        publish_data()

        await asyncio.sleep(UPDATE_INTERVAL)


async def main():

    # Valori iniziali
    store.setValues(3, 8, [1800])
    store.setValues(3, 9, [0])

    print("=" * 50)
    print("MARINE KITCHEN SIMULATOR")
    print("Modbus TCP Server")
    print(f"Indirizzo: {HOST}")
    print(f"Porta: {PORT}")
    print("Unit ID: 1")
    print("=" * 50)

    # Avvio simulazione in background
    asyncio.create_task(simulation_loop())

    # Avvio server Modbus
    await StartAsyncTcpServer(
        context=context,
        address=(HOST, PORT),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nServer Modbus arrestato")
