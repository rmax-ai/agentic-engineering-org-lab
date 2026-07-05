<script lang="ts">
	import type { PipelineStage } from "$lib/data/mock";

	let { stages }: { stages: PipelineStage[] } = $props();

	function stageColor(s: PipelineStage): string {
		switch (s.status) {
			case "pass": return "bg-success border-success";
			case "fail": return "bg-failure border-failure";
			case "active": return "bg-active border-active pipeline-active";
			case "skipped": return "bg-neutral/30 border-neutral/50";
			default: return "bg-neutral/20 border-neutral/40";
		}
	}
</script>

<div class="flex items-center gap-0 overflow-x-auto py-4 px-2">
	{#each stages as stage, i}
		<div class="flex items-center gap-0 shrink-0">
			<!-- Node -->
			<div class="flex flex-col items-center gap-1">
				<div class="w-10 h-10 rounded-full border-2 flex items-center justify-center text-sm font-bold {stageColor(stage)}">
					{stage.icon}
				</div>
				<span class="text-[10px] text-muted whitespace-nowrap">{stage.label}</span>
				{#if stage.timestamp}
					<span class="text-[9px] text-neutral/70">{stage.timestamp}</span>
				{/if}
				{#if stage.duration}
					<span class="text-[9px] text-neutral/50">{stage.duration}</span>
				{/if}
			</div>

			<!-- Connector -->
			{#if i < stages.length - 1}
				<div class="w-8 h-0.5 {stages[i + 1].status === 'pass' ? 'bg-success/50' : stages[i + 1].status === 'fail' ? 'bg-failure/50' : 'bg-neutral/30'}" style="margin-top: -20px"></div>
			{/if}
		</div>
	{/each}
</div>
