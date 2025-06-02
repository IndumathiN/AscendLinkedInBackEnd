import sqlite3

# Define your path (absolute or relative)
db_path = "./database/linkedInAutomation.db"

# Connect to the database (this creates it if it doesn't exist)
conn = sqlite3.connect(db_path)

# Optional: create a table
cursor = conn.cursor()
cursor.execute("""CREATE TABLE resumes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  gender TEXT,
  location TEXT,
  skills TEXT,
  experience TEXT,
  education TEXT,
  demographics TEXT,
  language TEXT,
  links TEXT,
  salary TEXT,
  travel TEXT,
  certification TEXT,
  missing_information TEXT,
  filename TEXT,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
  
)""")



# Commit and close
conn.commit()
conn.close()
