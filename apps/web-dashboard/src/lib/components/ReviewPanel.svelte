<script lang="ts">
	import type { ReviewFinding } from "$lib/data/mock";

	let { findings }: { findings: ReviewFinding[] } = $props();

	const severityColors: Record<string, string> = {
		low: "text-neutral border-neutral/30",
		medium: "text-blocked border-blocked/30",
		high: "text-failure border-failure/30",
		blocker: "text-failure border-failure font-bold"
	};
</script>

<div class="space-y-2">
	{#each findings as finding}
		<div class="flex gap-3 px-3 py-2 bg-panel rounded border border-border">
			<span class="shrink-0 text-[10px] uppercase px-1.5 py-0.5 rounded border {severityColors[finding.severity]} font-mono">
				{finding.severity}
			</span>
			<div class="flex-1 min-w-0">
				<span class="text-[10px] text-muted uppercase tracking-wider">{finding.category}</span>
				<p class="text-xs text-gray-300 mt-0.5">{finding.message}</p>
			</div>
		</div>
	{/each}
</div>
