from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
import random
from datetime import datetime, timedelta

# Define your database URL and create an engine
db_url = 'sqlite:///./instance/users.db'
engine = create_engine(db_url)

# Reflect existing table 'medicine' from the database
metadata = MetaData()
medicine_table = Table('park', metadata, autoload_with=engine)

# Function to generate data with realistic pram fluctuations
def generate_data(num_rows):
    Session = sessionmaker(bind=engine)
    session = Session()
    pram_values = []
    
    # Start date (June 30th, 2024)
    start_date = datetime(2024, 6, 30)
    
    # Generate pram values with fluctuations
    pram = random.uniform(0.8, 1.1)  # Initial pram value
    
    for i in range(num_rows):
        # Introduce some randomness and fluctuations
        pram += random.uniform(-0.025, 0.05)
        pram = max(0.5, min(2.0, pram))  # Clamp pram between 0.5 and 2.0
        
        # Create a data dictionary to insert into 'medicine' table
        data = {
            'date': start_date + timedelta(days=i),
            'val1': random.uniform(0.0, 100.0),
            'val2': random.uniform(0.0, 100.0),
            'pram': pram,
            'email': 'user@gmail.com'
        }
        
        # Insert the data into 'medicine' table
        ins = medicine_table.insert().values(data)
        session.execute(ins)
    
    # Commit all changes to the database
    session.commit()
    session.close()

# Generate 100 rows of data with realistic pram fluctuations
generate_data(100)
