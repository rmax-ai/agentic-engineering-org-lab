<script lang="ts">
	import type { ServiceNode } from "$lib/data/mock";

	let { nodes }: { nodes: ServiceNode[] } = $props();

	const typeShapes: Record<string, string> = {
		service: "rounded-lg",
		library: "rounded",
		worker: "rounded-full"
	};

	const riskColors: Record<string, string> = {
		low: "border-success/40",
		medium: "border-blocked/40",
		high: "border-failure/40"
	};
</script>

<div class="p-4 overflow-x-auto">
	<div class="flex flex-wrap gap-6 items-center justify-center min-h-[200px]">
		{#each nodes as node}
			<div class="flex flex-col items-center gap-2">
				<div class="px-4 py-3 bg-panel border-2 {riskColors[node.riskLevel]} {typeShapes[node.type]} min-w-[140px] text-center">
					<div class="text-sm font-semibold text-gray-200">{node.name}</div>
					<div class="text-[10px] text-muted uppercase mt-0.5">{node.type} · {node.language}</div>
					<div class="flex items-center justify-center gap-1 mt-1.5">
						<span class="text-[10px] text-neutral">Owner:</span>
						<span class="text-[10px] text-gray-400">{node.owner}</span>
					</div>
					<div class="mt-1">
						<span class="text-[10px] px-1.5 py-0.5 rounded {node.readinessScore >= 80 ? 'bg-success/20 text-success' : 'bg-blocked/20 text-blocked'}">
							{node.readinessScore}/100
						</span>
					</div>
				</div>

				<!-- Edges (simplified — only show if has deps) -->
				{#if node.dependencies.length > 0}
					<div class="flex gap-2 text-[9px] text-neutral">
						depends on: {node.dependencies.join(", ")}
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>
