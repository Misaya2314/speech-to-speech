# 测试指南

本项目使用 [Vitest](https://vitest.dev/) 作为测试框架，结合 [@vue/test-utils](https://test-utils.vuejs.org/) 和 [@testing-library/vue](https://testing-library.com/docs/vue-testing-library/intro) 进行 Vue 组件测试。

## 运行测试

可以通过以下命令运行测试：

```bash
# 运行所有测试
npm test

# 以监视模式运行测试（修改文件时自动重新运行）
npm run test:watch
```

## 注意事项

当前版本的 Vitest 和 @vitest/coverage-v8 之间存在版本不兼容问题，所以覆盖率测试暂不可用。如果需要获取覆盖率报告，请执行以下修复操作：

```bash
# 删除现有的 vitest 和 @vitest/coverage-v8
npm uninstall vitest @vitest/coverage-v8

# 安装特定版本的 vitest 和匹配的 @vitest/coverage-v8
npm install vitest@1.2.1 @vitest/coverage-v8@1.2.1 --save-dev

# 然后运行覆盖率测试
npm run test:coverage
```

## 测试文件结构

- `tests/unit/`: 单元测试文件
  - `example.spec.ts`: 基本测试示例
  - `test-utils.spec.ts`: 工具函数测试示例
  - `SimpleCounter.spec.ts`: 计数器组件测试示例
  - `ToolBar.spec.ts`: 工具栏组件测试示例
  - `websocket-client.spec.ts`: WebSocket 客户端测试示例
- `tests/setup.ts`: 测试环境配置
- `tests/vitest.d.ts`: TypeScript 类型声明

## 编写测试

### 组件测试示例

```typescript
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import MyComponent from "@/components/MyComponent.vue";

describe("MyComponent.vue", () => {
  it("renders correctly", () => {
    const wrapper = mount(MyComponent, {
      props: {
        // 组件属性...
      },
    });

    expect(wrapper.text()).toContain("预期文本");
  });
});
```

### 工具函数测试示例

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "@/utils/myUtils";

describe("myFunction", () => {
  it("returns expected result", () => {
    const result = myFunction(1, 2);
    expect(result).toBe(3);
  });
});
```

## 测试最佳实践

1. **保持测试简单**：每个测试应该只测试一个功能点。
2. **使用有意义的名称**：测试名称应该清晰描述测试内容。
3. **使用数据测试属性**：对于组件测试，使用 `data-testid` 属性选择元素更加稳定。
4. **模拟外部依赖**：使用 `vi.mock()` 模拟外部依赖，以保持测试的独立性。
5. **使用测试钩子**：使用 `beforeEach` 和 `afterEach` 钩子设置和清理测试环境。
6. **避免测试实现细节**：测试组件的行为而不是实现细节，使测试更加健壮。
