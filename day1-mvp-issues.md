# Day 1 MVP GitHub Issues Plan

## Backend Issues (cerashield-backend)
1. **Create Convex schema for CoatingRecord** - Define tables for customers, coatings, weather data, maintenance schedules
2. **Implement Stripe payment processing webhook** - Handle one-time install payments and setup for recurring payments
3. **Build weather data fetching cron** - Daily job to fetch UV index, rainfall, temperature data by ZIP code
4. **Create vector store for coating SKUs** - Store and retrieve knowledge about Gyeon, Gtechniq, IGL, XPEL products
5. **Implement coating lifecycle workflow** - Connect Stripe payment → Convex record → scheduled milestones
6. **Build ML model integration API** - Endpoints to get/update health scores from ML models
7. **Create customer notification system** - Prepare framework for SMS/email notifications

## Frontend Issues (cerashield-frontend)
1. **Set up shadcn/ui dashboard layout** - Create main dashboard shell with navigation
2. **Implement AreaChart component** - Health score decay over time with weather event overlays
3. **Build BarChart component** - Recurring maintenance revenue vs one-time install revenue
4. **Develop RadialBar component** - Fleet warranty compliance visualization
5. **Create customer portal view** - Page for customers to see their personalized health reports
6. **Implement real-time data fetching** - Use Convex React hooks for live updates
7. **Add loading states and error handling** - Ensure robust UX

## AI Issues (cerashield-ai)
1. **Design Health Report Agent architecture** - Define how AI generates personalized reports
2. **Implement vector store integration** - Retrieve coating chemistry knowledge for reports
3. **Create report generation prompts** - Templates for different customer segments/coating types
4. **Build contextual messaging system** - Generate SMS/email content with booking links
5. **Develop response personalization logic** - Tailor reports based on vehicle data, ZIP code, health score
6. **Implement brand voice consistency** - Ensure all communications match CeraShield tone
7. **Create report delivery framework** - Prepare for integration with notification system

## ML Issues (cerashield-ml)
1. **Build Prophet model skeleton** - Basic time-series forecasting for coating degradation
2. **Implement scikit-learn model alternative** - Compare/contrast with Prophet approach
3. **Create Coating Health Score algorithm** - 0-100 scale based on UV, rainfall, temperature, chemistry
4. **Develop maintenance trigger logic** - Automatically flag when score < 65
5. **Integrate San Antonio/sun-belt weather patterns** - Special handling for high UV environments
6. **Connect coating chemistry data** - Use vector store to adjust degradation rates by product
7. **Set up model retraining pipeline** - Framework for improving accuracy over time