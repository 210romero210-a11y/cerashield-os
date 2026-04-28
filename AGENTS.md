# CeraShield OS - Team Charter & Development Guidelines

## Team Structure & Roles
- **Engineering Manager (Orchestrator)**: Leads the team, breaks down requirements, delegates tasks, facilitates handoffs, reviews progress, ensures quality via GitHub issues/PRs, and maintains alignment with business goals.
- **cerashield-backend**: Handles all Convex schemas, mutations, workflows, crons, vector stores, Stripe integration, and backend data flows.
- **cerashield-frontend**: Builds polished shadcn/ui dashboards including AreaChart (health score decay + weather events), BarChart (recurring vs one-time revenue), and RadialBar (warranty compliance).
- **cerashield-ai**: Acts as the intelligent Health Report Agent that generates personalized customer reports and responses using the vector store and vehicle/weather data.
- **cerashield-ml**: Focuses exclusively on building and improving degradation forecasting models using Prophet/scikit-learn, weather data (especially UV and rainfall in San Antonio/sun-belt climates), and coating chemistry.

## Core Responsibilities
As Manager:
- Break complex features (such as the full lifecycle workflow: Stripe payment → Convex record → daily weather cron + ML health score update → AI-generated report → notification + booking loop) into small, well-defined tasks.
- Use delegation patterns and worktrees to enable safe parallel work across specialists.
- Maintain one shared GitHub repository for CeraShield OS. Create issues for tracking, enforce PR reviews, and ensure every meaningful change goes through proper version control.
- Facilitate clear handoffs: Require each specialist to return concise summaries including what was built, changed files, data dependencies for other team members, and any open questions.
- Monitor overall progress toward the Day 1 MVP and longer-term revenue roadmap.
- Make architectural decisions that balance reliability, scalability, and ease of maintenance — with special attention to accurate degradation predictions in high-UV markets like San Antonio.
- Enforce high standards: clean code, proper error handling, clear documentation, and alignment with the platform’s goal of warranty-linked lifecycle intelligence.

## Coding Standards
- **Convex**: Follow `convex/_generated/ai/guidelines.md` for correct API usage and patterns.
- **TypeScript**: Strict mode enabled, no `any` types without justification, proper interfaces for all public APIs.
- **Next.js**: Use app router, server components where beneficial, client components for interactivity.
- **shadcn/ui**: Follow the existing component structure and styling conventions.
- **Python (ML)**: PEP 8 compliance, type hints where possible, clear separation of concerns.
- **Git**: Commit messages follow conventional style (feat:, fix:, docs:, etc.). Branches: `feature/`, `fix/`, `chore/` prefixed.
- **Testing**: Write unit tests for critical logic. Backend: Convex test utilities. Frontend: Vitest/React Testing Library. ML: Pytest for model accuracy.

## Architecture Overview
```
Stripe Payment → Convex Webhook → CoatingRecord Table
                                    ↓
                           Weather Cron (daily)
                                    ↓
                  [UV/Rainfall/Temp] → ML Model → Health Score (0-100)
                                    ↓
                            Convex: HealthScore Table
                                    ↓
                            AI Report Generator
                                    ↓
                  Customer Notification (SMS/Email) → Booking Link
                                    ↓
                         Recurring Revenue Loop
```
- **Data Flow**: 
  1. Stripe payment triggers Convex action to create CoatingRecord
  2. Daily cron fetches weather data by ZIP code, stores in WeatherData table
  3. ML model (triggered by cron or on-demand) calculates health score using:
     - Coating chemistry (from vector store)
     - Historical weather (UV index, rainfall, temperature)
     - Time since application
  4. Health score stored in Convex
  5. AI agent retrieves coating knowledge + vehicle/weather data to generate personalized report
  6. Report + booking link sent via notification system
  7. Customer books recurring maintenance → new Stripe subscription → repeat

## ML ↔ Convex Integration Guidelines
To integrate the Python ML models (Prophet/scikit-learn) with the Convex/TypeScript backend, we propose the following approach:

### Option 1: Microservice (Recommended for MVP)
- Deploy the ML models as a lightweight FastAPI service.
- The service will expose endpoints matching the API specification in `ml/API_SPEC.md`.
- Convex actions will call this service via HTTP to get health scores and forecasts.
- This keeps the ML code in Python and avoids complex bindings.

### Option 2: Child Process (for initial testing)
- For early testing, Convex actions can spawn a Python child process to run the ML models.
- This is less efficient but easier to set up initially.
- We recommend moving to Option 1 as soon as possible.

### Data Exchange Format
- Use JSON for requests and responses.
- The ML service will accept:
  - Coating record ID (to fetch data from Convex via a helper function or by passing necessary fields)
  - OR directly: application date, coating product ID, zip code, and historical weather data.
- The ML service will return:
  - Current health score (0-100)
  - Health grade (Excellent, Good, Fair, Poor, Critical)
  - Maintenance flag (true if score < 65)
  - Optional forecast and confidence intervals

### Security and Performance
- The ML service should be deployed in a secure environment (e.g., same VPC or behind API gateway).
- Implement caching for recent health scores to reduce redundant computations.
- Use API keys or tokens for authentication between Convex and the ML service.

### File Locations
- ML models: `ml/models/prophet_model.py` and `ml/models/sklearn_model.py`
- Health score calculator: `ml/health_score_calculator.py`
- API specification: `ml/API_SPEC.md`
- Required input data: `ml/REQUIRED_INPUT_DATA.md`

## Handoff Protocols
When completing a task, each specialist must provide:
1. **Summary of Accomplishments**: What was built/changed
2. **Changed Files**: List of files modified/created
3. **Data Dependencies Provided**: What data/APIs are now available for other teams
4. **Open Questions/Blockers**: Anything needed from other teams
5. **Suggested Next Steps**: What the receiving team should do next

## GitHub Workflow
- All work happens in feature branches off `dev`
- Create GitHub issues from `day1-mvp-issues.md` and assign to specialists
- Use PR template: Summary, Related Issue, Testing Steps, Screenshots (if UI)
- Require at least one approval before merging
- Use Convex dev dashboard for testing backend changes
- Netlify/Vercel previews for frontend changes

## Day 1 MVP Focus
Turn one-time ceramic coating installs into predictable recurring maintenance revenue through:
Stripe payment → Convex record → daily weather cron + ML health score update → AI-generated report → notification + booking loop

## Success Metrics
- Complete end-to-end flow for one test customer
- Accurate health score degradation model (validated against known product lifespans)
- Dashboard showing health score trend and revenue metrics
- Automated personalized reports generated and delivered