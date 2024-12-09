# Grid Search Runner

This project provides a grid search runner for parallel computing using SLURM job scheduling. It allows you to define a grid of parameters, generate combinations, and run experiments in parallel.

## Project Structure

- `examples/`: Contains example configuration files and scripts.
- `gridsearch/`: Contains the main code for the grid search runner. 
  - `runner.py`: Contains the main logic for running the grid search.
  - `manager.py`: Contains the logic for managing the grid and database.


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/NabJa/gridsearch.git
    cd gridsearch
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
Run very customizable and parallelizable grid search experiments in three steps:

1. Define your grid parameters in a YAML file (e.g., `examples/grid.yml`):
    ```yaml
    param1:
      min: 0
      max: 10
      dist: linear
      num: 5

    param2:
      min: 10e-5
      max: 10e-2
      dist: log
      num: 5
    ```

2. Create a SLURM script to run your experiments (e.g., `examples/script.sh`):
    ```sh
    #!/bin/bash
    #SBATCH --job-name=python_job
    #SBATCH --output=output.txt
    #SBATCH --error=error.txt
    #SBATCH --time=01:00:00
    #SBATCH --partition=compute
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=1
    #SBATCH --mem=1G

    srun python examples/train.py "$@"
    ```

3. Create a Python script to run your experiments (e.g., `examples/train.py`):
    ```python
    import argparse
    from time import sleep

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Grid search runner")
        parser.add_argument("--param1", type=str)
        parser.add_argument("--param2", type=str)
        args = parser.parse_args()

        print(f"Running experiment with parameters: {args.param1}, {args.param2}")
        sleep(2)
    ```

4. Run the grid search runner:
    ```sh
    python gridsearch/runner.py examples/grid.yml examples/script.sh
    ```
