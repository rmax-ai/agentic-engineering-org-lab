<script lang="ts">
	import type { TraceEvent } from "$lib/data/mock";

	let { events }: { events: TraceEvent[] } = $props();

	const actorIcons: Record<string, string> = {
		system: "⬡",
		agent: "◇",
		human: "●"
	};
</script>

<div class="space-y-0">
	{#each events as event}
		<div class="flex gap-3 py-2 px-3 hover:bg-panel/50 rounded transition-colors">
			<!-- Timeline dot + line -->
			<div class="flex flex-col items-center shrink-0">
				<div class="w-6 h-6 rounded-full flex items-center justify-center text-xs
					{event.status === 'pass' ? 'bg-success/20 text-success' : event.status === 'fail' ? 'bg-failure/20 text-failure' : 'bg-active/20 text-active'}">
					{actorIcons[event.actor] ?? "○"}
				</div>
				<div class="w-px flex-1 bg-border/50 min-h-[8px]"></div>
			</div>

			<!-- Content -->
			<div class="flex-1 min-w-0 pb-2">
				<div class="flex items-center gap-2 flex-wrap">
					<span class="text-[10px] text-neutral font-mono">{event.timestamp}</span>
					<span class="text-[10px] text-muted uppercase tracking-wider">{event.type}</span>
				</div>
				<p class="text-xs text-gray-300 mt-0.5 leading-relaxed">{event.summary}</p>
			</div>
		</div>
	{/each}
</div>
