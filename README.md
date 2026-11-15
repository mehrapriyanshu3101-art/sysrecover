# SysRecover

An educational Flask platform that simulates OS and DBMS behaviour: CPU scheduling,
memory page replacement, transactions and locking, deadlock detection, crash
recovery and system diagnostics.

## Requirements

- Python 3.10+
- MySQL 8 (running on `localhost:3306`)

## Setup

1. Install the Python packages:

   ```
   pip install -r requirements.txt
   ```

2. Create the database and tables. Run `database/schema.sql` in MySQL Workbench,
   or from a terminal:

   ```
   mysql -u root -p < database/schema.sql
   ```

3. Copy the database settings into a `.env` file in the project root (this file is
   ignored by git):

   ```
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=sysrecover_db
   ```

4. Start the app:

   ```
   python app.py
   ```

5. Open <http://localhost:5000>, create a simulation run from the header, and use
   the sidebar to explore each module.

## How to use it

Most pages work on the run selected in the header dropdown. A typical demo:

1. **Process Management** – add a few processes (or auto-import real ones).
2. **CPU Scheduling** – run FCFS, SJF, SRTF, Round Robin or Priority.
3. **Transactions** – create transactions, read/write accounts A and B, commit or roll back.
4. **Resources & Locks** – add resources and grant locks to transactions.
5. **Deadlock Detection** – make two transactions wait on each other's resources,
   then detect and resolve the deadlock.
6. **Crash Recovery** – write some data, create a checkpoint, simulate a crash and recover.
7. **Event History** – review everything that happened in the run.
