## Generally
The script is created to parse all criminals from the site https://state.sor.gbi.ga.gov/Sort_Public/ and obtain all possible data about them. All objects are saved to the database.


## Setup Database
If you want to see a structure of the database, you can see it in the file `offenders.py` (Path - `database/models/offenders.py`).

If you want to use Sqlite3.db, you don't need to do anything; just run the script. If you want to use a different database URL, you need to change the database settings in the file `settings.py` (Path - `database/settings.py`).

To set up a `PostgreSQL` database, you need to create a database and, in the settings.py file, change the database URL to your own.

Example URL for PostgreSQL: `asyncpg://postgres:pass@db.host:5432/somedb`

Example URL for SQLite (auto-create): `sqlite://database/db.sqlite3`

If you have any questions, you can refer to this documentation: `https://tortoise.github.io/databases.html#db-url`


## Config (settings.yaml)
1. `two_captcha_api_key` - API key for the service `https://2captcha.com`.
To get the api key, you need to register on the site `https://2captcha.com`, top up your balance with at least 1 dollar and get the api key in your account. 

Then you need to change the api key in the file `settings.yaml` (Path - `source folder`).
Replace the value of the `two_captcha_api_key` variable with your own.

2. `max_iterations` - The maximum number of iterations to parse criminals. Every iteration have 8-10 pages (80-100 criminals). 

This value is made so that the script can complete its work, since the site does not provide information about the number of pages or criminals. 

To change the value, you need to change the value of the `max_iterations` variable in the file `settings.yaml` (Path - `source folder`).


## Installation
1. Install Python 3.10 or higher. (`https://www.python.org/downloads/`)
2. Open the terminal and go to the folder with the script. (`cd "path/to/folder"`)
3. Create a venv: `python3 -m venv .venv`
4. Activate venv: `.venv\bin\activate`
3. Install the required libraries. `pip install -r requirements.txt`
4. Setup database. (See `Setup Database`)
5. Setup config. (See `Config (settings.yaml)`)
6. Run the script: `python3 main.py`

