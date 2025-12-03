<script setup lang="ts">
// Generate QR Code
import type QRCode from 'qrcode'
import { useDebounceFn } from '@vueuse/core'

const { data: page } = await useAsyncData('index', () =>
  queryCollection('index').first()
)
const config = useRuntimeConfig()

console.log('test:', config.public)
console.log('test2:', process.env.BACKEND_BASE_URL)
console.log('test2:', process.env.PORT)

const title = page.value?.seo?.title || page.value?.title
const description = page.value?.seo?.description || page.value?.description

useSeoMeta({
  titleTemplate: '',
  title,
  ogTitle: title,
  description,
  ogDescription: description
})

// Shorten url algorithm
const rawLink: Ref<string> = ref('')
const openResults: Ref<boolean> = ref(false)
const shortLink: Ref<string> = ref('')
const isShortening: Ref<boolean> = ref(false)

watch(rawLink, (value) => {
  const sanitized = value.replace(/^https?:\/\//i, '')
  if (sanitized !== value) rawLink.value = sanitized
})

async function shortenURL() {
  if (!rawLink.value.trim()) return

  isShortening.value = true
  try {
    const payload = await $fetch<{
      original_url: string
      short_id: string
      short_url: string
    }>('/shorten', {
      baseURL: config.public.backendBaseUrl,
      params: { url: `https://${rawLink.value}` }
    })
    console.log(payload)

    shortLink.value = payload.short_url
    openResults.value = true
    debouncedRenderQr()
  } catch (error) {
    console.error('Failed to shorten URL', error)
  } finally {
    isShortening.value = false
  }
}

let QRCodeLib: typeof QRCode | null = null

const fgColor = ref('#000000') // main color ("dark" modules)
const bgColor = ref('#ffffff') // background color ("light" modules)
const qrCanvas = ref<HTMLCanvasElement | null>(null)

const renderQr = async () => {
  if (!import.meta.client || !qrCanvas.value) return

  try {
    if (!QRCodeLib) {
      const mod = await import('qrcode')
      QRCodeLib = mod.default || mod
    }

    await QRCodeLib.toCanvas(
      qrCanvas.value,
      shortLink.value || `https://${rawLink.value || ''}`,
      {
        margin: 2,
        scale: 8,
        color: {
          dark: fgColor.value, // main
          light: bgColor.value // background
        }
      }
    )
  } catch (err) {
    console.error('Failed to render QR', err)
  }
}

const debouncedRenderQr = useDebounceFn(renderQr, 150)

// initial render
onMounted(renderQr)

// rerender whenever input or colors change
watch([shortLink, fgColor, bgColor], () => {
  debouncedRenderQr()
})

// const downloadQr = () => {
//   if (!qrCanvas.value) return
//   const link = document.createElement('a')
//   link.href = qrCanvas.value.toDataURL('image/png')
//   link.download = 'exq-links-qr.png' // @todo change file name
//   link.click()
// }
</script>

<template>
  <div v-if="page">
    <UPageHero
      :title="page.title"
      :description="page.description"
    >
      <template #top>
        <HeroBackground />
      </template>

      <template #title>
        <MDC
          :value="page.title"
          unwrap="p"
        />
      </template>

      <template #links>
        <UInput
          v-model="rawLink"
          placeholder="example.com"
          size="xl"
          :ui="{
            base: 'pl-14.5',
            leading: 'pointer-events-none'
          }"
        >
          <template #leading>
            <p class="text-sm text-muted">
              https://
            </p>
          </template>
        </UInput>

        <UButton
          icon="i-lucide-wand-2"
          size="xl"
          color="primary"
          variant="outline"
          :loading="isShortening"
          @click="shortenURL"
        >
          Shorten
        </UButton>
      </template>
    </UPageHero>

    <UModal v-model:open="openResults">
      <template #content>
        <ClientOnly>
          <div class="flex items-center justify-center">
            <canvas ref="qrCanvas" />
          </div>
        </ClientOnly>
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
            <UIcon
              :name="item.icon"
              class="size-5 shrink-0 text-primary"
            />
            <UBadge
              v-if="item.upcoming"
              label="Upcoming"
              class="ml-2.5"
            />
          </template>
        </UPageCard>
      </UPageGrid>
    </UPageSection>
  </div>
</template>
