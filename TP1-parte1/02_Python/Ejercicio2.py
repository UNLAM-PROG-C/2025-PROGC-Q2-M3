import os
import random
import time

PLAYER = 5   # Number of players
THROWS = 10  # Throws per player

def play(player):
    print(f"Player {player} enters the game (PID={os.getpid()})")
    total = 0
    for i in range(THROWS):
        roll = random.randint(1, 6)
        total += roll
        print(f"Player {player} rolled a {roll}")
        time.sleep(random.random())  # Simulates concurrency
    print(f"Player {player} finished with {total} points")
    os._exit(0)  # Ends the child process

if __name__ == "__main__":
    children = []
    for player in range(1, PLAYER + 1):
        pid = os.fork()
        if pid == 0:
            # Child code
            play(player)
        else:
            # Parent code
            children.append(pid)

    # Parent waits for all children to finish
    for pid in children:
        os.waitpid(pid, 0)

    print("All players have finished.")
