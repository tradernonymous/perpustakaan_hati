/** Loose env shape so tests can pass plain objects. process.env fits it. */
export type Env = Record<string, string | undefined>;
