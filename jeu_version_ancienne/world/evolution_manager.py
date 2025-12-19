import numpy as np
import random

class EvolutionManager:
    def __init__(self):
        self.snapshots = {}
        self.last_simulated_minute = 0

    def get_total_minutes(self, days, hours, minutes):
        return int(days * 1440 + hours * 60 + minutes)

    def apply_evolution_rules(self, grid):
        """Organic, slow evolution with probability."""
        new_grid = grid.copy()
        rows, cols = grid.shape

        # PROBABILITY: Tiny chance per minute for a 'living' feel
        # 0.005 = 0.5% chance per tile per minute
        ERODE_CHANCE = 0.005

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                cell = grid[r, c]
                # If Grass (1)
                if cell == 1:
                    # Check 4 neighbors for water (0)
                    if grid[r - 1, c] == 0 or grid[r + 1, c] == 0 or grid[r, c - 1] == 0 or grid[r, c + 1] == 0:
                        if random.random() < ERODE_CHANCE:
                            new_grid[r, c] = 3  # Turn to sand
        return new_grid

    def simulate_forward(self, grid, start_min, end_min):
        current_step_grid = np.array(grid)

        for m in range(start_min + 1, end_min + 1):
            # Deterministic seed: Minute 10 always results in the same 'random' rolls
            random.seed(m)
            current_step_grid = self.apply_evolution_rules(current_step_grid)

            if m % 60 == 0 and m not in self.snapshots:
                self.snapshots[m] = np.copy(current_step_grid)

        # Reset seed so drawing/generation stays truly random
        random.seed(None)
        return current_step_grid.tolist()

    def update_world_to_current_time(self, current_grid, days, hours, minutes):
        current_total = self.get_total_minutes(days, hours, minutes)

        # Only process if time has actually moved
        if current_total == self.last_simulated_minute:
            return current_grid

        if current_total < self.last_simulated_minute:
            updated_grid = self.restore_from_past(current_total)
        else:
            updated_grid = self.simulate_forward(current_grid, self.last_simulated_minute, current_total)

        self.last_simulated_minute = current_total
        return updated_grid

    def restore_from_past(self, target_minute):
        past_snapshots = [m for m in self.snapshots.keys() if m <= target_minute]
        # Always default to snapshot 0 if nothing else exists
        closest_hour = max(past_snapshots) if past_snapshots else 0

        if closest_hour not in self.snapshots:
            return None  # Should not happen if you save snapshot[0] on start

        grid_at_snapshot = np.copy(self.snapshots[closest_hour])
        return self.simulate_forward(grid_at_snapshot, closest_hour, target_minute)