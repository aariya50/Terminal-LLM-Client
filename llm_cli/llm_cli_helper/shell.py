import os
import platform
from typing import List, Optional

class Shell:
    """
    A class to handle shell-related operations and information.

    This class provides methods to determine available shells, select a preferred shell,
    and identify the operating system.
    """

    def __init__(self):
        """
        Initialize the Shell object with available and preferred shells.
        """
        self._available_shells: List[str] = self._get_available_shells()
        self._preferred_shells: List[str] = self._get_preferred_shells()

    @staticmethod
    def _get_available_shells() -> List[str]:
        """
        Get a list of available shells from /etc/shells.

        Returns:
            List[str]: A list of available shell paths.
        """
        try:
            with open("/etc/shells") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            return []

    @staticmethod
    def _get_preferred_shells() -> List[str]:
        """
        Get a list of preferred shells, starting with the current shell.

        Returns:
            List[str]: A list of preferred shell paths.
        """
        return [os.environ.get("SHELL"), "/zsh", "/bash", "/sh"]

    @property
    def selected(self) -> Optional[str]:
        """
        Select the first available preferred shell.

        Returns:
            Optional[str]: The path of the selected shell, or None if no shell is available.
        """
        for preferred in self._preferred_shells:
            if not preferred:
                continue
            for available in self._available_shells:
                if available.endswith(preferred):
                    return available
        return self._available_shells[0] if self._available_shells else None

    @staticmethod
    def operating_system() -> str:
        """
        Determine the current operating system.

        Returns:
            str: The name of the operating system ('macOS', 'linux', 'windows', 'bsd', or 'posix').
        """
        system = platform.system().lower()
        if system == 'darwin':
            return 'macOS'
        elif system == 'linux':
            return 'linux'
        elif system == 'windows':
            return 'windows'
        elif system in ('freebsd', 'openbsd'):
            return 'bsd'
        else:
            return 'posix'

    @staticmethod
    def get_input(prompt: str) -> str:
        """
        Get user input with a given prompt.

        Args:
            prompt (str): The prompt to display to the user.

        Returns:
            str: The user's input, stripped of leading/trailing whitespace.
        """
        return input(prompt).strip()
