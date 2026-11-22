import argparse
import random
import simulation

def run_game(iterations: int):
    # Hacky (for now), but any R_ prefixed stage is random.
    # We're also hard picking a goal to start

    rng = random.Random()
    s = simulation.Simulation()
    s = s.take_action(rng.choice(s.possible_actions()))
    print(f"Goal is {s.goal}")

    while s.reward is None:
        choice = rng.choice(s.possible_actions())
        print(choice)
        s=s.take_action(choice)
    
    print(s.reward)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", "-i", default=1000)
    parsed = parser.parse_args()

    run_game(parsed.iterations)

    pass

if __name__ == "__main__":
    main()
