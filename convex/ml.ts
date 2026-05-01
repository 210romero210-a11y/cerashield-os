import { action } from "../_generated/server";
import { v } from "convex/values";

// Action to call the ML service for a single coating record
export const updateHealthScoreForCoatingRecord = action({
  args: {
    coatingRecordId: v.id("coatingRecords"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // 1. Fetch the coating record
    const coatingRecord = await ctx.db.get(args.coatingRecordId);
    if (!coatingRecord) {
      throw new Error(`Coating record not found: ${args.coatingRecordId}`);
    }

    // 2. Fetch the customer to get ZIP code (already in coatingRecord)
    const { zipCode, applicationDate, coatingProductId } = coatingRecord;

    // 3. Fetch the coating product details
    const coatingProduct = await ctx.db.get(coatingProductId);
    if (!coatingProduct) {
      throw new Error(`Coating product not found: ${coatingProductId}`);
    }

    // 4. Fetch historical weather data for this ZIP code from applicationDate to now
    const now = Date.now();
    const weatherData = await ctx.db
      .query("weatherData")
      .filter((q) =>
        q.and(
          q.eq(q.field("zipCode"), zipCode),
          q.gte(q.field("date"), applicationDate),
          q.lte(q.field("date"), now)
        )
      )
      .collect();

    // 5. Prepare data for ML service
    const mlRequest = {
      coatingRecordId: args.coatingRecordId.toString(),
      applicationDate: applicationDate,
      coatingProduct: {
        id: coatingProductId.toString(),
        name: coatingProduct.name,
        productId: coatingProduct.productId,
        // Add any relevant fields from coatingProduct that affect degradation
        uvResistance: coatingProduct.uvResistance,
        expectedLifespanMonths: coatingProduct.expectedLifespanMonths,
        hydrophobicRating: coatingProduct.hydrophobicRating,
      },
      weatherData: weatherData.map((wd) => ({
        date: wd.date,
        uvIndex: wd.uvIndex,
        rainfall: wd.rainfall,
        temperatureAvg: wd.temperatureAvg,
      })),
    };

    // 6. Call the ML service (FastAPI) - TODO: replace with actual URL
    const mlServiceUrl = process.env.ML_SERVICE_URL || "http://localhost:8000/health-score";
    try {
      const response = await fetch(mlServiceUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // TODO: Add authentication if needed
          // "Authorization": `Bearer ${process.env.ML_SERVICE_TOKEN}`,
        },
        body: JSON.stringify(mlRequest),
      });

      if (!response.ok) {
        throw new Error(`ML service error: ${response.status} ${response.statusText}`);
      }

      const mlResponse = await response.json();

      // 7. Store the health score in the healthScores table
      await ctx.db.insert("healthScores", {
        coatingRecordId: args.coatingRecordId,
        timestamp: now,
        healthScore: mlResponse.current_health_score.score,
        healthGrade: mlResponse.current_health_score.grade,
        degradationPrediction: mlResponse.current_health_score.degradation_percentage,
        needsMaintenance: mlResponse.current_health_score.needs_maintenance,
        confidenceLower: mlResponse.current_health_score.confidence_interval?.lower,
        confidenceUpper: mlResponse.current_health_score.confidence_interval?.upper,
        // Optional: store the weather data used (we could store averages or just note we used recent data)
        uvIndexUsed: mlResponse.metadata?.data_points_used > 0 ? weatherData[weatherData.length - 1].uvIndex : null,
        rainfallUsed: mlResponse.metadata?.data_points_used > 0 ? weatherData[weatherData.length - 1].rainfall : null,
        temperatureUsed: mlResponse.metadata?.data_points_used > 0 ? weatherData[weatherData.length - 1].temperatureAvg : null,
      });

      // 8. Update the coating record with the latest health score for quick access
      await ctx.db.patch(args.coatingRecordId, {
        currentHealthScore: mlResponse.current_health_score.score,
        currentHealthGrade: mlResponse.current_health_score.grade,
        lastHealthScoreUpdate: now,
      });

      console.log(`Updated health score for coating record ${args.coatingRecordId}: ${mlResponse.current_health_score.score}`);
    } catch (error) {
      console.error(`Failed to update health score for coating record ${args.coatingRecordId}:`, error);
      throw error;
    }
  },
});

// Action to update health scores for all coating records in a ZIP code
export const updateHealthScoresForZipCode = action({
  args: {
    zipCode: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const { zipCode } = args;

    // Get all coating records for this ZIP code
    const coatingRecords = await ctx.db
      .query("coatingRecords")
      .filter((q) => q.eq(q.field("zipCode"), zipCode))
      .collect();

    console.log(`Updating health scores for ${coatingRecords.length} coating records in ZIP code ${zipCode}`);

    // Update each record sequentially (for now, we can parallelize later if needed)
    for (const record of coatingRecords) {
      await ctx.runAction(updateHealthScoreForCoatingRecord, {
        coatingRecordId: record._id,
      });
    }
  },
});