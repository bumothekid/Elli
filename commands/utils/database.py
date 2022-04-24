import sqlite3

def readOne(columns: str, table: str, where: str = "", values: list = None) -> tuple | None:
    """
    Reads a single row and returns a tuple or None

    Parameters
    -----------
    columns: :class:`str`
        The name(s) of the column(s) to read
    table: :class:`str`
        The name of the table to read from
    where: :class:`str`
        Optional conditions from with column to read
    values: :class:`list`
        Optional values from with column to read
    """
    if values is None: values = []

    if not isinstance(values, list): values = [values]

    whereArray = where.split(' ')
    where = ""
    for i, item in enumerate(whereArray):
        if item == "": continue
        if i == 0: where += f"WHERE {item} = ?"; continue

        where += f" AND {item} = ?"

    db = sqlite3.connect("database.db")
    c = db.cursor()

    c.execute(f"SELECT {columns} FROM {table} {where}", values)
    return c.fetchone()

def readAll(columns: str, table: str, where: str = "", values: list = None) -> list[tuple]:
    """
    Reads multiple rows from the database and returns a list of tuples

    Parameters
    -----------
    columns: :class:`str`
        The name(s) of the column(s) to read
    table: :class:`str`
        The name of the table to read from
    where: :class:`str`
        Optional conditions from with column to read
    values: :class:`list`
        Optional values from with column to read
    """
    if values is None: values = []
    if not isinstance(values, list): values = [values]

    whereArray = where.split(' ')
    where = ""
    for i, item in enumerate(whereArray):
        if item == "": continue
        if i == 0: where += f"WHERE {item} = ?"; continue
        where += f" AND {item} = ?"

    db = sqlite3.connect("database.db")
    c = db.cursor()

    c.execute(f"SELECT {columns} FROM {table} {where}", values)
    return c.fetchall()

def insert(table: str, columns: str, values: list):
    """
    Inserts a new row in the database and returns nothing

    Parameters
    -----------
    table: :class:`str`
        The name of the table to read from
    columns: :class:`str`
        The name(s) of the column(s) to read
    values: :class:`list`
        The values to insert in the row
    """

    if not isinstance(values, list): values = [values]

    valueString = ""
    for i in range(len(values)):
        if str(values[i]).lower() == "null":
            values.pop(i)
            valueString += "NULL" if i == 0 else ", NULL"
            continue
        if i == 0: valueString += "?"; continue
        valueString += ", ?"
        

    db = sqlite3.connect("database.db")
    c = db.cursor()
    
    c.execute(f"INSERT INTO {table}({columns}) VALUES({valueString})", values)
    db.commit()

def update(table: str, columns: str, where: str = "", values: list = None):
    """
    Updates a table row and returns nothing

    Parameters
    -----------
    table: :class:`str`
        The name of the table to update from
    columns: :class:`str`
        The name(s) of the column(s) to read
    where: :class:`str`
        The condition wich row should be updated
    values: :class:`list`
        The values to update the row with
    """
    if values is None: values = []
    if not isinstance(values, list): values = [values]

    whereArray = where.split(' ')
    where = ""
    for i, item in enumerate(whereArray):
        if item == "": continue
        if i == 0: where += f"WHERE {item} = ?"; continue
        where += f" AND {item} = ?"

    columnsArray = columns.split(' ')
    columns = ""
    for i, column in enumerate(columnsArray):
        if str(values[i]).lower() == "null":
            values.pop(i)
            columns += f"{column} = NULL" if i == 0 else f" AND {column} = NULL"
            continue
        if i == 0: columns += f"{column} = ?"; continue
        columns += f" AND {column} = ?"


    db = sqlite3.connect("database.db")
    c = db.cursor()

    c.execute(f"UPDATE {table} SET {columns} {where}", values)
    db.commit()

def delete(table: str, where: str, values: list):
    """
    Deletes a table row and returns nothing

    Parameters
    -----------
    table: :class:`str`
        The name of the table to delete from
    where: :class:`str`
        The conditions of the row being deleted
    values: :class:`list`
        The values of conditions
    """

    if not isinstance(values, list): values = [values]

    whereArray = where.split(' ')
    where = ""
    for i, item in enumerate(whereArray):
        if i == 0: where += f"{item} = ?"; continue
        where += f" AND {item} = ?"

    db = sqlite3.connect("database.db")
    c = db.cursor()

    c.execute(f"DELETE FROM {table} WHERE {where}", values)
    db.commit()

