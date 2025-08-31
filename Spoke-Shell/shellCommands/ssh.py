import paramiko
import threading
import sys
import re

def run(args):
    if len(args) < 4:
        print("Usage: ssh <hostname> <username> <password> <port>")
        return

    hostname, username, password = args[0], args[1], args[2]
    try:
        port = int(args[3])
    except ValueError:
        print("Port must be an integer.")
        return

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Regex to strip ANSI escape sequences (colors, cursor moves, etc.)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    try:
        client.connect(hostname=hostname,
                       port=port,
                       username=username,
                       password=password)

        channel = client.invoke_shell()
        print(f"Connected to {hostname}. Type 'exit' or Ctrl-D to quit.\n")

        def recv_thread():
            while True:
                try:
                    data = channel.recv(1024)
                    if not data:
                        break
                    text = data.decode(errors='ignore')
                    clean_text = ansi_escape.sub('', text)
                    sys.stdout.write(clean_text)
                    sys.stdout.flush()
                except Exception:
                    break

        threading.Thread(target=recv_thread, daemon=True).start()

        while True:
            try:
                user_input = sys.stdin.readline()
                if not user_input:
                    break  # EOF (Ctrl-D)
                if user_input.strip().lower() == "exit":
                    break
                channel.send(user_input)
            except KeyboardInterrupt:
                break

        channel.close()

    except paramiko.AuthenticationException:
        print("Authentication failed. Check your username and password.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        client.close()