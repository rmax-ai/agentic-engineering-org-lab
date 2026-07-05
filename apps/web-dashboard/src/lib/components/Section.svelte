<script lang="ts">
	let { title, children }: { title: string; children?: import("svelte").Snippet } = $props();
</script>

<div class="border-b border-border">
	<div class="px-4 py-2">
		<h3 class="text-[11px] text-muted uppercase tracking-wider font-semibold">{title}</h3>
	</div>
	<div class="px-4 pb-3">
		{@render children?.()}
	</div>
</div>
