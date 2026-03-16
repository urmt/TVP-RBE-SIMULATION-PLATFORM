"""Cybernation Hub - Central AI Director for RBE Resource Allocation."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class PriorityLevel(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class SustainabilityMetrics:
    carbon_footprint: float
    renewable_ratio: float
    recyclability: float
    water_usage: float
    def calculate_score(self) -> float:
        score = self.renewable_ratio * 30 + self.recyclability * 25
        score += max(0, 25 - self.carbon_footprint / 10)
        score += max(0, 20 - self.water_usage / 100)
        return min(100, max(0, score))

@dataclass
class EquityMetrics:
    population_served: int
    current_allocation_per_capita: float
    minimum_required: float
    geographic_distribution: Dict[str, float]
    def calculate_equity_score(self) -> float:
        if self.population_served == 0:
            return 0.0
        if self.current_allocation_per_capita < self.minimum_required:
            return 20.0
        score = 50.0
        ratio = self.current_allocation_per_capita / self.minimum_required
        score += min(30, (ratio - 1) * 15)
        return min(100, score)

@dataclass
class AllocationDecision:
    resource_id: str
    requested_amount: float
    approved_amount: float
    priority: PriorityLevel
    sustainability_score: float
    equity_score: float
    decision_reason: str
    timestamp: datetime

class CybernationHub:
    def __init__(self, db_path: str = "rbe_resources.db"):
        self.db_path = Path(db_path)
        self.decision_history: List[AllocationDecision] = []
        self._init_hub_tables()
    
    def _init_hub_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hub_decisions (
                    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id TEXT NOT NULL,
                    requested_amount REAL NOT NULL,
                    approved_amount REAL NOT NULL,
                    priority TEXT NOT NULL,
                    sustainability_score REAL,
                    equity_score REAL,
                    decision_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scarcity_scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    resource_constraints TEXT,
                    active BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def evaluate_sustainability(self, resource_id: str, metrics: SustainabilityMetrics) -> float:
        return metrics.calculate_score()
    
    def evaluate_equity(self, resource_id: str, metrics: EquityMetrics) -> float:
        return metrics.calculate_equity_score()
    
    def make_allocation_decision(self, resource_id: str, requested_amount: float,
                                  priority: PriorityLevel, sustainability_metrics: SustainabilityMetrics,
                                  equity_metrics: EquityMetrics, scarcity_scenario: str = None) -> AllocationDecision:
        sus_score = self.evaluate_sustainability(resource_id, sustainability_metrics)
        eq_score = self.evaluate_equity(resource_id, equity_metrics)
        
        scarcity_multiplier = 1.0
        if scarcity_scenario:
            scarcity_multiplier = self._get_scarcity_multiplier(scarcity_scenario, resource_id)
        
        approved_amount = 0.0
        reason = ""
        
        if priority == PriorityLevel.CRITICAL:
            if eq_score >= 30:
                approved_amount = requested_amount * scarcity_multiplier
                reason = f"Critical priority approved. Equity: {eq_score:.1f}"
            else:
                approved_amount = requested_amount * 0.5 * scarcity_multiplier
                reason = f"Critical with equity concerns. Equity: {eq_score:.1f}"
        elif priority == PriorityLevel.HIGH:
            if sus_score >= 60 and eq_score >= 50:
                approved_amount = requested_amount * scarcity_multiplier
                reason = f"High priority approved. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
            elif sus_score >= 40 and eq_score >= 30:
                approved_amount = requested_amount * 0.7 * scarcity_multiplier
                reason = f"High priority partial. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
            else:
                approved_amount = requested_amount * 0.3 * scarcity_multiplier
                reason = f"High priority minimal. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
        elif priority == PriorityLevel.MEDIUM:
            if sus_score >= 70 and eq_score >= 60:
                approved_amount = requested_amount * 0.8 * scarcity_multiplier
                reason = f"Medium priority approved. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
            else:
                approved_amount = requested_amount * 0.4 * scarcity_multiplier
                reason = f"Medium priority reduced. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
        else:  # LOW
            if sus_score >= 80 and eq_score >= 70:
                approved_amount = requested_amount * 0.5 * scarcity_multiplier
                reason = f"Low priority approved. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
            else:
                approved_amount = 0
                reason = f"Low priority denied. SUS: {sus_score:.1f}, EQ: {eq_score:.1f}"
        
        decision = AllocationDecision(
            resource_id=resource_id,
            requested_amount=requested_amount,
            approved_amount=round(approved_amount, 2),
            priority=priority,
            sustainability_score=sus_score,
            equity_score=eq_score,
            decision_reason=reason,
            timestamp=datetime.now()
        )
        
        self.decision_history.append(decision)
        self._store_decision(decision)
        
        return decision
    
    def _get_scarcity_multiplier(self, scenario_id: str, resource_id: str) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT resource_constraints FROM scarcity_scenarios WHERE scenario_id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
            if row:
                constraints = json.loads(row[0])
                return constraints.get(resource_id, {}).get("multiplier", 1.0)
        return 1.0
    
    def _store_decision(self, decision: AllocationDecision) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO hub_decisions 
                   (resource_id, requested_amount, approved_amount, priority,
                    sustainability_score, equity_score, decision_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (decision.resource_id, decision.requested_amount,
                 decision.approved_amount, decision.priority.name,
                 decision.sustainability_score, decision.equity_score,
                 decision.decision_reason)
            )
            conn.commit()
    
    def create_scarcity_scenario(self, scenario_id: str, name: str,
                                  description: str, constraints: dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO scarcity_scenarios 
                       (scenario_id, name, description, resource_constraints)
                       VALUES (?, ?, ?, ?)""",
                    (scenario_id, name, description, json.dumps(constraints))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False


if __name__ == "__main__":
    print("Cybernation Hub module loaded successfully")
