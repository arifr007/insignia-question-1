from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import Config

engine = create_engine(Config.POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FinanceExpense(Base):
    __tablename__ = 'finance_expense'

    id = Column(Integer, primary_key=True, autoincrement=True)
    posting_period = Column(String(50))
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
    
    # Helper properties for backward compatibility and easier access
    @property
    def cost_center(self):
        return self.cost_center_id
    
    @property
    def amount(self):
        return self.company_code_currency_value
    
    @property
    def currency(self):
        return self.company_code_currency_key
    
    @property
    def month_year(self):
        # Convert fiscal year to month-year format
        if self.general_ledger_fiscal_year and self.posting_period:
            try:
                year = self.general_ledger_fiscal_year
                period = str(self.posting_period).zfill(2)
                return f"{year}{period}"
            except:
                return f"{self.general_ledger_fiscal_year}01"
        return None