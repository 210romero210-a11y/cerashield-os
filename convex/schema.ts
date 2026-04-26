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
  }),

  coatingRecords: defineTable({
    customerId: v.id("customers"),
    vehicleInfo: v.string(), // e.g., "2020 Toyota Camry, VIN: ..."
    coatingProductId: v.id("coatings"),
    applicationDate: v.number(), // Timestamp
    warrantyEndDate: v.optional(v.number()),
    zipCode: v.string(), // For weather data lookup
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
});