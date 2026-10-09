"""
Secure Diary - Password-protected, encrypted local daily diary application.
"""

from .vault import DiaryVault, DiaryVaultError, InvalidPasswordError, VaultLockedError

__all__ = ["DiaryVault", "DiaryVaultError", "InvalidPasswordError", "VaultLockedError"]
