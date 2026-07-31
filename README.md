# QuickCast

![QuickCast dashboard](docs/screenshot.png)

## Table of Contents
- [Intro](#intro)
- [Directory Overview](#directory-overview)
- [Setup](#setup)
- [Capabilities](#capabilities)
- [Relevant Links and References](#relevant-links-and-references)
- [License](#license)

## Intro

QuickCast is a business intelligence tool that allows users to get overviews of their data easily. Specifically, it creates charts based on employees, locations, products, and customers. It also has a "forecast" feature, which generates a graph of orders for a specific product across all the dates it appears in the database.

QuickCast was designed to be simple, with most parts of it operating through buttons or counters. The only feature that requires typing is the forecast feature, which requires the product name to be entered manually.

The backend is a SQLite database with Flask, which integrates cleanly into the rest of the Python framework. SQLite also has the advantages of being customizable and lightweight, making it well-suited to the hosting platform used here. The buttons in QuickCast translate into different SQL queries, setting different conditions that are passed as arguments. This logic can be seen throughout the various scripts. QuickCast supports all CRUD operations in one form or another.

The general setup is a frontend hosted on GitHub Pages connecting to a backend hosted on PythonAnywhere. This allows for inexpensive hosting (being free), though it does not support heavy workloads. QuickCast is meant for demo and portfolio purposes, and should not be used commercially, as it does not have the capacity or the relevant security for handling user data.

## Directory Overview

### `data`
Contains three datasets:
- **Retail-Supply-Chain-Sales-Data** — the original flat Excel file obtained from Kaggle.
- **demo_data** and **guest_data** — processed versions of the original dataset, created through the `guest_insertion` script.

The processed files contain the following columns: Row ID, Order ID, Order Date, Customer ID, Customer Name, Country, City, State, Postal Code, Retail Sales People, Product ID, Category, Sub-Category, Product Name, Returned, Sales, Quantity, Discount, Profit.

If you would like to upload your own data, ensure it matches the proper types and that most fields are present, as the SQLite database is strictly typed with many required values.

### `docs`
Holds all files hosted by GitHub Pages. `index`, `style`, and `app` are standard frontend files, while `config` holds the PythonAnywhere API gateway address.

### `scripts`
Contains all the scripts and functions QuickCast depends on:
- **app** — the Flask backend, which uses the other scripts to communicate with the frontend.
- **database_init** — initializes the SQLite database, creating all tables and the `quickcast.db` file.
- **guest_insertion** — fills the newly created `quickcast.db` with `guest_data.csv`.
- **insertion** — provides routing logic as a reusable function for inserting data.
- **query_functions** — provides modular queries that adapt to frontend arguments, used once the database is filled.

**File dependencies:**
- `app` requires `query_functions` and `insertion`
- `database_init` has no dependencies
- `guest_insertion` requires `database_init` and `insertion`
- `insertion` has no dependencies
- `query_functions` has no dependencies

### `write_ups`
A miscellaneous folder containing papers related to this project's course. The papers discuss the approach taken and the design decisions made throughout the project.

## Setup

1. Download all required files (scripts, docs, data) and keep their organization as seen in the repository.
2. Choose a backend hosting platform (PythonAnywhere free tier was used here) and upload the files.
3. On that platform, run `guest_insertion` to create the database, populated with a guest user and sample data.
4. Run `app.py` and note the API address.
5. In `docs`, edit the `config` file to use that API address.
6. Host the frontend.
7. You should be good to go.

## Capabilities

QuickCast supports CRUD operations as follows:

- **Create** — users can upload data, provided it fits the database requirements.
- **Read** — users can query the database to create visualizations.
- **Update** — users can update individual rows of data.
- **Delete** — users can delete their account data.
- **Visualization** — creation of charts and common business metrics.

QuickCast was focused on database querying and application, so the following are outside its scope:

- Authentication
- Full protection against SQL injection
- Flexibility in data quality
- Security
- Multi-user support

### Dependencies and Libraries

Python 3.13 is suggested. The following should be installed in your virtual environment:

```
sqlite3
pandas
flask
flask_cors
numpy
pathlib
```

Note: versions are not pinned above; this project was built and tested using the latest standard releases of these libraries available for Python 3.13 at the time.

## Relevant Links and References

Demo video:
[https://youtu.be/dPKnpWezv9M?si=3HuDOvWes65Ih6Vl](https://youtu.be/dPKnpWezv9M?si=3HuDOvWes65Ih6Vl)

Original dataset:
[https://www.kaggle.com/datasets/shandeep777/retail-supply-chain-sales-dataset](https://www.kaggle.com/datasets/shandeep777/retail-supply-chain-sales-dataset)

Shandeep Raula's work is greatly appreciated.

## License

This project is licensed under the MIT License. See the `LICENSE` file in the repository for details.