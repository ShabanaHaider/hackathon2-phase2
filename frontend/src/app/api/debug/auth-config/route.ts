import { NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

// SECURITY: Remove this endpoint after debugging or add authentication
export async function GET() {
  const diagnostics = {
    timestamp: new Date().toISOString(),
    environment: {
      NODE_ENV: process.env.NODE_ENV,
      BETTER_AUTH_URL: process.env.BETTER_AUTH_URL,
      BETTER_AUTH_SECRET_SET: !!process.env.BETTER_AUTH_SECRET,
      BETTER_AUTH_SECRET_LENGTH: process.env.BETTER_AUTH_SECRET?.length || 0,
      DATABASE_URL_SET: !!process.env.DATABASE_URL,
      DATABASE_URL_PREFIX: process.env.DATABASE_URL?.substring(0, 20) + "...",
    },
    database: {
      connectionAttempt: "pending",
      error: null as string | null,
      success: false,
    },
  };

  // Test database connection
  try {
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });

    const client = await pool.connect();

    // Test query
    const result = await client.query("SELECT NOW()");
    diagnostics.database.success = true;
    diagnostics.database.connectionAttempt = "successful";

    // Check if Better Auth tables exist
    const tablesResult = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
    `);

    (diagnostics.database as any).tables = tablesResult.rows.map((r: any) => r.table_name);

    client.release();
    await pool.end();
  } catch (error: any) {
    diagnostics.database.connectionAttempt = "failed";
    diagnostics.database.error = error.message;
  }

  return NextResponse.json(diagnostics, {
    headers: {
      "Cache-Control": "no-store",
    },
  });
}
