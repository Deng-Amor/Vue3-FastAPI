<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>视频生成工作流</span>
          <el-button type="primary" icon="Plus" @click="openDialog">新建工作流</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="workflows" @row-click="selectWorkflow">
        <el-table-column prop="workflowName" label="名称" min-width="180" />
        <el-table-column prop="status" label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status] || 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currentNode" label="当前节点" width="150" />
        <el-table-column prop="ratio" label="比例" width="90" />
        <el-table-column prop="finalVideo" label="最终视频" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" icon="VideoPlay" @click.stop="run(row)">运行</el-button>
            <el-dropdown @command="(node) => rollback(row, node)">
              <el-button link type="primary" icon="RefreshLeft">回滚</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="node in nodes" :key="node.name" :command="node.name">
                    {{ node.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row v-if="current" :gutter="16" class="detail-row">
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>节点进度</template>
          <el-steps direction="vertical" :active="activeIndex" finish-status="success">
            <el-step v-for="node in nodes" :key="node.name" :title="node.label" :description="node.name" />
          </el-steps>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>节点数据</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="服装参考图">{{ current.image || "-" }}</el-descriptions-item>
            <el-descriptions-item label="模特参考图">{{ current.image1 || "-" }}</el-descriptions-item>
            <el-descriptions-item label="动作参考视频">{{ current.video || "-" }}</el-descriptions-item>
            <el-descriptions-item label="生成提示词">
              <pre class="prompt">{{ current.prompt || "-" }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="清理结果">
              {{ (current.cleanResult || []).join(", ") || "-" }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialog.visible" title="新建视频生成工作流" width="680px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="工作流名称">
          <el-input v-model="form.workflowName" placeholder="例如：灰色吊带裙手势舞" />
        </el-form-item>
        <el-form-item label="服装参考图">
          <el-input v-model="form.image" placeholder="image：衣服/商品参考图地址" />
        </el-form-item>
        <el-form-item label="模特参考图">
          <el-input v-model="form.image1" placeholder="image1：模特参考图地址" />
        </el-form-item>
        <el-form-item label="动作参考视频">
          <el-input v-model="form.video" placeholder="video：同类舞蹈视频地址" />
        </el-form-item>
        <el-form-item label="画面比例">
          <el-select v-model="form.ratio" style="width: 100%">
            <el-option label="竖屏 9:16" value="9:16" />
            <el-option label="横屏 16:9" value="16:9" />
            <el-option label="方形 1:1" value="1:1" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { addWorkflow, listWorkflows, rollbackWorkflow, runWorkflow } from "@/api/aigc";

const loading = ref(false);
const workflows = ref([]);
const current = ref(null);
const dialog = reactive({ visible: false });
const form = reactive({
  workflowName: "",
  image: "",
  image1: "",
  video: "",
  ratio: "9:16",
});
const nodes = [
  { name: "merge_image", label: "组合图片" },
  { name: "gen_prompt", label: "生成提示词" },
  { name: "gen_img", label: "图片生成" },
  { name: "mimic_action", label: "动作模仿" },
  { name: "gen_video", label: "视频生成" },
  { name: "clean_data", label: "后置清理" },
];
const statusType = {
  draft: "info",
  waiting_api: "warning",
  completed: "success",
  failed: "danger",
  rolled_back: "warning",
};
const activeIndex = computed(() => {
  if (!current.value) return 0;
  return Math.max(0, nodes.findIndex((item) => item.name === current.value.currentNode));
});

function resetForm() {
  form.workflowName = "";
  form.image = "";
  form.image1 = "";
  form.video = "";
  form.ratio = "9:16";
}

function openDialog() {
  resetForm();
  dialog.visible = true;
}

function selectWorkflow(row) {
  current.value = row;
}

async function getList() {
  loading.value = true;
  try {
    const res = await listWorkflows();
    workflows.value = res.data || [];
    if (!current.value && workflows.value.length) current.value = workflows.value[0];
  } finally {
    loading.value = false;
  }
}

async function submit() {
  const res = await addWorkflow(form);
  ElMessage.success("保存成功");
  dialog.visible = false;
  await getList();
  current.value = res.data;
}

async function run(row) {
  const res = await runWorkflow(row.workflowId);
  ElMessage.success("运行完成");
  await getList();
  current.value = res.data;
}

async function rollback(row, node) {
  const res = await rollbackWorkflow(row.workflowId, node);
  ElMessage.success("回滚完成");
  await getList();
  current.value = res.data;
}

getList();
</script>

<style scoped>
.card-header {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.detail-row {
  margin-top: 16px;
}

.prompt {
  margin: 0;
  white-space: pre-wrap;
}
</style>
