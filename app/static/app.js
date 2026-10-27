const $ = id => document.getElementById(id);
let tasks = [];
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error);
  return result;
}
function render() {
  const filter = document.querySelector('input[name=filter]:checked').value;
  const visible = tasks.filter(task => filter === 'all' || !task.done);
  $('tasks').replaceChildren();
  for (const task of visible) {
    const row = document.createElement('li');
    row.className = 'task' + (task.done ? ' done' : '');
    row.dataset.id = task.id;
    const check = document.createElement('input');
    check.type = 'checkbox'; check.checked = task.done;
    check.setAttribute('aria-label', 'Выполнена: ' + task.title);
    check.onchange = async () => { try { await api(`/api/tasks/${task.id}/toggle`, {}); await load(); } catch (e) { $('task-error').textContent = e.message; } };
    const title = document.createElement('span'); title.textContent = task.title;
    const priority = document.createElement('small'); priority.textContent = task.priority;
    const remove = document.createElement('button'); remove.textContent = 'Удалить';
    remove.onclick = async () => { if (confirm('Удалить задачу?')) { try { await api(`/api/tasks/${task.id}/delete`, {}); await load(); } catch (e) { $('task-error').textContent = e.message; } } };
    row.append(check, title, priority, remove); $('tasks').append(row);
  }
  $('empty').hidden = visible.length > 0;
}
async function load() { tasks = (await api('/api/tasks')).tasks; render(); }
async function showTasks() {
  $('login-panel').hidden = true; $('tasks-panel').hidden = false;
  await load();
  try { $('service-status').textContent = (await api('/api/health')).message; } catch { $('service-status').textContent = 'Сервис недоступен'; }
}
$('login-form').onsubmit = async event => {
  event.preventDefault(); $('login-error').textContent = '';
  try { await api('/api/login', {email: $('email').value, password: $('password').value}); await showTasks(); }
  catch (e) { $('login-error').textContent = e.message; }
};
$('task-form').onsubmit = async event => {
  event.preventDefault(); $('task-error').textContent = '';
  try { await api('/api/tasks', {title: $('title').value, priority: $('priority').value}); $('title').value = ''; await load(); }
  catch (e) { $('task-error').textContent = e.message; }
};
$('logout').onclick = async () => { await api('/api/logout', {}); location.reload(); };
document.querySelectorAll('input[name=filter]').forEach(input => input.onchange = render);
api('/api/tasks').then(showTasks).catch(() => {});
