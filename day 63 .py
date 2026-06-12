# snake, water, gun solution
import random
import msvcrt  # For Windows (works on Windows only)
import sys

# Cross-platform key detection using built-in modules only
def get_key_windows():
    """Get key press on Windows without Enter key"""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        try:
            return key.decode('utf-8').lower()
        except:
            return None
    return None

def game():
    print("=" * 40)
    print("     WELCOME TO SNAKE-WATER-GUN")
    print("=" * 40)
    print("Rules:")
    print("  Snake vs Water  -> Snake drinks Water (Snake wins)")
    print("  Water vs Gun    -> Gun drowns in Water (Water wins)")
    print("  Gun vs Snake    -> Gun shoots Snake (Gun wins)")
    print("  Same choices    -> Tie")
    print("=" * 40)
    print("\n🎮 CONTROLS:")
    print("  Press 'S' key for Snake 🐍")
    print("  Press 'W' key for Water 💧")
    print("  Press 'G' key for Gun 🔫")
    print("  Press 'Q' key to Quit the game")
    print("=" * 40)
    
    choices_map = {
        's': 'snake',
        'w': 'water', 
        'g': 'gun'
    }
    
    choice_icons = {'snake': '🐍', 'water': '💧', 'gun': '🔫'}
    
    user_score = 0
    comp_score = 0
    rounds = 0
    
    print("\n⏰ Game starting in 3 seconds...")
    import time
    time.sleep(3)
    print("Ready! Press S, W, or G to play!\n")
    
    while True:
        print(f"\n--- Round {rounds + 1} ---")
        print(f"Score: You {user_score} : {comp_score} Computer")
        print("\nPress S (Snake🐍), W (Water💧), G (Gun🔫), or Q (Quit): ")
        
        # Get key press without Enter (Windows only)
        key = None
        while key is None:
            key = get_key_windows()
            if key == 'q':
                print("\nQuitting game...")
                return
            elif key in choices_map:
                break
            elif key is not None:
                print(f"\n❌ Invalid key '{key.upper()}'! Please press S, W, G, or Q.")
                key = None
            time.sleep(0.1)
        
        user_choice = choices_map[key]
        
        # Computer choice
        comp_choice = random.choice(list(choices_map.values()))
        
        # Display choices
        print(f"\nYou pressed: {key.upper()} → {user_choice} {choice_icons[user_choice]}")
        print(f"Computer chose: {comp_choice} {choice_icons[comp_choice]}")
        
        # Determine winner
        if user_choice == comp_choice:
            print("Result: Tie! 🤝")
        elif (user_choice == 'snake' and comp_choice == 'water') or \
            (user_choice == 'water' and comp_choice == 'gun') or \
            (user_choice == 'gun' and comp_choice == 'snake'):
            print("Result: You win this round! 🎉")
            user_score += 1
        else:
            print("Result: Computer wins this round! 💻")
            comp_score += 1
        
        rounds += 1
        time.sleep(1)  # Small delay before next round
    
    # Final result
    print("\n" + "=" * 40)
    print("          GAME OVER")
    print("=" * 40)
    print(f"Total Rounds: {rounds}")
    print(f"Final Score - You: {user_score} | Computer: {comp_score}")
    
    if user_score > comp_score:
        print("🏆 Congratulations! You won the game! 🏆")
    elif comp_score > user_score:
        print("💻 Computer wins the game! Better luck next time. 💻")
    else:
        print("🤝 It's a tie overall! 🤝")
    
    print("=" * 40)

if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform == "win32":
        game()
    else:
        # Fallback to regular input for Mac/Linux
        print("Note: Instant key press only works on Windows.")
        print("Using standard input mode for Mac/Linux...\n")
        
        # Simple version with number input for Mac/Linux
        choices = ['snake', 'water', 'gun']
        choice_icons = {'snake': '🐍', 'water': '💧', 'gun': '🔫'}
        user_score = 0
        comp_score = 0
        rounds = 0
        
        print("=" * 40)
        print("     WELCOME TO SNAKE-WATER-GUN")
        print("=" * 40)
        
        while True:
            print(f"\n--- Round {rounds + 1} ---")
            print(f"Score: You {user_score} : {comp_score} Computer")
            print("\nChoose your option:")
            print("  1. Snake 🐍")
            print("  2. Water 💧")
            print("  3. Gun 🔫")
            print("  4. Quit the game")
            
            try:
                choice = input("\nEnter your choice (1/2/3/4): ")
                if choice == '4':
                    break
                choice = int(choice)
                if choice < 1 or choice > 3:
                    print("Invalid choice! Please enter 1, 2, or 3.")
                    continue
            except ValueError:
                print("Invalid input! Please enter a number.")
                continue
            
            user_choice = choices[choice - 1]
            comp_choice = random.choice(choices)
            
            print(f"\nYou chose: {user_choice} {choice_icons[user_choice]}")
            print(f"Computer chose: {comp_choice} {choice_icons[comp_choice]}")
            
            if user_choice == comp_choice:
                print("Result: Tie! 🤝")
            elif (user_choice == 'snake' and comp_choice == 'water') or \
                (user_choice == 'water' and comp_choice == 'gun') or \
                (user_choice == 'gun' and comp_choice == 'snake'):
                print("Result: You win this round! 🎉")
                user_score += 1
            else:
                print("Result: Computer wins this round! 💻")
                comp_score += 1
            
            rounds += 1
        
        print("\n" + "=" * 40)
        print("          GAME OVER")
        print("=" * 40)
        print(f"Total Rounds: {rounds}")
        print(f"Final Score - You: {user_score} | Computer: {comp_score}")
        
        if user_score > comp_score:
            print("🏆 Congratulations! You won the game! 🏆")
        elif comp_score > user_score:
            print("💻 Computer wins the game! Better luck next time. 💻")
        else:
            print("🤝 It's a tie overall! 🤝")
        
        print("=" * 40)