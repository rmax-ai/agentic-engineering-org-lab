<script lang="ts">
	let { diff }: { diff: string } = $props();

	function colorLine(line: string): string {
		if (line.startsWith("+")) return "diff-add";
		if (line.startsWith("-")) return "diff-remove";
		if (line.startsWith("@@")) return "diff-hunk";
		return "";
	}
</script>

<div class="bg-black rounded-lg border border-border overflow-hidden">
	<!-- Header -->
	<div class="flex items-center gap-2 px-3 py-2 border-b border-border bg-panel">
		<span class="text-[10px] text-muted uppercase tracking-wider font-semibold">Unified Diff</span>
		<span class="text-[9px] text-neutral ml-auto">3 files changed</span>
	</div>

	<!-- Diff content -->
	<pre class="p-3 text-xs font-mono leading-relaxed overflow-x-auto max-h-[500px] overflow-y-auto"><code>
		{#each diff.split("\n") as line}
			<span class={colorLine(line)}>{line}&#10;</span>
		{/each}
	</code></pre>
</div>
