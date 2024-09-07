import os

class Shell:
    # Read the available shells from the /etc/shells file
    with open("/etc/shells") as f:
        AVAILABLE_SHELLS = [line.strip() for line in f if not line.startswith('#')]

    # Define preferred shells, prioritizing the user's current shell environment variable
    PREFERRED_SHELLS = [os.getenv("SHELL"), "/zsh", "/bash", "/sh"]

    @property
    def selected(self):
        # Select the shell based on the available shells and preferred order
        shell = self.AVAILABLE_SHELLS[0]
        found = False

        for preferred in self.PREFERRED_SHELLS:
            if not preferred:
                continue
            for available in self.AVAILABLE_SHELLS:
                if available.endswith(preferred):
                    found = True
                    shell = available
                    break
            if found:
                break

        return shell

    def operating_system(self):
        # Determine the operating system based on platform flags
        if os.name == 'nt':
            return "windows"
        elif os.uname().sysname == 'Darwin':
            return "macOS"
        elif os.uname().sysname == 'Linux':
            return "linux"
        elif os.uname().sysname == 'FreeBSD' or os.uname().sysname == 'OpenBSD':
            return "bsd"
        else:
            return "posix"

    def get_input(self, prompt):
        # Get input from the user with a prompt
        return input(prompt).strip()
