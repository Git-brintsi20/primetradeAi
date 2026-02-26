/**
 * Application configuration — centralised constants for the frontend.
 *
 * The backend URL can be overridden at build-time via the
 * NEXT_PUBLIC_API_URL environment variable.
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
