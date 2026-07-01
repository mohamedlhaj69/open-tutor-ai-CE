<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { getTeacherTasks, type TeacherTask } from '$lib/apis/teacherTasks';

	interface I18n {
		t: (key: string) => string;
	}
	const i18n = getContext<Writable<I18n>>('i18n');

	let tasks: TeacherTask[] = [];
	let loading = true;
	let error: string | null = null;

	function token() {
		return localStorage.getItem('token') || '';
	}

	onMount(async () => {
		try {
			tasks = await getTeacherTasks(token());
		} catch (err: any) {
			error = err?.detail || err?.message || $i18n.t('Failed to load tasks');
		} finally {
			loading = false;
		}
	});
</script>

<div class="max-w-5xl mx-auto">
	<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">{$i18n.t('My Tasks')}</h1>
	<p class="text-gray-600 dark:text-gray-400 mb-6">
		{$i18n.t('Your private task list — visible only to you')}
	</p>

	{#if loading}
		<div class="flex justify-center items-center py-20">
			<div
				class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"
			></div>
			<span class="ml-3 text-gray-600 dark:text-gray-300">{$i18n.t('Loading...')}</span>
		</div>
	{:else if error}
		<div
			class="rounded-xl bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 px-4 py-3 text-sm"
		>
			{error}
		</div>
	{:else}
		<p class="text-sm text-gray-500 dark:text-gray-400">
			{tasks.length}
			{$i18n.t('tasks')}
		</p>
	{/if}
</div>
