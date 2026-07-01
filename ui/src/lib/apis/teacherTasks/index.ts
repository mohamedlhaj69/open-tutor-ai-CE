import { TUTOR_API_BASE_URL } from '$lib/constants';

// Types

export type TaskStatus = 'todo' | 'in_progress' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskCategory = 'teaching' | 'assessment' | 'administration' | 'meetings' | 'personal';
export type TaskSortBy = 'due_date' | 'created_at' | 'priority';

export interface TeacherTaskCreateRequest {
	title: string;
	description?: string;
	priority?: TaskPriority;
	category?: TaskCategory;
	due_date?: string;
}

export interface TeacherTaskUpdateRequest {
	title?: string;
	description?: string;
	status?: TaskStatus;
	priority?: TaskPriority;
	category?: TaskCategory;
	due_date?: string;
}

export interface TeacherTask {
	id: string;
	user_id: string;
	title: string;
	description?: string;
	status: TaskStatus;
	priority: TaskPriority;
	category: TaskCategory;
	due_date?: string;
	created_at: string;
	updated_at: string;
}

export interface TeacherTaskListParams {
	status?: TaskStatus;
	priority?: TaskPriority;
	category?: TaskCategory;
	search?: string;
	sort_by?: TaskSortBy;
}

function _headers(token: string) {
	return {
		Accept: 'application/json',
		'Content-Type': 'application/json',
		authorization: `Bearer ${token}`
	};
}

async function _handle<T>(res: Response): Promise<T> {
	if (!res.ok) throw await res.json();
	return res.json();
}

export const getTeacherTasks = async (
	token: string,
	params: TeacherTaskListParams = {}
): Promise<TeacherTask[]> => {
	let error = null;

	const query = new URLSearchParams();
	if (params.status) query.set('status', params.status);
	if (params.priority) query.set('priority', params.priority);
	if (params.category) query.set('category', params.category);
	if (params.search) query.set('search', params.search);
	if (params.sort_by) query.set('sort_by', params.sort_by);
	const qs = query.toString();
	const url = qs
		? `${TUTOR_API_BASE_URL}/teacher-tasks?${qs}`
		: `${TUTOR_API_BASE_URL}/teacher-tasks`;

	const res = await fetch(url, {
		method: 'GET',
		headers: _headers(token)
	})
		.then((res) => _handle<TeacherTask[]>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask[];
};

export const getTeacherTaskById = async (token: string, taskId: string): Promise<TeacherTask> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks/${taskId}`, {
		method: 'GET',
		headers: _headers(token)
	})
		.then((res) => _handle<TeacherTask>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask;
};

export const createTeacherTask = async (
	token: string,
	data: TeacherTaskCreateRequest
): Promise<TeacherTask> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks`, {
		method: 'POST',
		headers: _headers(token),
		body: JSON.stringify(data)
	})
		.then((res) => _handle<TeacherTask>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask;
};

export const updateTeacherTask = async (
	token: string,
	taskId: string,
	data: TeacherTaskUpdateRequest
): Promise<TeacherTask> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks/${taskId}`, {
		method: 'PATCH',
		headers: _headers(token),
		body: JSON.stringify(data)
	})
		.then((res) => _handle<TeacherTask>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask;
};

export const deleteTeacherTask = async (
	token: string,
	taskId: string
): Promise<{ status: string }> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks/${taskId}`, {
		method: 'DELETE',
		headers: _headers(token)
	})
		.then((res) => _handle<{ status: string }>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as { status: string };
};

export const completeTeacherTask = async (token: string, taskId: string): Promise<TeacherTask> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks/${taskId}/complete`, {
		method: 'POST',
		headers: _headers(token)
	})
		.then((res) => _handle<TeacherTask>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask;
};

export const reopenTeacherTask = async (token: string, taskId: string): Promise<TeacherTask> => {
	let error = null;

	const res = await fetch(`${TUTOR_API_BASE_URL}/teacher-tasks/${taskId}/reopen`, {
		method: 'POST',
		headers: _headers(token)
	})
		.then((res) => _handle<TeacherTask>(res))
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res as TeacherTask;
};
