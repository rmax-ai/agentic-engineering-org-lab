<script lang="ts">
	import { TASKS, SELECTED_TASK_ID, PIPELINE, TRACE_EVENTS, VERIFICATION_CHECKS, REVIEW_FINDINGS, WORLD_MODEL, UNIFIED_DIFF } from "$lib/data/mock";
	import StatusPill from "$lib/components/StatusPill.svelte";
	import Pipeline from "$lib/components/Pipeline.svelte";
	import TraceTimeline from "$lib/components/TraceTimeline.svelte";
	import DiffViewer from "$lib/components/DiffViewer.svelte";
	import VerificationPanel from "$lib/components/VerificationPanel.svelte";
	import ReviewPanel from "$lib/components/ReviewPanel.svelte";
	import WorldModelGraph from "$lib/components/WorldModelGraph.svelte";
	import Section from "$lib/components/Section.svelte";
	import type { Task } from "$lib/data/mock";

	let selectedId = $state(SELECTED_TASK_ID);
	let activeTab = $state("overview");

	const selected = $derived(TASKS.find(t => t.id === selectedId)!);

	const tabs = ["overview", "pipeline", "diff", "trace", "world"];

	const decisionLabels: Record<string, string> = {
		auto_delegate: "Auto-Delegate",
		human_decompose_first: "Decompose First",
		human_review_required: "Review Required",
		reject_unsafe: "Rejected (Unsafe)",
		insufficient_context: "Insufficient Context"
	};

	const priorityColors: Record<string, string> = {
		low: "text-neutral",
		medium: "text-blocked",
		high: "text-failure",
		critical: "text-failure font-bold"
	};
</script>

<div class="flex h-full">
	<!-- LEFT: Task List -->
	<div class="w-72 border-r border-border bg-surface shrink-0 overflow-y-auto">
		<div class="px-4 py-3 border-b border-border">
			<h2 class="text-xs text-muted uppercase tracking-wider font-semibold">Tasks</h2>
		</div>
		<div class="divide-y divide-border/50">
			{#each TASKS as task}
				<button
					class="w-full text-left px-4 py-3 hover:bg-panel/50 transition-colors {task.id === selectedId ? 'bg-panel border-l-2 border-active' : 'border-l-2 border-transparent'}"
					onclick={() => { selectedId = task.id; activeTab = "overview"; }}
				>
					<div class="flex items-center justify-between gap-2">
						<span class="text-xs font-mono text-neutral">{task.id}</span>
						<StatusPill status={task.status} />
					</div>
					<p class="text-sm text-gray-200 mt-1 leading-snug line-clamp-2">{task.title}</p>
					<div class="flex items-center gap-2 mt-1.5">
						<span class="text-[10px] text-muted">{task.requester}</span>
						<span class="text-[10px] {priorityColors[task.priority]}">{task.priority}</span>
					</div>
				</button>
			{/each}
		</div>
	</div>

	<!-- RIGHT: Detail View -->
	<div class="flex-1 overflow-y-auto">
		<!-- Task Header -->
		<div class="px-6 py-4 border-b border-border bg-panel/50">
			<div class="flex items-start justify-between gap-4">
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2 mb-1">
						<span class="text-xs font-mono text-neutral">{selected.id}</span>
						<StatusPill status={selected.status} />
						{#if selected.decision}
							<span class="text-[10px] text-agent border border-agent/30 px-1.5 py-0.5 rounded font-mono">
								{decisionLabels[selected.decision] ?? selected.decision}
							</span>
						{/if}
					</div>
					<h1 class="text-lg font-semibold text-white">{selected.title}</h1>
					<p class="text-sm text-muted mt-1">{selected.description}</p>
				</div>

				<div class="flex flex-col items-end gap-1 text-xs shrink-0">
					<span class="text-muted">Created {selected.createdAt}</span>
					<span class="text-muted">Risk: <span class="text-blocked font-semibold">{selected.riskLevel}</span></span>
					<div class="flex gap-1 mt-1">
						{#each selected.affectedServices as svc}
							<span class="text-[10px] bg-panel border border-border px-1.5 py-0.5 rounded font-mono text-gray-400">{svc}</span>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- Tabs -->
		<div class="flex border-b border-border bg-surface px-6">
			{#each tabs as tab}
				<button
					class="px-3 py-2 text-xs border-b-2 transition-colors
						{tab === activeTab ? 'border-active text-active' : 'border-transparent text-muted hover:text-gray-300'}"
					onclick={() => activeTab = tab}
				>
					{tab.charAt(0).toUpperCase() + tab.slice(1)}
				</button>
			{/each}
		</div>

		<!-- Tab Content -->
		<div class="p-6 space-y-4">
			{#if activeTab === "overview"}
				<!-- Repo Readiness -->
				<Section title="Repo Readiness">
					<div class="flex items-center gap-4">
						<div class="flex items-center gap-2">
							<span class="text-2xl font-bold text-success">82</span>
							<span class="text-sm text-muted">/ 100</span>
						</div>
						<div class="flex-1">
							<div class="w-full bg-panel rounded-full h-2">
								<div class="bg-success h-2 rounded-full" style="width: 82%"></div>
							</div>
						</div>
						<span class="text-xs px-2 py-0.5 rounded bg-blocked/20 text-blocked border border-blocked/30 font-mono">ready_with_caution</span>
					</div>
					<div class="text-xs text-muted mt-2">
						Missing: No threat model found · No explicit rollback notes
					</div>
				</Section>

				<!-- Final Recommendation -->
				<Section title="Merge Recommendation">
					<div class="flex items-center gap-3">
						<span class="w-10 h-10 rounded-full bg-success/20 border-2 border-success flex items-center justify-center text-success text-lg font-bold">▲</span>
						<div>
							<div class="text-sm font-semibold text-success">Ready for Human Review</div>
							<div class="text-xs text-muted mt-0.5">All checks passed. 0 blocking review findings. 1 low-severity suggestion.</div>
						</div>
					</div>
				</Section>

				<!-- Verdict summary cards -->
				<div class="grid grid-cols-3 gap-3">
					<div class="bg-panel border border-border rounded-lg p-3">
						<div class="text-[10px] text-muted uppercase tracking-wider">Classification</div>
						<div class="text-sm font-semibold text-agent mt-1">auto_delegate</div>
						<div class="text-xs text-neutral mt-0.5">Confidence: 0.82</div>
					</div>
					<div class="bg-panel border border-border rounded-lg p-3">
						<div class="text-[10px] text-muted uppercase tracking-wider">Verification</div>
						<div class="text-sm font-semibold text-success mt-1">5/5 Passed</div>
						<div class="text-xs text-neutral mt-0.5">Tests · Lint · TypeCheck · Policy · Boundaries</div>
					</div>
					<div class="bg-panel border border-border rounded-lg p-3">
						<div class="text-[10px] text-muted uppercase tracking-wider">Agent Execution</div>
						<div class="text-sm font-semibold text-active mt-1">1 attempt</div>
						<div class="text-xs text-neutral mt-0.5">3 files · 0 errors · 3m 40s</div>
					</div>
				</div>

			{:else if activeTab === "pipeline"}
				<Pipeline stages={PIPELINE} />

			{:else if activeTab === "diff"}
				<DiffViewer diff={UNIFIED_DIFF} />

			{:else if activeTab === "trace"}
				<TraceTimeline events={TRACE_EVENTS} />

			{:else if activeTab === "world"}
				<WorldModelGraph nodes={WORLD_MODEL} />
			{/if}

			<!-- Verification + Review always visible (collapsed) -->
			<details class="bg-panel border border-border rounded-lg" open>
				<summary class="px-4 py-2 cursor-pointer text-xs text-muted uppercase tracking-wider font-semibold hover:text-gray-300">
					Verification Results
				</summary>
				<div class="px-4 pb-4">
					<VerificationPanel checks={VERIFICATION_CHECKS} />
				</div>
			</details>

			<details class="bg-panel border border-border rounded-lg">
				<summary class="px-4 py-2 cursor-pointer text-xs text-muted uppercase tracking-wider font-semibold hover:text-gray-300">
					AI Review · 0 blocking · 2 findings
				</summary>
				<div class="px-4 pb-4">
					<ReviewPanel findings={REVIEW_FINDINGS} />
				</div>
			</details>
		</div>
	</div>
</div>
