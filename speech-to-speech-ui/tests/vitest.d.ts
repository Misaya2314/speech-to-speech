/// <reference types="vitest" />
/// <reference types="vite/client" />
/// <reference types="@testing-library/jest-dom" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  // 其他环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 