# discord-timed-roles-bot
bot to apply a role after specifid timeframe has elapsed




# OKC Discord DB Migration

This repository contains a Python script for creating a MySQL database, a table, and stored procedures for an OKC Discord bot.

## Prerequisites

Ensure you have the following installed:

- Python 3.6 or higher
- Pip (Python package installer)

## Installation

1. Install the required packages:

   ```
   pip install python-dotenv mysql-connector-python
   ```

2. Create a `.env` file in the same directory as the `db_migrations.py` script with the following content:

   ```
   DB_HOST=localhost
   DB_USER=username
   DB_PASSWORD=password
   DB_NAME=okc_discord_db
   ```

   Replace the placeholders with your MySQL connection details.

## Running the Migration

1. In your terminal or command prompt, navigate to the directory containing the `db_migrations.py` script.

2. Run the migration script using Python:

   ```
   python db_migrations.py
   ```

   This command will execute the script, which will:

   - Load the database configuration from the `.env` file
   - Create the `okc_discord_db` database if it doesn't exist
   - Create the `users` table if it doesn't exist
   - Create the `add_user` and `update_user` stored procedures if they don't exist

   If everything is set up correctly, the script should run without any errors, and the migration will be applied to your MySQL server.
