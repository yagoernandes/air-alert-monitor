from mysql.connector import connect

import os

from dotenv import load_dotenv

load_dotenv()


class Database:
    connection = connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )

    def create_research(self, _from, to, price, going_date, return_date):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO researches (`from`, `to`, `price`, `going_date`, `return_date`, `created_at`) "
            "VALUES ('"
            + _from
            + "', '"
            + to
            + "', '"
            + str(price)
            + "', '"
            + going_date
            + "', '"
            + return_date
            + "', "
            "CURRENT_TIME())"
        )
        self.connection.commit()

    def create_researches_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS researches ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "`from` VARCHAR(255) NOT NULL,"
            "`to` VARCHAR(255) NOT NULL,"
            "price INT NOT NULL,"
            "going_date DATE NOT NULL,"
            "return_date DATE NOT NULL,"
            "created_at DATETIME NOT NULL"
            ")"
        )
        self.connection.commit()
