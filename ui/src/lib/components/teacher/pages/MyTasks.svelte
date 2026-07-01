<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import type { Writable } from 'svelte/store';
	import {
		getTeacherTasks,
		createTeacherTask,
		updateTeacherTask,
		deleteTeacherTask,
		completeTeacherTask,
		reopenTeacherTask,
		type TeacherTask,
		type TaskStatus,
		type TaskPriority,
		type TaskCategory,
		type TaskSortBy
	} from '$lib/apis/teacherTasks';
	import ConfirmDialog from '$lib/components/student/elements/ConfirmDialog.svelte';

	interface I18n {
		t: (key: string) => string;
	}
	const i18n = getContext<Writable<I18n>>('i18n');

	const STATUS_OPTIONS: { value: TaskStatus; label: string }[] = [
		{ value: 'todo', label: 'To Do' },
		{ value: 'in_progress', label: 'In Progress' },
		{ value: 'completed', label: 'Completed' }
	];

	const PRIORITY_OPTIONS: { value: TaskPriority; label: string }[] = [
		{ value: 'low', label: 'Low' },
		{ value: 'medium', label: 'Medium' },
		{ value: 'high', label: 'High' },
		{ value: 'urgent', label: 'Urgent' }
	];

	const CATEGORY_OPTIONS: { value: TaskCategory; label: string }[] = [
		{ value: 'teaching', label: 'Teaching' },
		{ value: 'assessment', label: 'Assessment' },
		{ value: 'administration', label: 'Administration' },
		{ value: 'meetings', label: 'Meetings' },
		{ value: 'personal', label: 'Personal' }
	];

	const SORT_OPTIONS: { value: TaskSortBy; label: string }[] = [
		{ value: 'created_at', label: 'Creation date' },
		{ value: 'due_date', label: 'Due date' },
		{ value: 'priority', label: 'Priority' }
	];

	const STATUS_LABEL: Record<TaskStatus, string> = {
		todo: 'To Do',
		in_progress: 'In Progress',
		completed: 'Completed'
	};

	const PRIORITY_STYLES: Record<TaskPriority, string> = {
		low: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
		medium: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
		high: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
		urgent: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
	};

	const STATUS_STYLES: Record<TaskStatus, string> = {
		todo: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
		in_progress: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300',
		completed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
	};

	let tasks: TeacherTask[] = [];
	let loading = true;
	let error: string | null = null;

	let search = '';
	let filterStatus: TaskStatus | '' = '';
	let filterPriority: TaskPriority | '' = '';
	let filterCategory: TaskCategory | '' = '';
	let sortBy: TaskSortBy = 'created_at';

	let searchDebounce: ReturnType<typeof setTimeout>;

	function token() {
		return localStorage.getItem('token') || '';
	}

	function isOverdue(task: TeacherTask): boolean {
		return !!task.due_date && task.status !== 'completed' && new Date(task.due_date) < new Date();
	}

	async function loadTasks() {
		loading = true;
		error = null;
		try {
			tasks = await getTeacherTasks(token(), {
				status: filterStatus || undefined,
				priority: filterPriority || undefined,
				category: filterCategory || undefined,
				search: search || undefined,
				sort_by: sortBy
			});
		} catch (err: any) {
			error = err?.detail || err?.message || $i18n.t('Failed to load tasks');
		} finally {
			loading = false;
		}
	}

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(loadTasks, 300);
	}

	onMount(loadTasks);

	// ── Quick complete ────────────────────────────────────────────────────────

	async function quickToggle(task: TeacherTask) {
		try {
			if (task.status === 'completed') {
				await reopenTeacherTask(token(), task.id);
			} else {
				await completeTeacherTask(token(), task.id);
			}
			await loadTasks();
		} catch (err: any) {
			error = err?.detail || $i18n.t('Failed to update task');
		}
	}

	// ── Create / Edit form ────────────────────────────────────────────────────

	let showFormModal = false;
	let formMode: 'create' | 'edit' = 'create';
	let editingTask: TeacherTask | null = null;
	let form = {
		title: '',
		description: '',
		priority: 'medium' as TaskPriority,
		category: 'personal' as TaskCategory,
		status: 'todo' as TaskStatus,
		due_date: ''
	};

	function openCreate() {
		formMode = 'create';
		editingTask = null;
		form = {
			title: '',
			description: '',
			priority: 'medium',
			category: 'personal',
			status: 'todo',
			due_date: ''
		};
		showFormModal = true;
	}

	function openEdit(task: TeacherTask) {
		formMode = 'edit';
		editingTask = task;
		form = {
			title: task.title,
			description: task.description || '',
			priority: task.priority,
			category: task.category,
			status: task.status,
			due_date: task.due_date ? task.due_date.slice(0, 10) : ''
		};
		showFormModal = true;
	}

	async function saveForm() {
		if (!form.title.trim()) return;
		try {
			if (formMode === 'edit' && editingTask) {
				await updateTeacherTask(token(), editingTask.id, {
					title: form.title.trim(),
					description: form.description || undefined,
					priority: form.priority,
					category: form.category,
					status: form.status,
					due_date: form.due_date ? new Date(form.due_date).toISOString() : undefined
				});
			} else {
				await createTeacherTask(token(), {
					title: form.title.trim(),
					description: form.description || undefined,
					priority: form.priority,
					category: form.category,
					due_date: form.due_date ? new Date(form.due_date).toISOString() : undefined
				});
			}
			showFormModal = false;
			await loadTasks();
		} catch (err: any) {
			error = err?.detail || $i18n.t('Failed to save task');
		}
	}

	// ── View detail ───────────────────────────────────────────────────────────

	let showViewModal = false;
	let viewingTask: TeacherTask | null = null;

	function openView(task: TeacherTask) {
		viewingTask = task;
		showViewModal = true;
	}

	// ── Delete ────────────────────────────────────────────────────────────────

	let showDeleteConfirm = false;
	let deletingTask: TeacherTask | null = null;

	function askDelete(task: TeacherTask) {
		deletingTask = task;
		showDeleteConfirm = true;
	}

	async function performDelete() {
		if (!deletingTask) return;
		try {
			await deleteTeacherTask(token(), deletingTask.id);
			showDeleteConfirm = false;
			deletingTask = null;
			await loadTasks();
		} catch (err: any) {
			error = err?.detail || $i18n.t('Failed to delete task');
			showDeleteConfirm = false;
		}
	}
</script>

<div class="max-w-5xl mx-auto">
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">{$i18n.t('My Tasks')}</h1>
			<p class="text-gray-600 dark:text-gray-400">
				{$i18n.t('Your private task list — visible only to you')}
			</p>
		</div>

		<button
			class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-sm font-semibold shadow-sm transition-colors self-start"
			on:click={openCreate}
		>
			+ {$i18n.t('Create Task')}
		</button>
	</div>

	{#if error}
		<div
			class="mb-4 rounded-xl bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 px-4 py-3 text-sm"
		>
			{error}
		</div>
	{/if}

	<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm ring-1 ring-gray-100 dark:ring-gray-700 p-4 mb-6">
		<div class="flex flex-col lg:flex-row gap-3">
			<div class="flex-1">
				<label for="task-search" class="sr-only">{$i18n.t('Search by title')}</label>
				<input
					id="task-search"
					type="text"
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					placeholder={$i18n.t('Search by title...')}
					bind:value={search}
					on:input={onSearchInput}
				/>
			</div>

			<select
				class="rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				bind:value={filterStatus}
				on:change={loadTasks}
			>
				<option value="">{$i18n.t('All statuses')}</option>
				{#each STATUS_OPTIONS as opt}
					<option value={opt.value}>{$i18n.t(opt.label)}</option>
				{/each}
			</select>

			<select
				class="rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				bind:value={filterPriority}
				on:change={loadTasks}
			>
				<option value="">{$i18n.t('All priorities')}</option>
				{#each PRIORITY_OPTIONS as opt}
					<option value={opt.value}>{$i18n.t(opt.label)}</option>
				{/each}
			</select>

			<select
				class="rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				bind:value={filterCategory}
				on:change={loadTasks}
			>
				<option value="">{$i18n.t('All categories')}</option>
				{#each CATEGORY_OPTIONS as opt}
					<option value={opt.value}>{$i18n.t(opt.label)}</option>
				{/each}
			</select>

			<select
				class="rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				bind:value={sortBy}
				on:change={loadTasks}
			>
				{#each SORT_OPTIONS as opt}
					<option value={opt.value}>{$i18n.t('Sort by')}: {$i18n.t(opt.label)}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if loading}
		<div class="flex justify-center items-center py-20">
			<div
				class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"
			></div>
			<span class="ml-3 text-gray-600 dark:text-gray-300">{$i18n.t('Loading...')}</span>
		</div>
	{:else if tasks.length === 0}
		<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-10 text-center">
			<h3 class="text-lg font-medium text-gray-800 dark:text-white mb-2">
				{$i18n.t('No tasks found')}
			</h3>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				{$i18n.t('Create your first task or adjust your search and filters.')}
			</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each tasks as task (task.id)}
				<div
					class="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md ring-1 ring-gray-100 dark:ring-gray-700 p-4 transition-shadow flex items-start gap-3"
				>
					<button
						class="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors {task.status ===
						'completed'
							? 'bg-emerald-500 border-emerald-500 text-white'
							: 'border-gray-300 dark:border-gray-600 hover:border-emerald-500 text-transparent'}"
						title={task.status === 'completed'
							? $i18n.t('Mark as To Do')
							: $i18n.t('Mark as Done')}
						aria-label={task.status === 'completed'
							? $i18n.t('Mark as To Do')
							: $i18n.t('Mark as Done')}
						on:click={() => quickToggle(task)}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-4 h-4"
							viewBox="0 0 20 20"
							fill="currentColor"
						>
							<path
								fill-rule="evenodd"
								d="M16.704 5.29a1 1 0 010 1.415l-7.004 7a1 1 0 01-1.414 0l-3.5-3.5a1 1 0 111.414-1.414l2.793 2.793 6.297-6.294a1 1 0 011.414 0z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>

					<div class="flex-1 min-w-0">
						<div class="flex flex-wrap items-start justify-between gap-2">
							<button
								class="text-left font-semibold text-gray-900 dark:text-white hover:underline {task.status ===
								'completed'
									? 'line-through text-gray-500 dark:text-gray-400'
									: ''}"
								on:click={() => openView(task)}
							>
								{task.title}
							</button>

							<div class="flex flex-wrap items-center gap-1.5">
								<span
									class="text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap {STATUS_STYLES[
										task.status
									]}"
								>
									{$i18n.t(STATUS_LABEL[task.status])}
								</span>
								<span
									class="text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap {PRIORITY_STYLES[
										task.priority
									]}"
								>
									{$i18n.t(task.priority)}
								</span>
								<span
									class="text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300"
								>
									{$i18n.t(task.category)}
								</span>
							</div>
						</div>

						{#if task.description}
							<p
								class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-1 {task.status ===
								'completed'
									? 'opacity-60'
									: ''}"
							>
								{task.description}
							</p>
						{/if}

						<div class="flex items-center justify-between mt-3">
							<span
								class="text-xs {isOverdue(task)
									? 'text-rose-600 dark:text-rose-400 font-semibold'
									: 'text-gray-500 dark:text-gray-400'}"
							>
								{#if task.due_date}
									{$i18n.t('Due')}
									{new Date(task.due_date).toLocaleDateString()}
									{#if isOverdue(task)}
										· {$i18n.t('Overdue')}
									{/if}
								{/if}
							</span>

							<div class="flex items-center gap-3">
								<button
									class="text-xs text-gray-600 dark:text-gray-300 hover:underline"
									on:click={() => openView(task)}
								>
									{$i18n.t('View')}
								</button>
								<button
									class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
									on:click={() => openEdit(task)}
								>
									{$i18n.t('Edit')}
								</button>
								<button
									class="text-xs text-rose-600 dark:text-rose-400 hover:underline"
									on:click={() => askDelete(task)}
								>
									{$i18n.t('Delete')}
								</button>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showFormModal}
	<div
		class="fixed inset-0 backdrop-blur-sm bg-white/30 dark:bg-black/30 flex items-center justify-center z-50 p-4"
		role="dialog"
		aria-modal="true"
		in:fade
	>
		<div
			class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md ring-1 ring-gray-200 dark:ring-gray-700"
			transition:scale={{ duration: 200 }}
		>
			<h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
				{formMode === 'edit' ? $i18n.t('Edit Task') : $i18n.t('Create Task')}
			</h2>

			<div class="space-y-3">
				<div>
					<label
						for="task-title"
						class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
					>
						{$i18n.t('Title')}
					</label>
					<input
						id="task-title"
						class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						bind:value={form.title}
						placeholder={$i18n.t('e.g. Grade Chapter 4 quizzes')}
					/>
				</div>

				<div>
					<label
						for="task-description"
						class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
					>
						{$i18n.t('Description')}
					</label>
					<textarea
						id="task-description"
						class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						rows="3"
						bind:value={form.description}
					></textarea>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label
							for="task-priority"
							class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
						>
							{$i18n.t('Priority')}
						</label>
						<select
							id="task-priority"
							class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							bind:value={form.priority}
						>
							{#each PRIORITY_OPTIONS as opt}
								<option value={opt.value}>{$i18n.t(opt.label)}</option>
							{/each}
						</select>
					</div>
					<div>
						<label
							for="task-category"
							class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
						>
							{$i18n.t('Category')}
						</label>
						<select
							id="task-category"
							class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							bind:value={form.category}
						>
							{#each CATEGORY_OPTIONS as opt}
								<option value={opt.value}>{$i18n.t(opt.label)}</option>
							{/each}
						</select>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label
							for="task-due-date"
							class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
						>
							{$i18n.t('Due date')}
						</label>
						<input
							id="task-due-date"
							type="date"
							class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							bind:value={form.due_date}
						/>
					</div>
					{#if formMode === 'edit'}
						<div>
							<label
								for="task-status"
								class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1"
							>
								{$i18n.t('Status')}
							</label>
							<select
								id="task-status"
								class="w-full rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								bind:value={form.status}
							>
								{#each STATUS_OPTIONS as opt}
									<option value={opt.value}>{$i18n.t(opt.label)}</option>
								{/each}
							</select>
						</div>
					{/if}
				</div>
			</div>

			<div class="flex justify-end gap-3 mt-6">
				<button
					class="px-4 py-2 text-sm rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
					on:click={() => (showFormModal = false)}
				>
					{$i18n.t('Cancel')}
				</button>
				<button
					class="px-4 py-2 text-sm rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-sm disabled:opacity-50"
					disabled={!form.title.trim()}
					on:click={saveForm}
				>
					{$i18n.t('Save')}
				</button>
			</div>
		</div>
	</div>
{/if}

{#if showViewModal && viewingTask}
	<div
		class="fixed inset-0 backdrop-blur-sm bg-white/30 dark:bg-black/30 flex items-center justify-center z-50 p-4"
		role="dialog"
		aria-modal="true"
		in:fade
	>
		<div
			class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md ring-1 ring-gray-200 dark:ring-gray-700"
			transition:scale={{ duration: 200 }}
		>
			<div class="flex items-start justify-between gap-2 mb-4">
				<h2
					class="text-lg font-semibold text-gray-900 dark:text-white {viewingTask.status ===
					'completed'
						? 'line-through text-gray-500 dark:text-gray-400'
						: ''}"
				>
					{viewingTask.title}
				</h2>
				<span
					class="text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap {STATUS_STYLES[
						viewingTask.status
					]}"
				>
					{$i18n.t(STATUS_LABEL[viewingTask.status])}
				</span>
			</div>

			{#if viewingTask.description}
				<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{viewingTask.description}</p>
			{/if}

			<dl class="grid grid-cols-2 gap-3 text-sm mb-4">
				<div>
					<dt class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Priority')}</dt>
					<dd class="text-gray-900 dark:text-white">{$i18n.t(viewingTask.priority)}</dd>
				</div>
				<div>
					<dt class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Category')}</dt>
					<dd class="text-gray-900 dark:text-white">{$i18n.t(viewingTask.category)}</dd>
				</div>
				<div>
					<dt class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Due date')}</dt>
					<dd class="text-gray-900 dark:text-white">
						{viewingTask.due_date
							? new Date(viewingTask.due_date).toLocaleDateString()
							: $i18n.t('None')}
					</dd>
				</div>
				<div>
					<dt class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Created')}</dt>
					<dd class="text-gray-900 dark:text-white">
						{new Date(viewingTask.created_at).toLocaleDateString()}
					</dd>
				</div>
			</dl>

			<div class="flex justify-end gap-3">
				<button
					class="px-4 py-2 text-sm rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
					on:click={() => (showViewModal = false)}
				>
					{$i18n.t('Close')}
				</button>
				<button
					class="px-4 py-2 text-sm rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-sm"
					on:click={() => {
						showViewModal = false;
						if (viewingTask) openEdit(viewingTask);
					}}
				>
					{$i18n.t('Edit')}
				</button>
			</div>
		</div>
	</div>
{/if}

{#if showDeleteConfirm}
	<ConfirmDialog
		title={$i18n.t('Delete Task')}
		message={$i18n.t('Are you sure you want to delete this task? This cannot be undone.')}
		confirmText={$i18n.t('Delete')}
		cancelText={$i18n.t('Cancel')}
		confirmButtonClass="bg-rose-600 hover:bg-rose-700"
		on:confirm={performDelete}
		on:cancel={() => (showDeleteConfirm = false)}
	/>
{/if}

<style>
	.line-clamp-1 {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
