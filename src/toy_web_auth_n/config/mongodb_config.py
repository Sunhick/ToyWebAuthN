"""
MongoDB Configuration Module

This module provides configuration settings for MongoDB connections.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class MongoDBConfig:
    """
    MongoDB configuration handler that loads settings from environment variables.

    Environment Variables:
        MONGODB_HOST: MongoDB server hostname (default: localhost)
        MONGODB_PORT: MongoDB server port (default: 27017)
        MONGODB_DB: MongoDB database name (default: webauthn_db)
        MONGODB_USER: MongoDB username (optional)
        MONGODB_PASSWORD: MongoDB password (optional)
        MONGODB_AUTH_SOURCE: MongoDB authentication database (default: admin)
        MONGODB_SSL: Enable SSL/TLS connection (default: False)
    """

    def __init__(self) -> None:
        """Initialize MongoDB configuration by loading environment variables."""
        load_dotenv()  # Load environment variables from .env file

        self.host: str = os.getenv('MONGODB_HOST', 'localhost')
        self.port: int = int(os.getenv('MONGODB_PORT', '27017'))
        self.database: str = os.getenv('MONGODB_DB', 'webauthn_db')
        self.username: Optional[str] = os.getenv('MONGODB_USER')
        self.password: Optional[str] = os.getenv('MONGODB_PASSWORD')
        self.auth_source: str = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        self.ssl: bool = os.getenv('MONGODB_SSL', 'false').lower() == 'true'

    def get_connection_url(self) -> str:
        """
        Build and return the MongoDB connection URL based on configuration.

        Returns:
            str: MongoDB connection URL
        """
        # Start with base URL
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
            url = f"mongodb://{auth}{self.host}:{self.port}/{self.database}"
            # Add authentication source if using auth
            url += f"?authSource={self.auth_source}"
        else:
            url = f"mongodb://{self.host}:{self.port}/{self.database}"

        # Add SSL if enabled
        if self.ssl:
            url += "&ssl=true" if "?" in url else "?ssl=true"

        return url

    def get_database_name(self) -> str:
        """
        Get the configured database name.

        Returns:
            str: Database name
        """
        return self.database
