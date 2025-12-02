<script setup lang="ts">
const { data: page } = await useAsyncData("index", () =>
  queryCollection("index").first(),
);

const title = page.value?.seo?.title || page.value?.title;
const description = page.value?.seo?.description || page.value?.description;

useSeoMeta({
  titleTemplate: "",
  title,
  ogTitle: title,
  description,
  ogDescription: description,
});

const raw_link: Ref<string> = ref("");
const open_results: Ref<boolean> = ref(false);

watch(raw_link, (value) => {
  const sanitized = value.replace(/^https?:\/\//i, "");
  if (sanitized !== value) raw_link.value = sanitized;
});

async function shortenURL() {
  return new Promise<void>((res) =>
    setTimeout(() => {
      open_results.value = true;
      res();
    }, 1000),
  );
}
</script>

<template>
  <div v-if="page">
    <UPageHero :title="page.title" :description="page.description">
      <template #top>
        <HeroBackground />
      </template>

      <template #title>
        <MDC :value="page.title" unwrap="p" />
      </template>

      <template #links>
        <UInput
          v-model="raw_link"
          placeholder="example.com"
          size="xl"
          :ui="{
            base: 'pl-14.5',
            leading: 'pointer-events-none',
          }"
        >
          <template #leading>
            <p class="text-sm text-muted">https://</p>
          </template>
        </UInput>

        <UButton
          icon="i-lucide-wand-2"
          size="xl"
          color="primary"
          variant="outline"
          loading-auto
          @click="shortenURL"
          >Shorten</UButton
        >
      </template>
    </UPageHero>

    <UModal v-model:open="open_results">
      <template #content>
        <Placeholder class="h-48 m-4" />
      </template>
    </UModal>

    <UPageSection
      :title="page.features.title"
      :description="page.features.description"
    >
      <UPageGrid>
        <UPageCard
          v-for="(item, index) in page.features.items"
          :key="index"
          v-bind="item"
          spotlight
        >
          <template #leading>
            <UIcon :name="item.icon" class="size-5 shrink-0 text-primary" />
            <UBadge v-if="item.upcoming" label="Upcoming" class="ml-2.5" />
          </template>
        </UPageCard>
      </UPageGrid>
    </UPageSection>
  </div>
</template>
