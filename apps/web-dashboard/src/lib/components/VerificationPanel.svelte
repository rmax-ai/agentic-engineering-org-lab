<script lang="ts">
	import type { VerificationCheck } from "$lib/data/mock";
	import StatusPill from "./StatusPill.svelte";

	let { checks }: { checks: VerificationCheck[] } = $props();
</script>

<div class="space-y-1.5">
	{#each checks as check}
		<div class="flex items-center justify-between px-3 py-2 bg-panel rounded border border-border">
			<div class="flex items-center gap-3">
				<StatusPill status={check.status} />
				<span class="text-sm text-gray-200">{check.name}</span>
			</div>
			<div class="flex items-center gap-3 text-xs">
				<span class="text-muted">{check.summary}</span>
				<span class="text-neutral font-mono">{check.duration}</span>
			</div>
		</div>
	{/each}
</div>
