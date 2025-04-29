import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ToolBar from '@/components/ToolBar.vue';

// 模拟element-plus图标
vi.mock('@element-plus/icons-vue', () => ({
  Select: 'select-icon',
  DArrowRight: 'darrow-right-icon',
  Refresh: 'refresh-icon',
  ZoomIn: 'zoom-in-icon',
  Odometer: 'odometer-icon',
  Microphone: 'microphone-icon',
}));

describe('ToolBar.vue', () => {
  it('渲染正确的组件结构', () => {
    const wrapper = mount(ToolBar, {
      props: {
        isListening: false
      },
      global: {
        stubs: {
          'el-button': true,
          'el-tooltip': true
        }
      }
    });
    
    // 验证工具组的数量
    const toolGroups = wrapper.findAll('.tool-group');
    expect(toolGroups.length).toBe(3);
  });
  
  // 简化测试，直接测试emit函数而不是通过DOM事件
  it('触发toggle-listening事件', async () => {
    const wrapper = mount(ToolBar, {
      props: {
        isListening: false
      },
      global: {
        stubs: {
          'el-button': true,
          'el-tooltip': true
        }
      }
    });
    
    // 直接调用组件内的方法
    await wrapper.vm.toggleListening();
    
    // 验证是否触发了toggle-listening事件
    expect(wrapper.emitted()).toHaveProperty('toggle-listening');
    expect(wrapper.emitted()['toggle-listening']).toHaveLength(1);
  });
}); 