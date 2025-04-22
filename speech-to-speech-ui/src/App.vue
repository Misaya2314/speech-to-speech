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
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500;700&display=swap");

/* 可以使用在线CDN或者本地字体文件 */
@font-face {
  font-family: "Nico Moji";
  src: url("https://fonts.googleapis.com/css2?family=Nico+Moji&display=swap");
  font-weight: normal;
  font-style: normal;
}

/* 假设方正小标宋字体存放在assets目录下 */
@font-face {
  font-family: "FZXiaoBiaoSong-B05";
  src: local("FZXiaoBiaoSong-B05"), local("FangZhengXiaoBiaoSongJianTi");
  font-weight: normal;
  font-style: normal;
}

/* 全局样式 */
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: "Inter", "Microsoft YaHei", Arial, sans-serif;
}

#app {
  height: 100%;
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
