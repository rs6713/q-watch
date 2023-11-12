"""IO Operations for SQL Database"""
import os
import sqlalchemy
from google.cloud.sql.connector import Connector


def _create_engine():
    """Wrapper to create sqlalchemy engine."""

    if(os.environ.get('PRODUCTION', False)):

        db_host = os.environ[
            "INSTANCE_HOST"
        ]  # e.g. '127.0.0.1' ('172.17.0.1' if deployed to GAE Flex)
        db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
        db_pass = os.environ["DB_PASSWORD"]  # e.g. 'my-db-password'
        db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
        db_port = os.environ["DB_PORT"]  # e.g. 3306

        # [END cloud_sql_mysql_sqlalchemy_connect_tcp]
        connect_args = {}
        # For deployments that connect directly to a Cloud SQL instance without
        # using the Cloud SQL Proxy, configuring SSL certificates will ensure the
        # connection is encrypted.
        if os.environ.get("DB_ROOT_CERT"):
            # e.g. '/path/to/my/server-ca.pem'
            db_root_cert = os.environ["DB_ROOT_CERT"]
            # e.g. '/path/to/my/client-cert.pem'
            db_cert = os.environ["DB_CERT"]
            db_key = os.environ["DB_KEY"]  # e.g. '/path/to/my/client-key.pem'

            ssl_args = {"ssl_ca": db_root_cert,
                        "ssl_cert": db_cert, "ssl_key": db_key}
            connect_args = ssl_args

        # [START cloud_sql_mysql_sqlalchemy_connect_tcp]
        return sqlalchemy.create_engine(
            # Equivalent URL:
            # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL.create(
                drivername="mssql+pytds",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name,
            ),
            # [END cloud_sql_mysql_sqlalchemy_connect_tcp]
            connect_args=connect_args,
            # [START cloud_sql_mysql_sqlalchemy_connect_tcp]
            # [START_EXCLUDE]
            # [START cloud_sql_mysql_sqlalchemy_limit]
            # Pool size is the maximum number of permanent connections to keep.
            pool_size=5,
            # Temporarily exceeds the set pool_size if no connections are available.
            max_overflow=2,
            # The total number of concurrent connections for your application will be
            # a total of pool_size and max_overflow.
            # [END cloud_sql_mysql_sqlalchemy_limit]
            # [START cloud_sql_mysql_sqlalchemy_backoff]
            # SQLAlchemy automatically uses delays between failed connection attempts,
            # but provides no arguments for configuration.
            # [END cloud_sql_mysql_sqlalchemy_backoff]
            # [START cloud_sql_mysql_sqlalchemy_timeout]
            # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
            # new connection from the pool. After the specified amount of time, an
            # exception will be thrown.
            pool_timeout=30,  # 30 seconds
            # [END cloud_sql_mysql_sqlalchemy_timeout]
            # [START cloud_sql_mysql_sqlalchemy_lifetime]
            # 'pool_recycle' is the maximum number of seconds a connection can persist.
            # Connections that live longer than the specified amount of time will be
            # re-established
            pool_recycle=1800,  # 30 minutes
            # [END cloud_sql_mysql_sqlalchemy_lifetime]
            # [END_EXCLUDE]
        )

        return sqlalchemy.create_engine(
            # Equivalent URL:
            # mssql+pytds://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL.create(
                # 'mssql+pyodbc',  # "mssql+pytds",  # 'mssql+pyodbc',  # "mssql+pytds",
                drivername="mssql+pytds",  # 'mssql+pymysql',
                username=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
                host=os.environ["DB_HOST"],
                port=os.environ["DB_PORT"],
            )
        )
        # initialize Connector object
        connector = Connector()

        def getconn():
            conn = connector.connect(
                'q-watch69:europe-west3:qwatch-sql',
                "pymysql",
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                db=os.environ["DB_NAME"]
            )
            return conn
        return sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )
    else:
        return sqlalchemy.create_engine(
            # 11.0'SQL+Server+Native+Client+11.0
            'mssql+pyodbc://localhost/Q-Watch?driver=ODBC+Driver+17+for+SQL+Server'
        )
