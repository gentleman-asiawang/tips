import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';

export const useTreeStore = defineStore('tree', {
  state: () => ({
    target: '',
    previousTarget: '',
    targetUUID: '', // 添加用于存储 UUID 的字段
  }),
  actions: {
    setTarget(newTarget: string) {
      if (newTarget !== this.target) {
        this.previousTarget = this.target; // 更新 previousTarget 为当前的 target 值
        this.target = newTarget; // 更新 target
        this.targetUUID = uuidv4();
      }
    },
    hasTargetChanged() {
      // 比较 current target 和 previousTarget 是否不同
      return this.target !== this.previousTarget;
    }
  }
});