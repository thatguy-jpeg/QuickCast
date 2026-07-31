import pandas as pd
import numpy as np
import sqlite3 as sql
from database_init import init
from pathlib import Path
from insertion import insert_records_orders

if not Path("./data/guest_data.csv").exists():

    #reads the guest data into a df
    
    df = pd.read_csv("./data/Retail-Supply-Chain-Sales-Dataset(Retails Order Full Dataset).csv", encoding="latin1")

    #takes only the needed columns 

    df = df[["Row ID", "Order ID", "Order Date", "Customer ID", "Customer Name", "Country", "City", "State", "Postal Code", "Retail Sales People", "Product ID", "Category", "Sub-Category", "Product Name", "Returned", "Sales", "Quantity", "Discount", "Profit"]]

    #changes the returned column into boolean

    df["Returned"] = df["Returned"].replace({"Not": 0, "Yes": 1})

    #splits the df into a guest and a demo dataset (80:20), one for public use, the other for demo use
        
    order_ids = df["Order ID"].unique()
    demo_ids = pd.Series(order_ids).sample(frac=0.2, random_state=42)
    demo = df[df["Order ID"].isin(demo_ids)]
    main = df[~df["Order ID"].isin(demo_ids)]

    main.to_csv('guest_data.csv', index=False)
    demo.to_csv('demo_data.csv', index=False)

df = pd.read_csv("./data/guest_data.csv", encoding="latin1")

#initializes the database using the init function from database_init.py

init()

con = sql.connect("./quickcast.db")
c = con.cursor()

c.execute("PRAGMA foreign_keys = ON;")

#uses the insert_records_orders function from insertion.py to insert the guest data

insert_records_orders(df=df, cur=c)

con.commit()
con.close()