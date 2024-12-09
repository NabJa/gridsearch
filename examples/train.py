import argparse
from time import sleep

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grid search runner")
    parser.add_argument("--param1", type=str)
    parser.add_argument("--param2", type=str)
    args = parser.parse_args()

    print(f"Running experiment with parameters: {args.param1}, {args.param2}")
    sleep(2)
