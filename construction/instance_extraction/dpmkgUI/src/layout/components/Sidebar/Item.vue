<template>
  <svg-icon class="icon" v-if="isCustomSvg" :name="icon" />
  <component :is="icon" v-else-if="!!icon" class="icon" />
  <span>{{ $t(title) }}</span>
</template>

<script>
import { computed, defineComponent } from 'vue'

export default defineComponent({
  props: ['title', 'icon'],
  setup({ icon }) {
    const isCustomSvg = computed(() => icon && icon.startsWith('icon-'))

    return {
      isCustomSvg,
    }
  },
})
</script>
<style lang="scss" scoped>
.icon {
  margin-right: 10px;
  width: 16px !important;
  height: 16px !important;
  font-size: 16px;
  text-align: center;
  color: currentColor;
}
</style>
