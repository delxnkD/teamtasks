document.addEventListener("DOMContentLoaded", function () {

  const jsonFetch = (url, opts = {}) => {
    const headers = opts.headers || {};
    headers["Content-Type"] = "application/json";
    return fetch(url, Object.assign({ credentials: "same-origin", headers }, opts));
  };


  const addForm = document.getElementById("addTaskForm");
  if (addForm) {
    addForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const listId = addForm.dataset.listId;
      const titleEl = document.getElementById("title");
      const descEl = document.getElementById("desc");
      const title = titleEl.value.trim();
      const description = descEl.value.trim();
      if (!title) return showToast("Title required");

      const addBtn = document.getElementById("addBtn");
      addBtn.disabled = true;
      try {
        const res = await jsonFetch(`/api/lists/${listId}/tasks`, {
          method: "POST",
          body: JSON.stringify({ title, description }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          showToast(err.error || "Failed to add task");
          addBtn.disabled = false;
          return;
        }

        location.reload();
      } catch (err) {
        console.error(err);
        showToast("Network error");
        addBtn.disabled = false;
      }
    });
  }

  const tasksContainer = document.getElementById("tasksContainer");
  if (tasksContainer) {
    tasksContainer.addEventListener("click", async function (e) {
      const toggleBtn = e.target.closest(".js-toggle");
      if (toggleBtn) {
        const taskId = toggleBtn.dataset.taskId;
        const currentlyDone = toggleBtn.dataset.done === "true";
        toggleBtn.disabled = true;
        try {
          const res = await jsonFetch(`/api/tasks/${taskId}/toggle`, {
            method: "POST",
            body: JSON.stringify({ done: !currentlyDone }),
          });
          if (!res.ok) {
            showToast("Couldn't toggle task");
            toggleBtn.disabled = false;
            return;
          }

          const item = document.querySelector(`.task-item[data-task-id='${taskId}']`)
          if (item) item.classList.toggle("done", !currentlyDone);
          toggleBtn.dataset.done = (!currentlyDone).toString();
          toggleBtn.disabled = false;
        } catch (err) {
          console.error(err);
          showToast("Network error");
          toggleBtn.disabled = false;
        }
        return;
      }

      const delBtn = e.target.closest(".js-delete");
      if (delBtn) {
        const taskId = delBtn.dataset.taskId;
        if (!confirm("Delete this task?")) return;
        delBtn.disabled = true;
        try {
          const res = await fetch(`/api/tasks/${taskId}`, {
            method: "DELETE",
            credentials: "same-origin",
          });
          if (!res.ok) {
            showToast("Failed to delete task");
            delBtn.disabled = false;
            return;
          }

          const item = document.querySelector(`.task-item[data-task-id='${taskId}']`);
          if (item) item.remove();
        } catch (err) {
          console.error(err);
          showToast("Network error");
          delBtn.disabled = false;
        }
        return;
      }
    });
  }

  function showToast(msg) {
    let el = document.getElementById("simpleToast");
    if (!el) {
      el = document.createElement("div");
      el.id = "simpleToast";
      el.style.position = "fixed";
      el.style.right = "18px";
      el.style.bottom = "18px";
      el.style.padding = "10px 14px";
      el.style.borderRadius = "10px";
      el.style.background = "rgba(15,23,36,0.92)";
      el.style.color = "white";
      el.style.boxShadow = "0 8px 20px rgba(2,6,23,0.25)";
      el.style.zIndex = 9999;
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.opacity = "1";
    setTimeout(() => {
      el.style.transition = "opacity .6s ease";
      el.style.opacity = "0";
    }, 2200);
  }
});
