export function buildFolderTree(folders) {
  const map = new Map();
  folders.forEach((folder) => map.set(folder.id, { ...folder, children: [] }));
  const roots = [];

  map.forEach((folder) => {
    if (folder.parentId && map.has(folder.parentId)) {
      map.get(folder.parentId).children.push(folder);
    } else {
      roots.push(folder);
    }
  });

  return roots;
}

export function buildToolQueryParams({ search, folderPath, labels } = {}) {
  const params = new URLSearchParams();
  if (search) {
    params.set("search", search);
  }
  if (folderPath) {
    params.set("folderPath", folderPath);
  }
  if (labels && labels.length > 0) {
    params.set("labels", labels.join(","));
  }
  return params.toString();
}
