<script lang="ts">
	import type { TaskStatus } from "$lib/data/mock";

	let { status, label }: { status: TaskStatus | "pass" | "fail" | "info"; label?: string } = $props();

	const colors: Record<string, string> = {
		pending: "bg-neutral/20 text-neutral border-neutral/30",
		classifying: "bg-agent/20 text-agent border-agent/30",
		running: "bg-active/20 text-active border-active/30",
		verifying: "bg-active/20 text-active border-active/30",
		reviewing: "bg-blocked/20 text-blocked border-blocked/30",
		completed: "bg-success/20 text-success border-success/30",
		failed: "bg-failure/20 text-failure border-failure/30",
		pass: "bg-success/20 text-success border-success/30",
		fail: "bg-failure/20 text-failure border-failure/30",
		info: "bg-active/20 text-active border-active/30"
	};
</script>

<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border {colors[status] ?? 'bg-neutral/20 text-neutral'}">
	<span class="w-1.5 h-1.5 rounded-full {status === 'running' || status === 'classifying' ? 'animate-pulse' : ''}" style="background: currentColor"></span>
	{label ?? status}
</span>
