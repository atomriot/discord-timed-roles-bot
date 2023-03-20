##Disclaimer: This code was written by ChatGPT and the prompts it took to get it this far. The full dialog will eventually be included as part of the repo for documentorial purposes and to see the reason why some things were done the way the were.

# Discord Established User Bot

This Discord bot assigns the "Established User" role to members who have been on the server for a specified number of days (default is 30 days). The bot utilizes a MySQL database to store user join dates and roles. It checks for users who qualify for the role and assigns it if needed. The bot also logs the status of its nightly checks.

## Features

- Assigns "Established User" role after a specified number of days
- Checks when a user joins the server and logs the user to the database
- Monitors user role changes and ensures they have the correct role
- Runs a nightly check at a specified time to update users who qualify for the role
- Logs the status of the nightly checks in the database

## Requirements

- Python 3.6 or higher
- MySQL 5.6.41-84.1 or higher
- Discord.py (Pycord) library
- mysql-connector-python library
- python-dotenv library

## Installation

1. Clone the repository:
git clone https://github.com/atomriot/discord-timed-roles-bot.git

2. Navigate to the project folder:
cd discord-timed-roles-bot

3. Install the required Python packages:
pip install -r requirements.txt

4. Copy the `.env.sample` file to be `.env` and add your environment values

5. Run the `db_migrations.py` script to create the necessary database, tables, and stored procedures:
python db_migrations.py

## Usage

1. Start the bot:
python bot.py

The bot will now monitor user join events and role changes, and perform nightly checks to update user roles as needed.

## Notes

- The bot requires the appropriate permissions to manage roles on the Discord server.
- The bot should be placed higher in the role hierarchy than the "Established User" role in order to assign it to users.
