<script lang="ts">
	// Icons as single chars for compact sidebar
	const sections = [
		{ id: "tasks", icon: "☰", label: "Tasks", active: true },
		{ id: "world", icon: "◈", label: "World Model", active: false },
		{ id: "repos", icon: "◫", label: "Readiness", active: false },
		{ id: "docs", icon: "⎘", label: "Docs", active: false }
	];
</script>

<aside class="w-12 flex flex-col items-center py-3 border-r border-border bg-surface shrink-0">
	<div class="text-agent text-sm font-bold mb-6" title="Agentic Engineering Org Lab">AE</div>

	<nav class="flex flex-col gap-1 flex-1">
		{#each sections as s}
			<button
				class="w-8 h-8 flex items-center justify-center rounded-md text-sm
					{s.active ? 'bg-panel text-active border border-border' : 'text-neutral hover:text-gray-300 hover:bg-panel'}"
				title={s.label}
			>
				{s.icon}
			</button>
		{/each}
	</nav>

	<div class="text-neutral text-xs mt-auto" title="v0.1.0">v1</div>
</aside>
