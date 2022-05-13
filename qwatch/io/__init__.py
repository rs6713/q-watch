"""IO Operations for SQL Database"""
import sqlalchemy


def _create_engine():
    """Wrapper to create sqlalchemy engine."""
    return sqlalchemy.create_engine(
        # 11.0'SQL+Server+Native+Client+11.0
        'mssql+pyodbc://localhost/Q-Watch?driver=ODBC+Driver+17+for+SQL+Server'
    )
