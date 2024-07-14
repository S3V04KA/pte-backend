from h2o_wave import main, app, Q, ui
from app.DB import get_users

async def make_table(q: Q):
  users = await get_users()
  columns = [
    ui.table_column(name='name', label='Логин'),
    ui.table_column(name='email', label='Почта'),
    ui.table_column(name='full_name', label='Полное имя'),
    ui.table_column(name='created_at', label='Создан'),
  ]
  
  return ui.table(
    name='users',
    columns=columns,
    rows=[ui.table_row(name=user['username'], cells=[user['username'], user['email'], user['full_name'], user['created_at']]) for user in users],
    multiple=True
  )

async def show_users(q: Q):
  q.page['users'] = ui.form_card(
    box='1 1 6 7',
    items=[await make_table(), ui.buttons([ui.button(name='delete', label='Удалить', primary=True)])]
  )
  
  await q.page.save()