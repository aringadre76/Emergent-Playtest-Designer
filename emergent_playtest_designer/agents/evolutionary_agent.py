"""Evolutionary algorithm agent for game exploration."""

import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action, AgentConfig


@dataclass
class Individual:
    """Represents an individual in the evolutionary algorithm."""
    genome: List[float]
    fitness: float = 0.0
    novelty_score: float = 0.0
    age: int = 0
    
    def __post_init__(self):
        """Initialize individual."""
        if not self.genome:
            self.genome = [random.uniform(-1, 1) for _ in range(20)]


class EvolutionaryAgent:
    """Agent using evolutionary algorithms for game exploration."""
    
    def __init__(self, config: AgentConfig):
        """Initialize evolutionary agent."""
        self.config = config
        self.population: List[Individual] = []
        self.population_size = 50
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
        self.generation = 0
        self.current_individual: Optional[Individual] = None
        self.current_episode = []
        
        self._initialize_population()
    
    def select_action(self, state: GameState) -> Action:
        """Select action based on current individual's genome."""
        if not self.current_individual:
            self._select_individual()
        
        return self._genome_to_action(self.current_individual.genome, state)
    
    def update(self, state: GameState, action: Action, reward: float, next_state: GameState) -> None:
        """Update agent with new experience."""
        self.current_episode.append({
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state
        })
        
        if len(self.current_episode) >= self.config.max_episode_length:
            self._evaluate_individual()
    
    def _initialize_population(self) -> None:
        """Initialize random population."""
        self.population = []
        for _ in range(self.population_size):
            genome = [random.uniform(-1, 1) for _ in range(20)]
            individual = Individual(genome=genome)
            self.population.append(individual)
        
        logger.info(f"Initialized population of {self.population_size} individuals")
    
    def _select_individual(self) -> None:
        """Select individual for current episode."""
        if not self.population:
            self._initialize_population()
        
        self.current_individual = random.choice(self.population)
        self.current_episode.clear()
    
    def _genome_to_action(self, genome: List[float], state: GameState) -> Action:
        """Convert genome to action."""
        action_type_index = int(abs(genome[0]) * 4) % 4
        action_types = ["key_press", "key_release", "mouse_click", "mouse_move"]
        action_type = action_types[action_type_index]
        
        parameters = self._genome_to_parameters(genome[1:], action_type)
        
        return Action(
            action_type=action_type,
            parameters=parameters,
            timestamp=state.timestamp,
            duration=max(0.1, abs(genome[5]) * 2.0)
        )
    
    def _genome_to_parameters(self, genome: List[float], action_type: str) -> Dict[str, Any]:
        """Convert genome to action parameters."""
        if action_type in ["key_press", "key_release"]:
            key_index = int(abs(genome[0]) * 8) % 8
            keys = ["w", "a", "s", "d", "space", "shift", "ctrl", "alt"]
            return {"key": keys[key_index]}
        
        elif action_type == "mouse_click":
            return {
                "button": "left" if genome[0] > 0 else "right",
                "x": int(abs(genome[1]) * 1920),
                "y": int(abs(genome[2]) * 1080)
            }
        
        elif action_type == "mouse_move":
            return {
                "x": int(abs(genome[1]) * 1920),
                "y": int(abs(genome[2]) * 1080),
                "delta_x": int(genome[3] * 200),
                "delta_y": int(genome[4] * 200)
            }
        
        return {}
    
    def _evaluate_individual(self) -> None:
        """Evaluate current individual's performance."""
        if not self.current_individual or not self.current_episode:
            return
        
        fitness = self._calculate_fitness()
        novelty_score = self._calculate_novelty_score()
        
        self.current_individual.fitness = fitness
        self.current_individual.novelty_score = novelty_score
        self.current_individual.age += 1
        
        logger.debug(f"Individual evaluated - Fitness: {fitness:.3f}, Novelty: {novelty_score:.3f}")
        
        self.current_individual = None
        self.current_episode.clear()
        
        if len([ind for ind in self.population if ind.fitness > 0]) >= self.population_size:
            self._evolve_population()
    
    def _calculate_fitness(self) -> float:
        """Calculate fitness based on episode performance."""
        if not self.current_episode:
            return 0.0
        
        total_reward = sum(exp["reward"] for exp in self.current_episode)
        episode_length = len(self.current_episode)
        
        states = [exp["state"] for exp in self.current_episode]
        position_change = self._calculate_position_change(states[0], states[-1])
        
        fitness = total_reward + (position_change * 0.1) + (episode_length * 0.01)
        return max(0.0, fitness)
    
    def _calculate_novelty_score(self) -> float:
        """Calculate novelty score for current episode."""
        if not self.current_episode:
            return 0.0
        
        states = [exp["state"] for exp in self.current_episode]
        final_state = states[-1]
        
        behavior_features = [
            final_state.player_position[0],
            final_state.player_position[1],
            final_state.player_position[2],
            final_state.player_health,
            sum(final_state.player_resources.values()),
            len(self.current_episode)
        ]
        
        novelty_scores = []
        for individual in self.population:
            if individual.fitness > 0:
                individual_features = individual.genome[:6]
                distance = np.linalg.norm(np.array(behavior_features) - np.array(individual_features))
                novelty_scores.append(distance)
        
        return np.mean(novelty_scores) if novelty_scores else 1.0
    
    def _calculate_position_change(self, initial_state: GameState, final_state: GameState) -> float:
        """Calculate position change in episode."""
        initial_pos = initial_state.player_position
        final_pos = final_state.player_position
        
        return ((final_pos[0] - initial_pos[0])**2 + 
                (final_pos[1] - initial_pos[1])**2 + 
                (final_pos[2] - initial_pos[2])**2)**0.5
    
    def _evolve_population(self) -> None:
        """Evolve population using genetic operators."""
        self.generation += 1
        
        evaluated_individuals = [ind for ind in self.population if ind.fitness > 0]
        if len(evaluated_individuals) < 2:
            logger.warning("Not enough evaluated individuals for evolution")
            return
        
        new_population = []
        
        evaluated_individuals.sort(key=lambda x: x.fitness + x.novelty_score, reverse=True)
        
        for i in range(self.elite_size):
            if i < len(evaluated_individuals):
                elite = Individual(
                    genome=evaluated_individuals[i].genome.copy(),
                    fitness=evaluated_individuals[i].fitness,
                    novelty_score=evaluated_individuals[i].novelty_score,
                    age=evaluated_individuals[i].age
                )
                new_population.append(elite)
        
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection(evaluated_individuals)
            parent2 = self._tournament_selection(evaluated_individuals)
            
            if random.random() < self.crossover_rate:
                child_genome = self._crossover(parent1.genome, parent2.genome)
            else:
                child_genome = parent1.genome.copy()
            
            child_genome = self._mutate(child_genome)
            
            child = Individual(genome=child_genome)
            new_population.append(child)
        
        self.population = new_population
        
        avg_fitness = np.mean([ind.fitness for ind in evaluated_individuals])
        avg_novelty = np.mean([ind.novelty_score for ind in evaluated_individuals])
        
        logger.info(f"Generation {self.generation} - Avg Fitness: {avg_fitness:.3f}, Avg Novelty: {avg_novelty:.3f}")
    
    def _tournament_selection(self, individuals: List[Individual], tournament_size: int = 3) -> Individual:
        """Select individual using tournament selection."""
        tournament = random.sample(individuals, min(tournament_size, len(individuals)))
        return max(tournament, key=lambda x: x.fitness + x.novelty_score)
    
    def _crossover(self, genome1: List[float], genome2: List[float]) -> List[float]:
        """Perform crossover between two genomes."""
        child_genome = []
        
        for i in range(len(genome1)):
            if random.random() < 0.5:
                child_genome.append(genome1[i])
            else:
                child_genome.append(genome2[i])
        
        return child_genome
    
    def _mutate(self, genome: List[float]) -> List[float]:
        """Mutate genome."""
        mutated_genome = genome.copy()
        
        for i in range(len(mutated_genome)):
            if random.random() < self.mutation_rate:
                mutation_strength = random.uniform(-0.2, 0.2)
                mutated_genome[i] = max(-1, min(1, mutated_genome[i] + mutation_strength))
        
        return mutated_genome
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        evaluated_individuals = [ind for ind in self.population if ind.fitness > 0]
        
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "evaluated_individuals": len(evaluated_individuals),
            "avg_fitness": np.mean([ind.fitness for ind in evaluated_individuals]) if evaluated_individuals else 0.0,
            "avg_novelty": np.mean([ind.novelty_score for ind in evaluated_individuals]) if evaluated_individuals else 0.0,
            "best_fitness": max([ind.fitness for ind in evaluated_individuals]) if evaluated_individuals else 0.0,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate
        }
    
    def reset(self) -> None:
        """Reset agent state."""
        self.current_individual = None
        self.current_episode.clear()
        self.generation = 0
        self._initialize_population()
