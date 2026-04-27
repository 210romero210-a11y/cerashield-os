import { mutation, action } from "../_generated/server";
import { v } from "convex/values";

// Stub for weather cron - to be implemented with actual weather API
export const fetchWeatherData = action({
  args: {
    zipCode: v.string(),
    date: v.number(), // Unix milliseconds for the date
  },
  returns: v.null(), // Will return null for now
  handler: async (ctx, args) => {
    console.log(`Fetching weather data for ZIP ${args.zipCode} on date ${new Date(args.date)}`);
    
    // TODO: Replace with actual weather API call (OpenWeatherMap, WeatherAPI, etc.)
    // For now, we'll insert mock data
    
    // Mock weather data - in reality, this would come from an API
    const mockUvIndex = 5 + Math.random() * 5; // UV index between 5-10
    const mockRainfall = Math.random() * 10;   // Rainfall between 0-10mm
    const mockTemperature = 15 + Math.random() * 15; // Temperature between 15-30°C
    
    // Insert or update weather data for this ZIP code and date
    await ctx.db.insert("weatherData", {
      zipCode: args.zipCode,
      date: args.date,
      uvIndex: mockUvIndex,
      rainfall: mockRainfall,
      temperatureAvg: mockTemperature,
    });
    
    console.log(`Inserted mock weather data: UV=${mockUvIndex.toFixed(1)}, Rain=${mockRainfall.toFixed(1)}mm, Temp=${mockTemperature.toFixed(1)}°C`);
    
    // TODO: Trigger health score recalculation for affected coating records
    // This would query coatingRecords for this zipCode and call ML service
    
    return null;
  },
});

// Cron job wrapper - to be scheduled daily
export const weatherCron = mutation({
  handler: async (ctx) => {
    console.log("Running daily weather cron job");
    
    // TODO: Get list of unique ZIP codes from coatingRecords
    // For now, we'll use a hardcoded list for testing
    const testZipCodes = ["78201", "78209", "78229"]; // San Antonio area ZIPs
    
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Start of day in UTC
    const timestamp = today.getTime();
    
    for (const zipCode of testZipCodes) {
      await ctx.runAction(fetchWeatherData, {
        zipCode,
        date: timestamp,
      });
    }
    
    console.log("Weather cron job completed");
  },
});