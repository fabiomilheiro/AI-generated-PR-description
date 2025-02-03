<!-- Popover.vue -->
<script setup lang="ts">
import { PopoverArrow, PopoverClose, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger>More info</PopoverTrigger>
    <PopoverPortal>
      <PopoverContent>
        Some more info...
        <PopoverClose>Close</PopoverClose>
        <PopoverArrow />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>