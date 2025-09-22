# Multi-Agent Explainer Architecture

## Overview

The Explainer Agent serves as the **universal translator** for the Bank Guardian AI system, converting technical events from multiple Guardian agents into human-readable explanations.

## Multi-Agent Event Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Financial       │    │   Explainer      │    │ Ops Guardian    │
│ Guardian        │───▶│   Agent          │◀───│ Agent           │
│                 │    │                  │    │                 │
│ • Fraud Events  │    │ • Event          │    │ • Scale Events  │
│ • Block Actions │    │   Correlation    │    │ • Health Events │
│ • Risk Analysis │    │ • Cross-Agent    │    │ • Performance   │
└─────────────────┘    │   Context        │    └─────────────────┘
                       │ • Multi-Audience │
                       │   Explanations   │
                       └──────────────────┘
                              ▲
                              │
                       ┌──────────────────┐
                       │ Coordinator      │
                       │ Agent (A2A)      │
                       │                  │
                       │ • Orchestration  │
                       │ • Conflict Res.  │
                       │ • Priority Mgmt  │
                       └──────────────────┘
```

## Event Types & Sources

### 1. Financial Events (Financial Guardian)
```json
{
  "event_type": "fraud_detection",
  "source_service": "financial-guardian",
  "severity": "high",
  "context": {
    "transaction_id": "tx_123",
    "user_id": "user_456", 
    "amount": 5000,
    "fraud_score": 0.95,
    "action_taken": "BLOCK"
  },
  "audience": "user",
  "correlation_id": "corr_789"
}
```

### 2. Operations Events (Ops Guardian - Future)
```json
{
  "event_type": "system_scaling",
  "source_service": "ops-guardian",
  "severity": "medium",
  "context": {
    "service_name": "ledgerwriter",
    "action": "scale_up",
    "from_replicas": 3,
    "to_replicas": 6,
    "trigger": "cpu_threshold",
    "prediction_confidence": 0.94
  },
  "audience": "operator",
  "correlation_id": "corr_789"
}
```

### 3. Coordination Events (Coordinator Agent - Future)
```json
{
  "event_type": "agent_coordination",
  "source_service": "coordinator-agent",
  "severity": "medium",
  "context": {
    "coordination_type": "priority_conflict",
    "involved_agents": ["financial-guardian", "ops-guardian"],
    "decision": "prioritize_fraud_investigation",
    "reasoning": "Active fraud investigation takes precedence",
    "affected_actions": ["pause_scaling", "maintain_evidence"]
  },
  "audience": "operator",
  "correlation_id": "corr_789"
}
```

## Multi-Agent Scenarios

### Scenario 1: Coordinated Fraud Response
```
1. Financial Guardian detects coordinated fraud attack
2. Coordinator Agent decides to pause all scaling operations
3. Ops Guardian receives pause instruction
4. Explainer Agent correlates all three events
5. Generates comprehensive explanation for operators
```

**Generated Explanation:**
```
🎯 Coordinated Security Response

Multi-Agent Action: Fraud investigation with infrastructure freeze

What happened:
• Financial Guardian detected coordinated fraud (confidence: 96%)
• Coordinator prioritized fraud investigation over performance
• Operations Guardian paused auto-scaling to preserve evidence
• All systems now in coordinated defensive mode

Impact: 
• 15 suspicious transactions blocked across 8 accounts
• Infrastructure scaling paused for estimated 20 minutes
• Evidence preservation enabled for forensic analysis

Next Steps: Monitor fraud investigation progress, resume scaling when cleared
```

### Scenario 2: Priority Conflict Resolution
```
1. Peak traffic surge detected (Ops Guardian wants to scale)
2. Simultaneous fraud alert (Financial Guardian wants to investigate)
3. Coordinator Agent resolves conflict (fraud takes priority)
4. Explainer Agent explains the decision to operations team
```

**Generated Explanation:**
```
⚖️ Agent Priority Resolution

Conflict: Peak traffic scaling vs. Active fraud investigation
Decision: Prioritized fraud investigation (estimated 10 minute delay)

Reasoning:
• Fraud investigation: 94% confidence, affects 12 accounts
• Traffic surge: 85% prediction, 15% performance impact acceptable
• Coordinator decision: Security over performance

Impact: 
• Response times may increase by ~200ms during investigation
• Fraud investigation takes precedence for resource allocation
• Auto-scaling will resume after fraud resolution

Estimated Resolution: 10-15 minutes
```

## Core Components

### 1. Multi-Agent Event Processor
```python
class MultiAgentEventProcessor:
    def __init__(self):
        self.event_buffer = {}  # correlation_id -> events
        self.correlation_window = 300  # 5 minutes
        self.agent_states = {}  # current state of each agent
    
    async def process_event(self, event: AgentEvent):
        # Check for correlated events
        correlated_events = await self.find_correlated_events(event)
        
        if correlated_events:
            # Multi-agent scenario
            return await self.generate_multi_agent_explanation(
                event, correlated_events
            )
        else:
            # Single agent event
            return await self.generate_single_agent_explanation(event)
```

### 2. Cross-Agent Context Enricher
```python
class CrossAgentContextEnricher:
    async def enrich_event(self, event: AgentEvent):
        """Enrich event with context from other agents"""
        
        # Get current state from all agents
        financial_state = await self.get_financial_guardian_state()
        ops_state = await self.get_ops_guardian_state()
        coordinator_state = await self.get_coordinator_state()
        
        # Add cross-agent context
        event.context.update({
            "financial_guardian_state": financial_state,
            "ops_guardian_state": ops_state,
            "coordinator_decisions": coordinator_state.get("recent_decisions", [])
        })
        
        return event
```

### 3. Agent Coordination Tracker
```python
class AgentCoordinationTracker:
    def __init__(self):
        self.active_coordinations = {}  # Track ongoing multi-agent actions
        self.agent_priorities = {}      # Current priority assignments
    
    async def track_coordination(self, event: AgentEvent):
        """Track multi-agent coordinations"""
        
        if event.correlation_id:
            if event.correlation_id not in self.active_coordinations:
                self.active_coordinations[event.correlation_id] = {
                    "events": [],
                    "start_time": datetime.now(),
                    "involved_agents": set()
                }
            
            coordination = self.active_coordinations[event.correlation_id]
            coordination["events"].append(event)
            coordination["involved_agents"].add(event.source_service)
```

## Explanation Templates

### Multi-Agent Templates
```python
multi_agent_templates = {
    "coordinated_response": """
🎯 Multi-Agent Coordination

Action: {{coordination_summary}}
Involved Agents: {{involved_agents|join(', ')}}
Trigger: {{primary_trigger}}

Sequence of Events:
{{event_timeline}}

Impact:
{{impact_summary}}

Coordination Status: {{coordination_status}}
""",
    
    "priority_conflict": """
⚖️ Agent Priority Resolution

Conflict: {{conflict_description}}
Decision: {{resolution_decision}}
Priority Given To: {{priority_agent}}

Reasoning:
{{resolution_reasoning}}

Impact:
{{impact_assessment}}

Duration: {{estimated_duration}}
""",
    
    "cross_agent_impact": """
🔄 Cross-Agent Impact

Primary Action: {{primary_action}} ({{primary_agent}})
Secondary Effects:
{{secondary_effects}}

Coordination Logic:
{{coordination_reasoning}}

Overall Impact: {{overall_impact}}
"""
}
```

## API Design

### Core Endpoints

#### Multi-Agent Event Processing
```
POST /explain/multi-agent-event
- Process events that involve multiple agents
- Correlate with recent events from other agents
- Generate comprehensive multi-agent explanations

POST /explain/coordination-event  
- Handle coordination decisions from Coordinator Agent
- Explain agent priority conflicts and resolutions
- Track ongoing multi-agent scenarios

GET /explain/agent-states
- Get current state of all Guardian agents
- Show active coordinations and priorities
- Provide system-wide status overview
```

#### Cross-Agent Context
```
GET /explain/correlations/{correlation_id}
- Get all events for a specific correlation ID
- Show the full multi-agent story
- Timeline of coordinated actions

POST /explain/agent-context
- Enrich events with cross-agent context
- Add current state from other agents
- Provide comprehensive situational awareness
```

## Integration Patterns

### 1. Event Correlation
```python
# All agents include correlation_id for related events
correlation_id = str(uuid4())

# Financial Guardian sends fraud event
await explainer_client.send_event({
    "event_type": "fraud_detection",
    "correlation_id": correlation_id,
    "context": fraud_analysis
})

# Coordinator Agent sends coordination event  
await explainer_client.send_event({
    "event_type": "agent_coordination", 
    "correlation_id": correlation_id,
    "context": coordination_decision
})

# Ops Guardian sends scaling pause event
await explainer_client.send_event({
    "event_type": "scaling_paused",
    "correlation_id": correlation_id, 
    "context": scaling_pause_reason
})
```

### 2. Agent State Sharing
```python
# Each agent registers its current state
await explainer_client.register_agent_state({
    "agent_name": "financial-guardian",
    "state": {
        "active_investigations": 3,
        "blocked_transactions": 15,
        "risk_level": "HIGH",
        "last_update": datetime.now()
    }
})
```

### 3. Priority Coordination
```python
# Coordinator Agent sends priority decisions
await explainer_client.explain_priority_decision({
    "conflict_type": "fraud_vs_scaling",
    "decision": "prioritize_fraud",
    "affected_agents": ["financial-guardian", "ops-guardian"],
    "reasoning": "Active fraud investigation takes precedence",
    "estimated_duration": "15 minutes"
})
```

## Benefits of Multi-Agent Architecture

### 1. Comprehensive Understanding
- Users get the **full picture** of what's happening
- Operators understand **cross-agent dependencies**
- Decisions are explained in **complete context**

### 2. Conflict Transparency  
- When agents have conflicting priorities, users understand **why**
- Operations team sees **trade-offs** being made
- **Reasoning** behind coordination decisions is clear

### 3. System-Wide Visibility
- **Single source of truth** for all system explanations
- **Consistent messaging** across all Guardian agents
- **Coordinated communication** strategy

## Implementation Priority

### Phase 1: Core Multi-Agent Processing ✅ (Design Complete)
- Event correlation by correlation_id
- Basic multi-agent explanation generation
- Cross-agent context enrichment

### Phase 2: Coordinator Integration (Next)
- Agent coordination event handling
- Priority conflict resolution explanations
- Cross-agent decision tracking

### Phase 3: Advanced Features (Future)
- Predictive explanations (explain actions before they happen)
- Multi-language support
- Learning from operator feedback

This architecture ensures the Explainer Agent can handle the full complexity of your multi-agent Bank Guardian AI system while providing clear, actionable explanations to both users and operators.
