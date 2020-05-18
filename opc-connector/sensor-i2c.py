import json
import sys
import threading
from time import sleep

from services.publisher import LocalClient

import FdsChargeController as FdsCC
import FdsSensorUnico      as FdsSS
import FdsDbConstants      as FdsDB

import FdsCommon as fds


DELAY      = 1.0
IS_RUNNING = True

DEFAULT_RESET_GPIO_NEO          = 39
DEFAULT_RESET_GPIO_C23          = 149


def mqtt_connection():
    global mqtt_client
    mqtt_client = LocalClient('sensor-i2c', 'localhost', 1883)
    mqtt_client.run()


def resetMcu(boardType, resetPin):

    if (boardType == "NEO"):
        gpios = [
            "178", "179", "104", "143", "142", "141", "140", "149", "105", "148",
            "146", "147", "100", "102", "102", "106", "106", "107", "180", "181",
            "172", "173", "182", "124",  "25",  "22",  "14",  "15",  "16",  "17",
            "18",   "19",  "20",  "21", "203", "202", "177", "176", "175", "174",
            "119", "124", "127", "116",   "7",   "6",   "5",   "4"]

        gpio = gpios[resetPin]

        try:
            with open("/sys/class/gpio/gpio" + gpio + "/direction", "w") as re:
                re.write("out")
            with open("/sys/class/gpio/gpio" + gpio + "/value", "w") as writes:
                writes.write("0")
                time.sleep(1.0)
                writes.write("1")
                time.sleep(1.0)
        except Exception as e:
                print(e)

    # for C23 we use PWM
    elif boardType == "C23":
        try:
            with open("/sys/class/pwm/pwmchip4/export", "w") as pwm:
                pwm.write("0")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/period", "w") as pwm:
                pwm.write("100")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/duty_cycle", "w") as pwm:
                pwm.write("100")
        except Exception as e:
            print(e)

        try:
            with open("/sys/class/pwm/pwmchip4/pwm0/enable", "w") as pwm:
                pwm.write("0")
                pwm.flush()
                time.sleep(1.0)
                pwm.write("1")
                pwm.flush()
        except Exception as e:
            print(e)


if __name__ == "__main__":

    mqtt_connection()

    boardType = "C23"

        arduino  = None

        ## initialize the MCU object
        try:
            print('Initializing MCU connection...')
            arduino = FdsSS.FdsSensor(isDebug = IS_MCU_IN_DEBUG_MODE, busId = BUS_I2C)
        except Exception as e:
            print(e)


        while IS_RUNNING:
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            ## get Data from MCUs
            for attempt in range(0, MCU_MAX_ATTEMPTS):
                # initialize the data structure for MCU da
                mcuData = dict()

                try:
                    mcuData  = arduino.getMcuData()
                    print("I2C read attempt " + str(attempt) + ": ok")
                    break
                except Exception as e:
                    mcuData = None
                    print("I2C read attempt " + str(attempt) + ": FAIL  " + str(e))


            ## if after all the cycles the mcu is stuck try reset
            if(mcuData == None):
                print("MCU RESET: MCU i2c probably stuck!")
                resetMcu( BOARD_TYPE, RESET_PIN )

        time.delay( DELAY )
