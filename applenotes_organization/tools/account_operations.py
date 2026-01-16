"""Account operations for Apple Notes MCP server."""

from typing import List, Dict, Any

from .applescript_runner import run_inline_applescript, parse_applescript_list


class AccountOperations:
    """Handle account-related operations with Apple Notes."""

    @staticmethod
    def list_all_accounts() -> List[str]:
        """
        Get a list of all accounts.

        Returns:
            List of account names
        """
        script = 'tell application "Notes" to get name of every account'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)

    @staticmethod
    def get_default_account() -> str:
        """
        Get the default account.

        Returns:
            Name of the default account
        """
        script = 'tell application "Notes" to get default account'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def list_folders_in_account(account_name: str) -> List[str]:
        """
        Get a list of folders in a specific account.

        Args:
            account_name: Name of the account

        Returns:
            List of folder names in the account
        """
        script = f'tell application "Notes" to get name of every folder of account "{account_name}"'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)
