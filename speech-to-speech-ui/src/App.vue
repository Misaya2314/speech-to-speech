<template>
  <div class="app-container">
    <el-config-provider>
      <router-view />
    </el-config-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { ElConfigProvider } from "element-plus";

export default defineComponent({
  name: "App",
  components: {
    ElConfigProvider,
  },
});
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, "PingFang SC",
    "Hiragino Sans GB", Arial, sans-serif;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

.app-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
}

/* 消除Element Plus按钮外边框 */
.el-button:focus {
  box-shadow: none !important;
}
</style>
