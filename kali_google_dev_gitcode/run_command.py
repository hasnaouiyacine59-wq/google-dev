import subprocess

CODESPACE_NAME = "your-codespace-name"  # get with: gh cs list
COMMAND = "ls -la"

result = subprocess.run(
    ["gh", "cs", "ssh", "-c", CODESPACE_NAME, "--", COMMAND],
    capture_output=True, text=True
)

print(result.stdout)
print(result.stderr)
