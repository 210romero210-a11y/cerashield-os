# CeraShield OS: The Ceramic Coating Lifecycle Intelligence Platform

## Value Proposition
Warranty-linked, AI-driven platform tracking/predicting/monetizing ceramic coating lifecycles (degradation curves, UV exposure, hydrophobic decline) to turn one-time installs into recurring maintenance revenue. Targets detailers/shops with predictive Health Scores, milestone workflows, and dynamic pricing.

## Tech Stack
- **Frontend**: Next.js (App Router, TypeScript)
- **UI**: shadcn/ui + shadcn/ui Charts (AreaChart for decay curves with weather overlays, BarChart for recurring vs one-time revenue, RadialBar for warranty compliance)
- **Backend**: Convex (reactive queries/mutations, crons, workflows, file storage, vector store for coating knowledge base)
- **Day 1 Components**: Stripe (payments/subscriptions), Aggregate (charts), Workflow, Crons, File, Auth, AI Agent, Vector, Search, Notifications
- **Forecasting**: Open-source ML (Prophet or scikit-learn) for per-vehicle degradation models fed by daily weather (UV, rainfall, etc. per ZIP)

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

### Data Flow:
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

## Revenue Roadmap (Day 1 MVP Focus)
- **Seed Target**: $79/mo for 5 detailers (25 vehicles @ $3.16/vehicle/mo)
- **Phase 1**: Turn one-time ceramic coating installs into predictable recurring maintenance revenue
- **Phase 2**: Dynamic pricing based on health score and predictive maintenance needs
- **Phase 3**: Fleet management and enterprise pricing tiers

## Key Flows
- **Install Flow**: Stripe ceramic install payment → Convex write CoatingRecord/VehicleProfile (SKU, install date, warranty, ZIP)
- **Workflow**: Schedule 30-day/6-mo/12-mo check-ins
- **Cron**: Daily pull weather API per ZIP → update Coating Health Score (0-100) via ML model → Trigger notifications if <65
- **AI Agent + Vector**: Ingest proprietary coating KB (specs, cure times, warranties) → Generate personalized "Coating Health Report" on query or milestones, factoring local climate/car storage
- **Notifications**: SMS/email with score + one-click "Book Maintenance" (Stripe loyalty charge)
- **Charts in Aggregate**: 
  - AreaChart: Health score decay over time with weather event overlays
  - BarChart: Recurring maintenance revenue vs one-time install revenue
  - RadialBar: Fleet warranty compliance visualization

## Day 1 MVP Success Metrics
- Complete end-to-end flow for one test customer
- Accurate health score degradation model (validated against known product lifespans)
- Dashboard showing health score trend and revenue metrics
- Automated personalized reports generated and delivered

## Getting Started
1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (see .env.example)
4. Run Convex dev server: `npx convex dev`
5. Run Next.js dev server: `npm run dev`

## Project Structure
- `/app` - Next.js App Router pages and components
- `/components` - Reusable UI components (shadcn/ui)
- `/convex` - Convex backend (schemas, mutations, queries, actions, cron jobs)
- `/ml` - Machine learning models (Prophet/scikit-learn) and health score calculation
- `/public` - Static assets
- `/profiles` - Agent profiles and skills for AI orchestration

## Contributing
We use Conventional Commits and GitHub flow:
- Branch naming: `feature/`, `fix/`, `chore/` prefixed off `dev`
- Create GitHub issues from day1-mvp-issues.md
- PR template: Summary, Related Issue, Testing Steps, Screenshots (if UI)
- Require at least one approval before merging

## License
Proprietary - CeraShield OS