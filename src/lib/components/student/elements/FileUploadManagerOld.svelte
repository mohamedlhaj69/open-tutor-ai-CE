<script>
      export let text = "Click me";

</script>


<!-- Course Selection step -->
							<div class="space-y-6 step-content-enter">
						<h3 class="text-xl font-medium text-gray-800 dark:text-gray-200">
							{$i18n.t('Course Materials')}
						</h3>

						<div class="mt-2">
							<h4 class="text-gray-700 dark:text-gray-300 mb-6">
								{$i18n.t('Attach Course Materials')}
							</h4>

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

								<div class="flex flex-col items-center">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-12 w-12 text-blue-500 mb-3"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
										/>
									</svg>

									<p class="text-gray-600 dark:text-gray-300 mb-1">
										{$i18n.t('Click to upload or drag and drop files')}
									</p>
									<p class="text-gray-500 dark:text-gray-400 text-xs">
										{$i18n.t('PDF, DOCX, PPTX, MP4 (max 50MB)')}
									</p>

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
							
							<p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
								{$i18n.t('Upload your course materials to get personalized learning assistance')}
							</p>
						</div>
					</div>