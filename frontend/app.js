const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const stagedList = document.getElementById("staged-list");
const uploadBtn = document.getElementById("upload-btn");
const statusEl = document.getElementById("status");
const filesList = document.getElementById("files-list");

let stagedFiles = [];

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function setStatus(message, type = "") {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}

// archivos seleccionados antes de subir
function addFiles(files) {
  for (const file of files) {
    stagedFiles.push(file);
  }
  renderStaged();
}

function renderStaged() {
  stagedList.innerHTML = "";
  stagedFiles.forEach((file) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${file.name}</span>
      <span class="size">${formatSize(file.size)}</span>
    `;
    stagedList.appendChild(li);
  });
  uploadBtn.disabled = stagedFiles.length === 0;
}

// drag and drop
dropzone.addEventListener("dragenter", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
});

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) addFiles(fileInput.files);
  fileInput.value = "";
});

// subida de archivos
uploadBtn.addEventListener("click", async () => {
  if (!stagedFiles.length) return;

  const formData = new FormData();
  stagedFiles.forEach((file) => formData.append("files", file));

  uploadBtn.disabled = true;
  setStatus("Subiendo...");

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    setStatus(`${data.uploaded.length} archivo(s) subido(s)`, "ok");
    stagedFiles = [];
    renderStaged();
    await loadFiles();
  } catch (err) {
    setStatus(`Error al subir: ${err.message}`, "error");
    uploadBtn.disabled = false;
  }
});

// listado y descarga de archivos
async function loadFiles() {
  try {
    const res = await fetch("/api/files");
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderFiles(data.files);
  } catch (err) {
    filesList.innerHTML = `<li class="empty">No se pudo cargar la lista: ${err.message}</li>`;
  }
}

function renderFiles(files) {
  filesList.innerHTML = "";
  if (!files.length) {
    filesList.innerHTML = '<li class="empty">Aun no has subido archivos.</li>';
    return;
  }
  for (const file of files) {
    const li = document.createElement("li");
    const downloadUrl = `/api/download?key=${encodeURIComponent(file.key)}`;
    li.innerHTML = `
      <div>
        <div class="file-name">${file.name}</div>
        <div class="file-meta">${formatSize(file.size)}</div>
      </div>
      <a class="btn-download" href="${downloadUrl}">Descargar</a>
    `;
    filesList.appendChild(li);
  }
}

loadFiles();
