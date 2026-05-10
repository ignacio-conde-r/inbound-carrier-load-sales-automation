import asyncio
import csv
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db.database import init_db, AsyncSessionLocal
from app.models.load import Load


async def seed():
    await init_db()
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'db', 'seed_loads.csv')
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Load))
        if result.scalars().first():
            print("DB already seeded. Skipping.")
            return
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                load = Load(
                    load_id=row['load_id'],
                    origin=row['origin'],
                    destination=row['destination'],
                    pickup_datetime=datetime.strptime(row['pickup_datetime'], '%Y-%m-%d %H:%M'),
                    delivery_datetime=datetime.strptime(row['delivery_datetime'], '%Y-%m-%d %H:%M'),
                    equipment_type=row['equipment_type'],
                    loadboard_rate=float(row['loadboard_rate']),
                    weight=int(row['weight']),
                    commodity_type=row['commodity_type'],
                    miles=int(row['miles']),
                    notes=row['notes'],
                    num_of_pieces=int(row['num_of_pieces']) if row['num_of_pieces'] else 0,
                    dimensions=row['dimensions'],
                    status=row['status'],
                )
                session.add(load)
        await session.commit()
        print("Seeded 30 loads successfully.")


asyncio.run(seed())
