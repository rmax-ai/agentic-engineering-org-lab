// Mock data for the dashboard demo — mirrors real pipeline output shapes

export type TaskStatus = "pending" | "classifying" | "running" | "verifying" | "reviewing" | "completed" | "failed";

export type DelegationDecision =
	| "auto_delegate"
	| "human_decompose_first"
	| "human_review_required"
	| "reject_unsafe"
	| "insufficient_context";

export type ReadinessRating = "not_ready" | "partially_ready" | "ready_with_caution" | "agent_ready";

export type PipelineStage = {
	id: string;
	label: string;
	status: "pending" | "active" | "pass" | "fail" | "skipped";
	icon: string;
	timestamp?: string;
	duration?: string;
};

export type Task = {
	id: string;
	title: string;
	description: string;
	status: TaskStatus;
	requester: string;
	priority: "low" | "medium" | "high" | "critical";
	createdAt: string;
	decision: DelegationDecision | null;
	affectedServices: string[];
	riskLevel: "low" | "medium" | "high";
};

export type TraceEvent = {
	id: string;
	type: string;
	timestamp: string;
	actor: "system" | "agent" | "human";
	summary: string;
	status: "pass" | "fail" | "info";
};

export type ServiceNode = {
	name: string;
	type: "service" | "library" | "worker";
	language: string;
	owner: string;
	riskLevel: "low" | "medium" | "high";
	readinessScore: number;
	dependencies: string[];
};

export type VerificationCheck = {
	name: string;
	status: "pass" | "fail" | "running";
	summary: string;
	duration: string;
};

export type ReviewFinding = {
	severity: "low" | "medium" | "high" | "blocker";
	category: string;
	message: string;
};

export const TASKS: Task[] = [
	{
		id: "task_001",
		title: "Add email validation to signup API",
		description: "Reject invalid email addresses during signup and update tests.",
		status: "completed",
		requester: "product_manager",
		priority: "medium",
		createdAt: "2026-07-05T09:00:00Z",
		decision: "auto_delegate",
		affectedServices: ["signup-api", "validation"],
		riskLevel: "medium"
	},
	{
		id: "task_002",
		title: "Disable payment verification for test users",
		description: "Allow test users to bypass Stripe verification in sandbox.",
		status: "failed",
		requester: "qa_engineer",
		priority: "high",
		createdAt: "2026-07-05T08:30:00Z",
		decision: "reject_unsafe",
		affectedServices: ["billing-api"],
		riskLevel: "high"
	},
	{
		id: "task_003",
		title: "Improve the onboarding flow",
		description: "Make onboarding smoother for new users.",
		status: "pending",
		requester: "designer",
		priority: "low",
		createdAt: "2026-07-05T10:15:00Z",
		decision: "human_decompose_first",
		affectedServices: ["signup-api", "notification-worker"],
		riskLevel: "low"
	},
	{
		id: "task_004",
		title: "Add rate limiting to notification worker",
		description: "Prevent notification spam by limiting to 10/second per user.",
		status: "running",
		requester: "sre",
		priority: "high",
		createdAt: "2026-07-05T11:00:00Z",
		decision: "auto_delegate",
		affectedServices: ["notification-worker"],
		riskLevel: "medium"
	},
	{
		id: "task_005",
		title: "Fix billing invoice total rounding",
		description: "VAT rounding causes 1-cent discrepancies in invoice totals.",
		status: "completed",
		requester: "finance",
		priority: "critical",
		createdAt: "2026-07-04T14:00:00Z",
		decision: "auto_delegate",
		affectedServices: ["billing-api", "validation"],
		riskLevel: "high"
	}
];

export const PIPELINE: PipelineStage[] = [
	{ id: "queued", label: "Queued", status: "pass", icon: "●", timestamp: "09:00:01", duration: "0.2s" },
	{ id: "classify", label: "Classify", status: "pass", icon: "◆", timestamp: "09:00:03", duration: "2.1s" },
	{ id: "sandbox", label: "Sandbox", status: "pass", icon: "⬡", timestamp: "09:00:05", duration: "3.4s" },
	{ id: "execute", label: "Execute", status: "pass", icon: "◇", timestamp: "09:03:45", duration: "3m40s" },
	{ id: "verify", label: "Verify", status: "pass", icon: "✓", timestamp: "09:04:10", duration: "25s" },
	{ id: "review", label: "Review", status: "pass", icon: "◉", timestamp: "09:04:22", duration: "12s" },
	{ id: "merge", label: "Ready", status: "pass", icon: "▲", timestamp: "09:04:23"}
];

export const PIPELINE_WITH_FAILURE: PipelineStage[] = [
	{ id: "queued", label: "Queued", status: "pass", icon: "●", timestamp: "09:00:01" },
	{ id: "classify", label: "Classify", status: "pass", icon: "◆", timestamp: "09:00:03" },
	{ id: "sandbox", label: "Sandbox", status: "pass", icon: "⬡", timestamp: "09:00:05" },
	{ id: "execute", label: "Execute", status: "pass", icon: "◇", timestamp: "09:02:30" },
	{ id: "verify", label: "Verify", status: "fail", icon: "✗", timestamp: "09:02:55" },
	{ id: "autofix", label: "Autofix", status: "pass", icon: "↻", timestamp: "09:03:40" },
	{ id: "verify2", label: "Verify", status: "pass", icon: "✓", timestamp: "09:04:05" },
	{ id: "review", label: "Review", status: "pass", icon: "◉", timestamp: "09:04:18" },
	{ id: "merge", label: "Ready", status: "pass", icon: "▲", timestamp: "09:04:20" }
];

export const TRACE_EVENTS: TraceEvent[] = [
	{ id: "evt_001", type: "task.created", timestamp: "09:00:01.002", actor: "system", summary: "Task received: Add email validation to signup API", status: "info" },
	{ id: "evt_002", type: "task.classified", timestamp: "09:00:03.150", actor: "system", summary: "Classification: auto_delegate (0.82 confidence). Intent: feature_change.", status: "pass" },
	{ id: "evt_003", type: "repo.scanned", timestamp: "09:00:04.210", actor: "system", summary: "Repo readiness: 82/100 (ready_with_caution). signup-api + validation.", status: "pass" },
	{ id: "evt_004", type: "sandbox.created", timestamp: "09:00:05.100", actor: "system", summary: "Sandbox sandbox_123 provisioned. Bounded scope: signup-api/** + validation/**", status: "info" },
	{ id: "evt_005", type: "context_pack.created", timestamp: "09:00:05.800", actor: "system", summary: "Context pack assembled: 5 files, 2 AGENTS.md, architecture extract", status: "info" },
	{ id: "evt_006", type: "agent.started", timestamp: "09:00:06.000", actor: "agent", summary: "Patch-only agent invoked. Model: gpt-5.4. Timeout: 300s.", status: "info" },
	{ id: "evt_007", type: "agent.completed", timestamp: "09:03:45.300", actor: "agent", summary: "Agent completed. 3 files modified, 0 errors.", status: "pass" },
	{ id: "evt_008", type: "verification.completed", timestamp: "09:04:10.500", actor: "system", summary: "Verification: 3/3 passed (tests ✓, lint ✓, typecheck ✓)", status: "pass" },
	{ id: "evt_009", type: "review.completed", timestamp: "09:04:22.100", actor: "system", summary: "AI review: 0 blocking, 1 suggestion (edge case: whitespace trimming)", status: "pass" },
	{ id: "evt_010", type: "final_report.created", timestamp: "09:04:23.050", actor: "system", summary: "Recommendation: ready for human review. Diff hash: a3f2b9c1.", status: "pass" }
];

export const VERIFICATION_CHECKS: VerificationCheck[] = [
	{ name: "Unit Tests", status: "pass", summary: "12/12 passed", duration: "8.2s" },
	{ name: "Lint (ruff)", status: "pass", summary: "0 errors, 0 warnings", duration: "2.1s" },
	{ name: "Type Check", status: "pass", summary: "0 errors", duration: "5.7s" },
	{ name: "Policy: no secrets", status: "pass", summary: "No secret patterns detected", duration: "1.2s" },
	{ name: "File boundaries", status: "pass", summary: "All changes within allowed scope", duration: "0.5s" }
];

export const REVIEW_FINDINGS: ReviewFinding[] = [
	{ severity: "low", category: "edge_case", message: "Email validation does not trim whitespace before validation — `\" user@test.com\"` would fail." },
	{ severity: "low", category: "style", message: "Consider extracting regex to shared validation constants." }
];

export const WORLD_MODEL: ServiceNode[] = [
	{ name: "signup-api", type: "service", language: "typescript", owner: "team-growth", riskLevel: "medium", readinessScore: 82, dependencies: ["validation"] },
	{ name: "billing-api", type: "service", language: "typescript", owner: "team-payments", riskLevel: "high", readinessScore: 74, dependencies: ["validation"] },
	{ name: "notification-worker", type: "worker", language: "python", owner: "team-platform", riskLevel: "low", readinessScore: 91, dependencies: ["signup-api", "billing-api"] },
	{ name: "validation", type: "library", language: "python", owner: "team-platform", riskLevel: "medium", readinessScore: 88, dependencies: [] }
];

export const UNIFIED_DIFF = `diff --git a/services/signup-api/src/routes/signup.ts b/services/signup-api/src/routes/signup.ts
index a1b2c3d..e4f5g6h 100644
--- a/services/signup-api/src/routes/signup.ts
+++ b/services/signup-api/src/routes/signup.ts
@@ -1,5 +1,6 @@
 import { Router } from "express";
 import { validateRequired, validateString } from "validation";
+import { validateEmail } from "validation/email";
 import { createUser } from "../db/users";
 import { logger } from "../utils/logger";
 
@@ -12,6 +13,13 @@ router.post("/signup", async (req, res) => {
     return res.status(400).json({ error: "Password is required" });
   }
 
+  // Validate email format
+  const emailError = validateEmail(email);
+  if (emailError) {
+    logger.warn("signup_invalid_email", { email });
+    return res.status(400).json({ error: emailError });
+  }
+
   try {
     const user = await createUser({ email, password });
     logger.info("signup_success", { userId: user.id });

diff --git a/services/signup-api/test/signup.test.ts b/services/signup-api/test/signup.test.ts
index b2c3d4e..f5g6h7i 100644
--- a/services/signup-api/test/signup.test.ts
+++ b/services/signup-api/test/signup.test.ts
@@ -25,6 +25,20 @@ describe("POST /signup", () => {
     expect(res.status).toBe(400);
   });
 
+  it("rejects invalid email format", async () => {
+    const res = await request(app)
+      .post("/signup")
+      .send({ email: "not-an-email", password: "valid123" });
+    expect(res.status).toBe(400);
+    expect(res.body.error).toContain("invalid email");
+  });
+
+  it("accepts valid email format", async () => {
+    const res = await request(app)
+      .post("/signup")
+      .send({ email: "user@example.com", password: "valid123" });
+    expect(res.status).toBe(201);
+  });
+
   it("creates user on valid input", async () => {
     const res = await request(app)
       .post("/signup")
`;

export const SELECTED_TASK_ID = "task_001";
