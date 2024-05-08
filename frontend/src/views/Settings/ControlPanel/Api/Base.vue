<script setup lang="ts">
import AuthOptions from "@/components/Settings/General/AuthOptions.vue";
import storeAuth from "@/stores/auth";

// Props
const auth = storeAuth();
</script>

<template>
  <theme />
  <interface-options class="mt-1" />
  <task-status v-if="auth.scopes.includes('tasks.run')" class="mt-1" />
</template>
