const tools = {
  echo: { enabled: true },
  report: { enabled: true },
};

const labelPath = ["Root", "Messaging", "Echo"];
let labelIndex = 0;

const labelCurrent = document.querySelector("[data-testid='label-current']");
const labelButton = document.querySelector("[data-testid='next-label']");

labelButton.addEventListener("click", () => {
  labelIndex = (labelIndex + 1) % labelPath.length;
  labelCurrent.textContent = labelPath[labelIndex];
});

function updateTool(toolName) {
  const status = document.querySelector(`[data-testid='status-${toolName}']`);
  const button = document.querySelector(`[data-testid='toggle-${toolName}']`);
  const tool = tools[toolName];
  status.textContent = tool.enabled ? "Enabled" : "Disabled";
  button.textContent = tool.enabled ? "Disable" : "Enable";
}

Object.keys(tools).forEach((toolName) => {
  const button = document.querySelector(`[data-testid='toggle-${toolName}']`);
  button.addEventListener("click", () => {
    tools[toolName].enabled = !tools[toolName].enabled;
    updateTool(toolName);
  });
  updateTool(toolName);
});
