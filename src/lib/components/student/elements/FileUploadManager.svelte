<script lang="ts">
	import { getContext } from 'svelte';
    import type { Writable } from 'svelte/store';


	// Get i18n from context with proper typing 
	interface I18n {
		t: (key: string) => string;
	}
	const i18n = getContext<Writable<I18n>>('i18n');

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
        </div>