# First Sprint Plan: CeraShield OS Day 1 MVP

## Sprint Goal
Establish the foundational pieces of the CeraShield OS platform:
1. Core data schema and storage (Convex)
2. Basic degradation forecasting model (ML)
3. Initial data flow between backend and ML components
4. Project setup and team coordination frameworks

## Parallel Workstreams (Can be delegated simultaneously)

### Workstream 1: Backend Foundation (cerashield-backend)
**Goal**: Create initial Convex schema and basic data structures
**Tasks**:
- Define CoatingRecord schema with fields for customer, vehicle, coating product, application date
- Create WeatherData schema for storing UV index, rainfall, temperature by ZIP code/date
- Set up basic Customer and StripeCustomer schemas
- Implement initial migration scripts
**Dependencies**: None (foundational)
**Deliverables**: 
- Updated `convex/schema.ts`
- Migration files in `convex/migrations/` (if applicable)
- Summary of data dependencies for ML and AI teams

### Workstream 2: ML Model Skeleton (cerashield-ml)
**Goal**: Build basic degradation forecasting model framework
**Tasks**:
- Create Python environment with Prophet and scikit-learn
- Develop basic Prophet model that takes UV exposure as input and outputs degradation over time
- Create simple scikit-learn model alternative for comparison
- Design Coating Health Score calculation (0-100 scale)
- Implement maintenance trigger logic (score < 65)
**Dependencies**: 
- Needs to know what data backend will provide (UV index, rainfall, temperature, coating type)
- Will provide API specification for backend to get health scores
**Deliverables**:
- `ml/models/prophet_model.py`
- `ml/models/sklearn_model.py` 
- `ml/health_score_calculator.py`
- API specification document for health score endpoints
- Summary of required input data from backend

### Workstream 3: Project Infrastructure & Coordination
**Goal**: Set up team workflows, documentation, and initial integration points
**Tasks**:
- Configure GitHub repository with issue templates, PR templates
- Set up the cerashield-team-orchestration skill for future reference
- Create initial documentation in README about team structure and workflow
- Define API contract between backend and ML services
- Set up initial Convex function structure for ML integration
**Dependencies**: 
- Needs schema definition from backend to define API contracts
- Needs model output specification from ML team
**Deliverables**:
- Updated README with team workflow documentation
- GitHub issue and PR templates
- API contract document between backend and ML
- Initial Convex function stubs for ML integration

## First Sprint Prioritization
**Priority 1 (Must have for sprint completion)**:
- Backend: Basic CoatingRecord and WeatherData schemas
- ML: Prophet model skeleton with health score calculation
- Coordination: API contract definition and initial integration points

**Priority 2 (Should have if time permits)**:
- Backend: Stripe webhook placeholder
- ML: Scikit-learn model alternative
- Coordination: GitHub templates and workflow documentation

**Priority 3 (Nice to have for later sprints)**:
- Backend: Full workflow implementation
- Frontend: Initial dashboard components
- AI: Report generation architecture

## Immediate Blocker
**GitHub Authentication Required**: Need to authenticate with GitHub to create issues, manage repository, and collaborate effectively.

## Suggested Next Steps
Once GitHub authentication is complete:
1. Create GitHub issues using the day1-mvp-issues.md as reference
2. Assign issues to appropriate specialist profiles
3. Begin first sprint development in parallel workstreams
4. Schedule regular sync points for handoffs and integration testing

## Communication Protocol
Each workstream lead should provide at end of work period:
1. Summary of accomplishments
2. List of changed files
3. Data dependencies provided to other teams
4. Open questions or blockers
5. Suggested next steps for receiving teams