import { apiRequest } from "./api.js";
import { buildFolderTree, buildToolQueryParams } from "./lib.js";

const state = {
  folders: [],
  labels: [],
  tools: [],
  activeTool: null,
  dragToolId: null,
};

const elements = {
  folderTree: document.getElementById("folder-tree"),
  labelTree: document.getElementById("label-tree"),
  labelFilters: document.getElementById("label-filters"),
  toolLabels: document.getElementById("tool-labels"),
  toolList: document.getElementById("tool-list"),
  toolForm: document.getElementById("tool-form"),
  toolId: document.getElementById("tool-id"),
  toolName: document.getElementById("tool-name"),
  toolDescription: document.getElementById("tool-description"),
  toolEnabled: document.getElementById("tool-enabled"),
  toolFolder: document.getElementById("tool-folder"),
  deleteTool: document.getElementById("delete-tool"),
  moveToolForm: document.getElementById("move-tool-form"),
  moveTool: document.getElementById("move-tool"),
  moveFolder: document.getElementById("move-folder"),
  searchForm: document.getElementById("search-form"),
  folderPath: document.getElementById("folder-path"),
  toolSearch: document.getElementById("tool-search"),
  clearSearch: document.getElementById("clear-search"),
  refreshData: document.getElementById("refresh-data"),
  modal: document.getElementById("modal"),
  modalTitle: document.getElementById("modal-title"),
  modalForm: document.getElementById("modal-form"),
  modalType: document.getElementById("modal-type"),
  modalId: document.getElementById("modal-id"),
  modalName: document.getElementById("modal-name"),
  modalParent: document.getElementById("modal-parent"),
  modalParentWrapper: document.getElementById("modal-parent-wrapper"),
  modalCancel: document.getElementById("modal-cancel"),
  toast: document.getElementById("toast"),
};

const API_BASE = "";

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.style.background = isError ? "#b91c1c" : "#0f172a";
  elements.toast.classList.add("show");
  setTimeout(() => elements.toast.classList.remove("show"), 3000);
}

function renderFolderTree() {
  elements.folderTree.innerHTML = "";
  const tree = document.createElement("div");
  tree.className = "tree";

  const roots = buildFolderTree(state.folders);
  if (roots.length === 0) {
    tree.textContent = "No folders yet.";
  } else {
    roots.forEach((folder) => tree.appendChild(renderFolderNode(folder)));
  }

  elements.folderTree.appendChild(tree);
}

function renderFolderNode(folder) {
  const container = document.createElement("div");
  const item = document.createElement("div");
  item.className = "tree-item";
  item.dataset.folderId = folder.id;

  const label = document.createElement("span");
  label.textContent = folder.name;

  const actions = document.createElement("div");
  const editButton = document.createElement("button");
  editButton.textContent = "Edit";
  editButton.className = "secondary";
  editButton.addEventListener("click", () => openModal("folder", folder));

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "Delete";
  deleteButton.className = "danger";
  deleteButton.addEventListener("click", () => deleteFolder(folder.id));

  actions.append(editButton, deleteButton);
  actions.style.display = "flex";
  actions.style.gap = "6px";
  item.append(label, actions);

  item.addEventListener("dragover", (event) => {
    event.preventDefault();
    item.classList.add("drop-target");
  });

  item.addEventListener("dragleave", () => {
    item.classList.remove("drop-target");
  });

  item.addEventListener("drop", async (event) => {
    event.preventDefault();
    item.classList.remove("drop-target");
    const toolId = event.dataTransfer.getData("text/plain");
    if (!toolId) {
      return;
    }
    await moveToolToFolder(toolId, folder.id);
  });

  container.appendChild(item);

  if (folder.children && folder.children.length > 0) {
    const children = document.createElement("div");
    children.className = "tree-children";
    folder.children.forEach((child) => children.appendChild(renderFolderNode(child)));
    container.appendChild(children);
  }

  return container;
}

function renderLabelTree() {
  elements.labelTree.innerHTML = "";
  const tree = document.createElement("div");
  tree.className = "tree";

  if (state.labels.length === 0) {
    tree.textContent = "No labels yet.";
  } else {
    state.labels.forEach((label) => {
      const item = document.createElement("div");
      item.className = "tree-item";
      const name = document.createElement("span");
      name.textContent = label.name;

      const actions = document.createElement("div");
      actions.style.display = "flex";
      actions.style.gap = "6px";
      const editButton = document.createElement("button");
      editButton.textContent = "Edit";
      editButton.className = "secondary";
      editButton.addEventListener("click", () => openModal("label", label));
      const deleteButton = document.createElement("button");
      deleteButton.textContent = "Delete";
      deleteButton.className = "danger";
      deleteButton.addEventListener("click", () => deleteLabel(label.id));
      actions.append(editButton, deleteButton);

      item.append(name, actions);
      tree.appendChild(item);
    });
  }

  elements.labelTree.appendChild(tree);
}

function renderLabelOptions(container, selected = []) {
  container.innerHTML = "";
  if (state.labels.length === 0) {
    container.textContent = "No labels available.";
    return;
  }
  state.labels.forEach((label) => {
    const wrapper = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = label.id;
    checkbox.checked = selected.includes(label.id);
    wrapper.append(checkbox, document.createTextNode(label.name));
    container.appendChild(wrapper);
  });
}

function renderFolderOptions(select, selectedId = "") {
  select.innerHTML = "";
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = "Unassigned";
  select.appendChild(empty);
  state.folders.forEach((folder) => {
    const option = document.createElement("option");
    option.value = folder.id;
    option.textContent = folder.path || folder.name;
    if (String(folder.id) === String(selectedId)) {
      option.selected = true;
    }
    select.appendChild(option);
  });
}

function renderTools() {
  elements.toolList.innerHTML = "";

  if (state.tools.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = "No tools found.";
    row.appendChild(cell);
    elements.toolList.appendChild(row);
    return;
  }

  state.tools.forEach((tool) => {
    const row = document.createElement("tr");
    row.draggable = true;

    row.addEventListener("dragstart", (event) => {
      state.dragToolId = tool.id;
      row.classList.add("dragging");
      event.dataTransfer.setData("text/plain", tool.id);
      event.dataTransfer.effectAllowed = "move";
    });

    row.addEventListener("dragend", () => {
      row.classList.remove("dragging");
      state.dragToolId = null;
    });

    row.innerHTML = `
      <td>${tool.name}</td>
      <td>${tool.enabled ? "Enabled" : "Disabled"}</td>
      <td>${tool.folderPath || "Unassigned"}</td>
      <td>${(tool.labels || []).map((label) => `<span class="tag">${label.name}</span>`).join(" ")}</td>
      <td>
        <button class="secondary" data-action="edit">Edit</button>
      </td>
    `;

    row.querySelector("button[data-action='edit']").addEventListener("click", () => {
      setActiveTool(tool);
    });

    elements.toolList.appendChild(row);
  });
}

function setActiveTool(tool) {
  state.activeTool = tool;
  elements.toolId.value = tool.id || "";
  elements.toolName.value = tool.name || "";
  elements.toolDescription.value = tool.description || "";
  elements.toolEnabled.checked = Boolean(tool.enabled);
  renderFolderOptions(elements.toolFolder, tool.folderId || "");
  renderLabelOptions(elements.toolLabels, (tool.labelIds || []).map(String));
  elements.deleteTool.disabled = !tool.id;
}

function collectSelectedLabels(container) {
  return Array.from(container.querySelectorAll("input[type='checkbox']"))
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.value);
}

function openModal(type, data = {}) {
  elements.modalType.value = type;
  elements.modalId.value = data.id || "";
  elements.modalName.value = data.name || "";

  if (type === "folder") {
    elements.modalTitle.textContent = data.id ? "Edit folder" : "New folder";
    elements.modalParentWrapper.style.display = "flex";
    renderFolderOptions(elements.modalParent, data.parentId || "");
  } else {
    elements.modalTitle.textContent = data.id ? "Edit label" : "New label";
    elements.modalParentWrapper.style.display = "none";
  }

  elements.modal.classList.add("show");
}

function closeModal() {
  elements.modal.classList.remove("show");
}

async function loadData() {
  try {
    const [folders, labels] = await Promise.all([
      apiRequest("/api/folders", {}, API_BASE),
      apiRequest("/api/labels", {}, API_BASE),
    ]);
    state.folders = folders;
    state.labels = labels;
    renderFolderTree();
    renderLabelTree();
    renderFolderOptions(elements.toolFolder, state.activeTool?.folderId || "");
    renderLabelOptions(elements.toolLabels, state.activeTool?.labelIds || []);
    renderFolderOptions(elements.modalParent, "");
    renderFolderOptions(elements.moveFolder, "");
    renderMoveTools();
    renderLabelFilters();
    await loadTools();
  } catch (error) {
    showToast(`Failed to load data: ${error.message}`, true);
  }
}

async function loadTools(query = {}) {
  const params = buildToolQueryParams(query);
  const path = params ? `/api/tools?${params}` : "/api/tools";
  try {
    const tools = await apiRequest(path, {}, API_BASE);
    state.tools = tools;
    renderTools();
    renderMoveTools();
    if (!state.activeTool && tools.length > 0) {
      setActiveTool(tools[0]);
    }
  } catch (error) {
    showToast(`Failed to load tools: ${error.message}`, true);
  }
}

function renderMoveTools() {
  elements.moveTool.innerHTML = "";
  state.tools.forEach((tool) => {
    const option = document.createElement("option");
    option.value = tool.id;
    option.textContent = tool.name;
    elements.moveTool.appendChild(option);
  });
}

function renderLabelFilters() {
  elements.labelFilters.innerHTML = "";
  if (state.labels.length === 0) {
    elements.labelFilters.textContent = "No labels.";
    return;
  }
  state.labels.forEach((label) => {
    const wrapper = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = label.id;
    wrapper.append(checkbox, document.createTextNode(label.name));
    elements.labelFilters.appendChild(wrapper);
  });
}

async function saveTool(event) {
  event.preventDefault();
  const toolId = elements.toolId.value;
  const payload = {
    name: elements.toolName.value.trim(),
    description: elements.toolDescription.value.trim(),
    enabled: elements.toolEnabled.checked,
    folderId: elements.toolFolder.value || null,
    labelIds: collectSelectedLabels(elements.toolLabels),
  };

  try {
    let saved;
    if (toolId) {
      saved = await apiRequest(`/api/tools/${toolId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }, API_BASE);
    } else {
      saved = await apiRequest("/api/tools", {
        method: "POST",
        body: JSON.stringify(payload),
      }, API_BASE);
    }
    showToast("Tool saved.");
    await loadTools();
    if (saved) {
      setActiveTool(saved);
    }
  } catch (error) {
    showToast(`Failed to save tool: ${error.message}`, true);
  }
}

async function deleteTool() {
  const toolId = elements.toolId.value;
  if (!toolId) {
    return;
  }
  try {
    await apiRequest(`/api/tools/${toolId}`, { method: "DELETE" }, API_BASE);
    showToast("Tool deleted.");
    elements.toolForm.reset();
    state.activeTool = null;
    await loadTools();
  } catch (error) {
    showToast(`Failed to delete tool: ${error.message}`, true);
  }
}

async function createOrUpdateFolder(event) {
  event.preventDefault();
  const folderId = elements.modalId.value;
  const payload = {
    name: elements.modalName.value.trim(),
    parentId: elements.modalParent.value || null,
  };
  try {
    if (folderId) {
      await apiRequest(`/api/folders/${folderId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }, API_BASE);
    } else {
      await apiRequest("/api/folders", {
        method: "POST",
        body: JSON.stringify(payload),
      }, API_BASE);
    }
    showToast("Folder saved.");
    closeModal();
    await loadData();
  } catch (error) {
    showToast(`Failed to save folder: ${error.message}`, true);
  }
}

async function createOrUpdateLabel(event) {
  event.preventDefault();
  const labelId = elements.modalId.value;
  const payload = { name: elements.modalName.value.trim() };
  try {
    if (labelId) {
      await apiRequest(`/api/labels/${labelId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }, API_BASE);
    } else {
      await apiRequest("/api/labels", {
        method: "POST",
        body: JSON.stringify(payload),
      }, API_BASE);
    }
    showToast("Label saved.");
    closeModal();
    await loadData();
  } catch (error) {
    showToast(`Failed to save label: ${error.message}`, true);
  }
}

async function deleteFolder(folderId) {
  try {
    await apiRequest(`/api/folders/${folderId}`, { method: "DELETE" }, API_BASE);
    showToast("Folder deleted.");
    await loadData();
  } catch (error) {
    showToast(`Failed to delete folder: ${error.message}`, true);
  }
}

async function deleteLabel(labelId) {
  try {
    await apiRequest(`/api/labels/${labelId}`, { method: "DELETE" }, API_BASE);
    showToast("Label deleted.");
    await loadData();
  } catch (error) {
    showToast(`Failed to delete label: ${error.message}`, true);
  }
}

async function moveToolToFolder(toolId, folderId) {
  try {
    await apiRequest(`/api/tools/${toolId}/move`, {
      method: "POST",
      body: JSON.stringify({ folderId }),
    }, API_BASE);
    showToast("Tool moved.");
    await loadTools();
  } catch (error) {
    showToast(`Failed to move tool: ${error.message}`, true);
  }
}

async function handleMoveTool(event) {
  event.preventDefault();
  const toolId = elements.moveTool.value;
  const folderId = elements.moveFolder.value || null;
  if (!toolId) {
    return;
  }
  await moveToolToFolder(toolId, folderId);
}

function handleSearch(event) {
  event.preventDefault();
  const labels = collectSelectedLabels(elements.labelFilters);
  loadTools({
    folderPath: elements.folderPath.value.trim(),
    labels,
    search: elements.toolSearch.value.trim(),
  });
}

function clearSearch() {
  elements.folderPath.value = "";
  elements.toolSearch.value = "";
  elements.labelFilters.querySelectorAll("input").forEach((checkbox) => {
    checkbox.checked = false;
  });
  loadTools();
}

function setupEventListeners() {
  document.getElementById("new-folder").addEventListener("click", () => openModal("folder"));
  document.getElementById("new-label").addEventListener("click", () => openModal("label"));
  document.getElementById("new-tool").addEventListener("click", () => {
    setActiveTool({ name: "", description: "", enabled: true, labelIds: [] });
  });
  elements.modalCancel.addEventListener("click", closeModal);
  elements.modal.addEventListener("click", (event) => {
    if (event.target === elements.modal) {
      closeModal();
    }
  });

  elements.modalForm.addEventListener("submit", (event) => {
    const type = elements.modalType.value;
    if (type === "folder") {
      createOrUpdateFolder(event);
    } else {
      createOrUpdateLabel(event);
    }
  });

  elements.toolForm.addEventListener("submit", saveTool);
  elements.deleteTool.addEventListener("click", deleteTool);
  elements.moveToolForm.addEventListener("submit", handleMoveTool);
  elements.searchForm.addEventListener("submit", handleSearch);
  elements.clearSearch.addEventListener("click", clearSearch);
  elements.refreshData.addEventListener("click", loadData);
}

setupEventListeners();
loadData();
