<template>
  <el-menu :default-active="activeIndex" mode="horizontal" :ellipsis="false" :router="true"
    style="border: 0; top: 0; left: 0; width: 100%; z-index: 1000; background-color: #ffffff; justify-content: center;">

    <!-- Conditionally render the logo button only when not on the homepage -->
    <!-- <template v-if="$route.path !== '/'">
      <el-menu-item index="/">
        <img src="/favicon.svg" alt="Logo" style="width: 150px; height: 50px;" />
      </el-menu-item>
    </template> -->

    <!-- Apply align-right class to the following items -->
    <!-- <el-menu-item index="/" class="align-right">Home</el-menu-item>

    <el-sub-menu index="/">
      <template #title><span class="menu-item-text">Search</span></template>  
      <el-menu-item index="/byseq">by sequence</el-menu-item>
      <el-menu-item index="/bystr">by structure</el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/Explore">Visualize</el-menu-item>
    <el-menu-item index="/phylogenomics">Phylogeny</el-menu-item>
    <el-menu-item index="/download">Download</el-menu-item>
    <el-menu-item index="/about">About</el-menu-item> -->
    <el-menu-item index="/" class="menu-item"><span class="menu-item-text">Home</span></el-menu-item>

    <el-sub-menu index="/">
      <template #title><span class="menu-item-text">Search</span></template>
      <el-menu-item index="/bysequence">by sequence</el-menu-item>
      <el-menu-item index="/bystructure">by structure</el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/visualize" class="menu-item"><span class="menu-item-text">Visualize</span></el-menu-item>
    <el-menu-item index="/phylogeny" class="menu-item"><span class="menu-item-text">Phylogeny</span></el-menu-item>
    <el-menu-item index="/download" class="menu-item"><span class="menu-item-text">Download</span></el-menu-item>
    <el-menu-item index="/about" class="menu-item"><span class="menu-item-text">About</span></el-menu-item>
  </el-menu>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
const activeIndex = ref('/')
</script>

<style scoped>
/* Center the menu */
.el-menu {
  display: flex;
  justify-content: center; /* Centers the menu items */
  gap: 20px; /* Adds spacing between the menu items */
}

.menu-item {
  padding: 0 15px; /* Optional padding to make the menu items more spacious */
}

.menu-item-text {
  font-size: 25px !important; /* Ensure the text is the same size */
  font-family: "Helvetica", Times, Sans-serif;
  font-weight: bold;
}
</style>
