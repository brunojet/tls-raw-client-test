"""
TLS Raw Client - A Python library for low-level TLS diagnostics and proxy support.

This package provides tools for TLS connection testing, firewall diagnostics,
and proxy configuration in corporate environments.
"""

__version__ = "1.0.0"
__author__ = "Bruno Jet"
__email__ = "your.email@example.com"

from .tls_raw_client import TLSRawClient
from .proxy_tls_client import ProxyTLSClient
from .firewall_diagnostic import FirewallDiagnosticClient

__all__ = [
    'TLSRawClient',
    'ProxyTLSClient', 
    'FirewallDiagnosticClient'
]
