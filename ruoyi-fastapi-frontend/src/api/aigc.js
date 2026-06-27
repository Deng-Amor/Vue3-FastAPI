import request from "@/utils/request";

export function listMaterials(query) {
  return request({
    url: "/aigc/material/list",
    method: "get",
    params: query,
  });
}

export function addMaterial(data) {
  return request({
    url: "/aigc/material",
    method: "post",
    data,
  });
}

export function delMaterial(materialIds) {
  return request({
    url: "/aigc/material/" + materialIds,
    method: "delete",
  });
}

export function listWorkflows() {
  return request({
    url: "/aigc/workflow/list",
    method: "get",
  });
}

export function addWorkflow(data) {
  return request({
    url: "/aigc/workflow",
    method: "post",
    data,
  });
}

export function runWorkflow(workflowId) {
  return request({
    url: `/aigc/workflow/${workflowId}/run`,
    method: "post",
  });
}

export function rollbackWorkflow(workflowId, targetNode) {
  return request({
    url: `/aigc/workflow/${workflowId}/rollback`,
    method: "post",
    data: { targetNode },
  });
}

