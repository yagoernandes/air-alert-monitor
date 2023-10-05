import chromedriver_binary
import time

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.chrome.options import Options

from datetime import datetime
from datetime import timedelta

from database.database import Database

import os

from dotenv import load_dotenv

load_dotenv()


class AirAlertMonitor:
    _from = os.getenv("FROM")
    to = os.getenv("TO")
    adults = os.getenv("ADULTS")
    kids = os.getenv("KIDS")
    babies = os.getenv("BABIES")
    going_date = os.getenv("GOING_DATE")
    return_date = os.getenv("RETURN_DATE")
    monitor_enabled = os.getenv("MONITOR_ENABLED")
    monitor_interval = os.getenv("MONITOR_INTERVAL")
    monitor_log_file = os.getenv("MONITOR_LOG_FILE")
    _class = os.getenv("CLASS")

    def get_url(self):
        return f"https://123milhas.com/v2/busca?de={self._from}&para={self.to}&adultos={self.adults}&criancas={self.kids}&bebes={self.babies}&ida={self.going_date}&volta={self.return_date}&classe={self._class}"

    def start_monitoring(self):
        options = Options()

        options.add_argument("headless")

        driver = webdriver.Chrome(options=options)
        driver.get(self.get_url())

        going_date = datetime.strptime(self.going_date, "%d-%m-%Y")
        return_date = datetime.strptime(self.return_date, "%d-%m-%Y")

        try:
            database = Database()
            database.create_researches_table()

            print(
                f'\nBuscando passagens de ida {going_date.strftime("%d/%m/%Y")} ({self._from}) e volta {return_date.strftime("%d/%m/%Y")} ({self.to})'
            )
            inicio_busca = datetime.now()
            WebDriverWait(driver, 50).until(
                Ec.presence_of_all_elements_located((By.CLASS_NAME, "scale-in"))
            )

            print(
                f"Busca concluída em {str((datetime.now() - inicio_busca).total_seconds())} segundos"
            )
            prices = driver.find_elements(
                By.XPATH, '//p[@class[contains(.,"price-details__text")]]//span[2]'
            )
            prices = map(
                lambda _price: int(_price.text.replace(".", "").strip()), prices
            )

            for price in prices:
                database.create_research(
                    _from=self._from,
                    to=self.to,
                    going_date=going_date.strftime("%Y-%m-%d"),
                    return_date=return_date.strftime("%Y-%m-%d"),
                    price=price,
                )
                print(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {self._from}->{self.to} para o dia {self.going_date} e retorno {self.return_date} com o valor de {str(price)}"
                )
                # if monitor log file is setted with a valid file, write the log
                if self.monitor_log_file:
                    with open(self.monitor_log_file, "a") as file:
                        file.write(
                            f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {self._from}->{self.to} para o dia {self.going_date} e retorno {self.return_date} com o valor de {str(price)}\n"
                        )

        except Exception as e:
            print(e)
        finally:
            driver.quit()
            going_date = going_date + timedelta(days=1)

            end_date = datetime.strptime(os.getenv("RETURN_DATE"), "%d-%m-%Y")

            diff = end_date - going_date

            if diff.days > 15:
                self.going_date = going_date.strftime("%d-%m-%Y")
            else:
                # RESET
                self.going_date = os.getenv("GOING_DATE")

            if self.monitor_enabled:
                print("Aguardando " + str(self.monitor_interval) + " segundos...")

                time.sleep(int(self.monitor_interval))

                self.start_monitoring()


air_alert_monitor = AirAlertMonitor()
air_alert_monitor.start_monitoring()
