import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  customers: defineTable({
    name: v.string(),
    email: v.optional(v.string()),
    phone: v.optional(v.string()),
    address: v.optional(v.string()),
  }),

  coatings: defineTable({
    name: v.string(),
    productId: v.string(), // External product ID from manufacturer or vector store
    description: v.optional(v.string()),
    // Additional fields for coating chemistry that affect degradation
    uvResistance: v.optional(v.number()), // 0-1 scale, higher = more resistant
    expectedLifespanMonths: v.optional(v.number()), // e.g., 24 for 2-year coating
    hydrophobicRating: v.optional(v.number()), // 0-1 scale
  }),

  coatingRecords: defineTable({
    customerId: v.id("customers"),
    vehicleInfo: v.string(), // e.g., "2020 Toyota Camry, VIN: ..."
    coatingProductId: v.id("coatings"),
    applicationDate: v.number(), // Timestamp
    warrantyEndDate: v.optional(v.number()),
    zipCode: v.string(), // For weather data lookup
    // Store current health score for quick access (updated by ML service)
    currentHealthScore: v.optional(v.number()),
    currentHealthGrade: v.optional(v.string()),
    lastHealthScoreUpdate: v.optional(v.number()), // Timestamp of last update
  }),

  weatherData: defineTable({
    zipCode: v.string(),
    date: v.number(), // Timestamp at start of day (UTC)
    uvIndex: v.number(),
    rainfall: v.number(), // in mm
    temperatureAvg: v.number(), // average temperature in Celsius
    // Index for quick lookup by zipCode and date
  }, (table) => [
    table.index("byZipCodeAndDate", ["zipCode", "date"]),
  ]),

  healthScores: defineTable({
    coatingRecordId: v.id("coatingRecords"),
    timestamp: v.number(), // When this score was calculated
    healthScore: v.number(), // 0-100
    healthGrade: v.string(), // Excellent, Good, Fair, Poor, Critical
    degradationPrediction: v.number(), // 0-100 (inverse of healthScore)
    needsMaintenance: v.boolean(), // True if healthScore < 65
    // Optional: store confidence intervals from ML model
    confidenceLower: v.optional(v.number()),
    confidenceUpper: v.optional(v.number()),
    // Weather data used for this calculation (for audit/traceability)
    uvIndexUsed: v.optional(v.number()),
    rainfallUsed: v.optional(v.number()),
    temperatureUsed: v.optional(v.number()),
  }, (table) => [
    table.index("byCoatingRecord", ["coatingRecordId"]),
    table.index("byTimestamp", ["timestamp"]),
  ]),

  maintenanceSchedules: defineTable({
    coatingRecordId: v.id("coatingRecords"),
    scheduledDate: v.number(),
    type: v.string(), // e.g., 'inspection', 'maintenance'
    completed: v.boolean(),
    notes: v.optional(v.string()),
  }),

  stripeCustomers: defineTable({
    customerId: v.id("customers"),
    stripeCustomerId: v.string(),
    stripeSubscriptionId: v.optional(v.string()),
  }),

  // Store notifications sent to customers
  notifications: defineTable({
    coatingRecordId: v.id("coatingRecords"),
    type: v.string(), // 'email', 'sms', 'push'
    recipient: v.string(), // email address or phone number
    subject: v.optional(v.string()),
    content: v.string(),
    sentAt: v.number(), // Timestamp
    status: v.string(), // 'sent', 'failed', 'delivered'
    // Reference to health score that triggered notification
    healthScoreId: v.optional(v.id("healthScores")),
  }, (table) => [
    table.index("byCoatingRecord", ["coatingRecordId"]),
    table.index("bySentAt", ["sentAt"]),
  ]),
});