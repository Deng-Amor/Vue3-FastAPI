<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>素材库</span>
          <el-button type="primary" icon="Plus" @click="openDialog">新增素材</el-button>
        </div>
      </template>

      <el-tabs v-model="query.materialType" @tab-change="getList">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="模特" name="model" />
        <el-tab-pane label="衣服" name="clothes" />
        <el-tab-pane label="动作视频" name="action" />
        <el-tab-pane label="场景" name="scene" />
      </el-tabs>

      <el-table v-loading="loading" :data="materials">
        <el-table-column prop="materialName" label="名称" min-width="160" />
        <el-table-column prop="materialType" label="类型" width="130">
          <template #default="{ row }">
            <el-tag>{{ typeText[row.materialType] || row.materialType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="materialUrl" label="素材地址" min-width="260" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" icon="Delete" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog.visible" title="新增素材" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="素材名称">
          <el-input v-model="form.materialName" placeholder="例如：灰色吊带裙商品图" />
        </el-form-item>
        <el-form-item label="素材类型">
          <el-select v-model="form.materialType" style="width: 100%">
            <el-option label="模特" value="model" />
            <el-option label="衣服" value="clothes" />
            <el-option label="动作视频" value="action" />
            <el-option label="场景" value="scene" />
          </el-select>
        </el-form-item>
        <el-form-item label="素材地址">
          <el-input v-model="form.materialUrl" placeholder="先填图片/视频地址，文件上传后续再接" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
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
import { ElMessage, ElMessageBox } from "element-plus";
import { addMaterial, delMaterial, listMaterials } from "@/api/aigc";

const loading = ref(false);
const materials = ref([]);
const query = reactive({ materialType: "" });
const dialog = reactive({ visible: false });
const form = reactive({
  materialName: "",
  materialType: "clothes",
  materialUrl: "",
  remark: "",
});
const typeText = {
  model: "模特",
  clothes: "衣服",
  action: "动作视频",
  scene: "场景",
};

function resetForm() {
  form.materialName = "";
  form.materialType = "clothes";
  form.materialUrl = "";
  form.remark = "";
}

function openDialog() {
  resetForm();
  dialog.visible = true;
}

async function getList() {
  loading.value = true;
  try {
    const res = await listMaterials(query);
    materials.value = res.data || [];
  } finally {
    loading.value = false;
  }
}

async function submit() {
  await addMaterial(form);
  ElMessage.success("保存成功");
  dialog.visible = false;
  getList();
}

function remove(row) {
  ElMessageBox.confirm(`确认删除「${row.materialName}」吗？`, "提示", { type: "warning" }).then(async () => {
    await delMaterial(row.materialId);
    ElMessage.success("删除成功");
    getList();
  });
}

getList();
</script>

<style scoped>
.card-header {
  align-items: center;
  display: flex;
  justify-content: space-between;
}
</style>
