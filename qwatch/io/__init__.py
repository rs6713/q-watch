"""IO Operations for SQL Database"""
import sqlalchemy

def _create_engine():
  """Wrapper to create sqlalchemy engine."""
  return sqlalchemy.create_engine(
    'mssql+pyodbc://localhost/Q-Watch?driver=SQL+Server+Native+Client+11.0'
  )