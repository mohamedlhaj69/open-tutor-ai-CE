<script lang="ts">
	import { getContext } from 'svelte';
    import type { Writable } from 'svelte/store';


	// Get i18n from context with proper typing 
	interface I18n {
		t: (key: string) => string;
	}
	const i18n = getContext<Writable<I18n>>('i18n');

    export let uploadedFiles: File[] = [];

    // File upload handling
	function handleFileChange(event: Event) {
		const files = (event.target as HTMLInputElement).files;
		if (files && files.length > 0) {
			uploadedFiles = Array.from(files);
		}
	}

	function handleFileDrop(event: DragEvent) {
		event.preventDefault();
		if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
			uploadedFiles = Array.from(event.dataTransfer.files);
		}
	}

	function preventDefaults(event: Event) {
		event.preventDefault();
		event.stopPropagation();
	}

</script>		
        
        <div class="space-y-6 step-content-enter">
						<h3 class="text-xl font-medium text-gray-800 dark:text-gray-200">
							{$i18n.t('Course Materials')}
						</h3>

						<div class="mt-2">
							<h4 class="text-gray-700 dark:text-gray-300 mb-6">
								{$i18n.t('Attach Course Materials')}
							</h4>
                            </div>

                            <!-- File upload area -->
							<div
								class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
								on:click={() => document.getElementById('file-upload')?.click()}
								on:dragover={preventDefaults}
								on:dragenter={preventDefaults}
								on:drop={handleFileDrop}
							>
								<input
									type="file"
									id="file-upload"
									class="hidden"
									multiple
									on:change={handleFileChange}
									accept=".pdf,.doc,.docx,.pptx,.mp4"
								/>
                            {#if uploadedFiles.length > 0}
										<div class="mt-4 p-2 bg-blue-50 dark:bg-blue-900/20 rounded w-full max-w-md">
											<p class="text-sm text-blue-700 dark:text-blue-300 font-medium">
												{uploadedFiles.length}
												{$i18n.t('file(s) selected')}
											</p>
											<ul class="text-xs text-left mt-1 max-h-16 overflow-y-auto">
												{#each uploadedFiles as file}
													<li class="truncate text-gray-600 dark:text-gray-300">{file.name}</li>
												{/each}
											</ul>
										</div>
							{/if}
                 </div>

        </div>