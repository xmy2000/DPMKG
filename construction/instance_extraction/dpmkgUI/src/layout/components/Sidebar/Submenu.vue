<template>
  <el-menu-item v-if="!menu.children" :index="menu.url">
    <item :icon="menu.icon" :title="menu.title" />
  </el-menu-item>
  <el-sub-menu v-else :index="menu.url">
    <template #title>
      <item :icon="menu.icon" :title="menu.title" />
    </template>
    <submenu
      v-for="submenu in menu.children"
      :key="submenu.url"
      :is-nest="true"
      :menu="submenu"
    />
  </el-sub-menu>
</template>
<script>
import { defineComponent } from 'vue'
import Item from './Item.vue'
export default defineComponent({
  name: 'Submenu',
  components: {
    Item,
  },
  props: {
    menu: {
      type: Object,
      required: true,
    },
    isNest: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
