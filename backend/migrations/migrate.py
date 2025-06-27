import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config
import os

# Database setup
Base = declarative_base()

class FinanceExpense(Base):
    __tablename__ = 'finance_expense'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    posting_period = Column(Integer)
    ledger = Column(String(10))
    company_code = Column(String(20))
    region = Column(String(100))
    profit_center_id = Column(String(50))
    profit_center_name = Column(String(255))
    funds_center = Column(String(50))
    cost_center_id = Column(String(50))
    cost_center_name = Column(String(255))
    general_ledger_account = Column(String(50))
    general_ledger_account_name = Column(String(255))
    fund = Column(String(50))
    functional_area = Column(String(50))
    functional_area_name = Column(String(255))
    general_ledger_fiscal_year = Column(String(10))
    account_type = Column(String(10))
    company_code_currency_key = Column(String(10))
    debit_credit_ind = Column(String(5))
    company_code_currency_value = Column(Float)
    processed_database_rows = Column(Integer)
    supplier = Column(String(255))
    reference = Column(String(255))
    document_header_text = Column(Text)
    po_description = Column(Text)
    transaction = Column(String(255))
    level_1 = Column(String(255))
    level_7 = Column(String(255))
    directorate = Column(String(255))
    entity = Column(String(255))
    remapping_directorate = Column(String(255))
    status = Column(String(50))

def migrate_data():
    csv_file = os.path.join(os.path.dirname(__file__), "data-ori.csv")
    
    # Column names for CSV (excluding 'id' since it's auto-incrementing)
    columns = [
        "posting_period", 
        "ledger",
        "company_code",
        "region",
        "profit_center_id",
        "profit_center_name",
        "funds_center",
        "cost_center_id",
        "cost_center_name",
        "general_ledger_account",
        "general_ledger_account_name",
        "fund",
        "functional_area",
        "functional_area_name",
        "general_ledger_fiscal_year",
        "account_type",
        "company_code_currency_key",
        "debit_credit_ind",
        "company_code_currency_value",
        "processed_database_rows",
        "supplier",
        "reference",
        "document_header_text",
        "po_description",
        "transaction",
        "level_1",
        "level_7",
        "directorate",
        "entity",
        "remapping_directorate",
        "status",
    ]
    
    # Create engine
    engine = create_engine(Config.POSTGRES_URI)
    
    # Check if table already exists
    inspector = inspect(engine)
    table_exists = inspector.has_table('finance_expense')
    
    if table_exists:
        print("✅ Table 'finance_expense' already exists")
        # Check if table has data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM finance_expense"))
            count = result.scalar()
            if count > 0:
                print(f"✅ Table already contains {count} rows. Skipping migration.")
                return
            else:
                print("Table exists but is empty. Proceeding with data import...")
    else:
        # Create tables
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully")
    
    # Read CSV data (skip header row since CSV headers are different)
    print("Reading CSV data...")
    df = pd.read_csv(csv_file, header=0, names=columns, skiprows=1)
    
    # Clean and process data
    print("Processing data...")
    
    # Handle missing values
    df = df.fillna('')
    
    # Clean numeric fields
    df['company_code_currency_value'] = df['company_code_currency_value'].astype(str).str.replace(',', '').replace('', '0')
    df['company_code_currency_value'] = pd.to_numeric(df['company_code_currency_value'], errors='coerce').fillna(0)
    
    # Clean string fields
    string_columns = [col for col in columns if col not in ['company_code_currency_value']]
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Import data to database in smaller batches
    print(f"Importing {len(df)} rows to database in batches...")
    
    batch_size = 500  # Smaller batch size to avoid parameter limits
    total_rows = len(df)
    total_batches = (total_rows + batch_size - 1) // batch_size
    
    for i in range(0, total_rows, batch_size):
        batch_num = (i // batch_size) + 1
        end_idx = min(i + batch_size, total_rows)
        batch_df = df.iloc[i:end_idx]
        
        print(f"Processing batch {batch_num}/{total_batches} (rows {i+1} to {end_idx})")
        
        try:
            batch_df.to_sql('finance_expense', engine, if_exists='append', index=False, method='multi')
            print(f"✅ Batch {batch_num} completed ({len(batch_df)} rows)")
        except Exception as e:
            print(f"❌ Error in batch {batch_num}: {e}")
            # Try inserting one by one for this batch
            print(f"Trying row-by-row insertion for batch {batch_num}...")
            for idx, row in batch_df.iterrows():
                try:
                    row.to_frame().T.to_sql('finance_expense', engine, if_exists='append', index=False)
                except Exception as row_error:
                    print(f"❌ Error inserting row {idx}: {row_error}")
    
    print("✅ Data migration completed successfully")
    print(f"✅ Total rows processed: {len(df)}")
    
    # Verify data
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM finance_expense"))
        count = result.scalar()
        print(f"✅ Verification: {count} rows in database")

if __name__ == "__main__":
    migrate_data()