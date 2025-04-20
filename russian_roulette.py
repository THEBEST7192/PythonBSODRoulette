"""
Simple Russian Roulette game in Python.
On a loss, calls trigger_blue_screen() where you can implement actual bluescreen logic.
"""
import random
import sys
import ctypes
import time

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
    print("PC: Well played, you win this round! Want to play again?")
    # You can customize this message as desired.

def play_roulette(chambers=6):
    # Randomly place a bullet in one of the chambers
    bullet = random.randint(0, chambers - 1)
    position = 0
    # Mode: solo or against PC
    vs_pc = input("Play against PC? [y/N]: ").strip().lower() == 'y'
    # 0 = user, 1 = PC
    turn = 0
    print(f"Welcome to Russian Roulette! There are {chambers} chambers.")
    print("Press Enter to pull the trigger, or type 'q' to quit.")

    while True:
        if vs_pc and turn == 1:
            print("PC is pulling the trigger...")
            time.sleep(1)
        else:
            choice = input("Pull the trigger? [Enter/q]: ").strip().lower()
            if choice == 'q':
                print("You backed out. Stay safe!")
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
    try:
        play_roulette()
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye.")
