# Tank War - Project Part 2

by Sarah, Ruby, Celina

## Setup Instructions

1.  **Open file:** Unzip and open the folder Tank-War in an IDE.
* **Important:** Sometimes, unzipping might create an extra parent folder.  For example, you might end up with `Tank-War/Tank-War/` instead of just `Tank-War/`.  Ensure you proceed to the next step *inside* the folder that **directly contains** the `main.py`, `sprites.py`, `resources/` etc. files.
3.  **Navigate to Project Directory:**  If you are using VScode, just open terminal inside VScode and it will automatically navigate. If you are using Terminal or Powershell, use the `cd` command to change into the project folder you just extracted. For example:
    ```bash
    cd path/to/your/Tank-War
    ```
    (Replace `path/to/your/Tank-War` with the actual path to the folder).
4.  **Virtual Environment (optional):** Run: 
	```bash
	python -m venv .venv
	.venv\Scripts\activate
	``` 
	You should see a (.venv) in command line.
5.  **Install Pygame:** Run the following command in your terminal to install the Pygame library (if you don't already have it):
    ```bash
    pip install pygame
    ```
    *(Recommendation: It's best practice to install packages within a Python virtual environment to avoid conflicts, but it's not strictly necessary for simply running this game).*

## Running the Game

After completing the setup, make sure your terminal is still in the project directory, and run the following command to start the game:

```bash
python main.py
```

## Playing instructions
1. **Player 1:** Use WASD to control directions and SPACE for shooting
2. **Player 2:** Use Direction Keys to control directions and ENTER for shooting
3. The player killed by another player will lose, player killed by enemy tank will respawn.
4. The player can regain HP by killing enemy tanks.
5. If no player is killed till 20 enemies are defeated, player who kills most enemy tanks will win.
6. Player who accidently shoot Boss Wall will lose immediately.
