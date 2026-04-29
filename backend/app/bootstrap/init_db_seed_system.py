from __future__ import annotations

from typing import Any, Callable


def seed_system_data(
  cur: Any,
  *,
  now_str: Callable[[], str],
  hash_password: Callable[[str], str],
  is_password_hashed: Callable[[str], bool],
  menu_tree: Callable[[], list[dict[str, Any]]],
  flatten_menu_ids: Callable[[list[dict[str, Any]]], list[str]],
) -> None:
  cur.execute(
    '''
    INSERT OR IGNORE INTO roles(role_id, role_name, role_code, role_desc, del_flag, create_time, update_time)
    VALUES ('1', '系统管理员', 'ROLE_ADMIN', '系统默认管理员角色', '0', ?, ?)
    ''',
    (now_str(), now_str()),
  )
  cur.execute(
    '''
    INSERT OR IGNORE INTO roles(role_id, role_name, role_code, role_desc, del_flag, create_time, update_time)
    VALUES ('2', '普通用户', 'ROLE_USER', '系统默认普通用户角色', '0', ?, ?)
    ''',
    (now_str(), now_str()),
  )
  cur.execute(
    '''
    UPDATE roles
    SET role_code = COALESCE(NULLIF(role_code, ''), CASE role_id WHEN '1' THEN 'ROLE_ADMIN' ELSE 'ROLE_USER' END),
        role_desc = COALESCE(NULLIF(role_desc, ''), CASE role_id WHEN '1' THEN '系统默认管理员角色' ELSE '系统默认普通用户角色' END),
        create_time = COALESCE(NULLIF(create_time, ''), ?),
        update_time = COALESCE(NULLIF(update_time, ''), ?)
    WHERE role_id IN ('1', '2')
    ''',
    (now_str(), now_str()),
  )

  t = now_str()
  cur.execute(
    '''
    INSERT OR IGNORE INTO depts(dept_id, name, parent_id, sort_order, enabled, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    ('1', '总部', '0', 0, 0, t, t),
  )
  cur.execute(
    '''
    INSERT OR IGNORE INTO depts(dept_id, name, parent_id, sort_order, enabled, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    ('2', '生产部', '1', 10, 0, t, t),
  )
  cur.execute(
    '''
    INSERT OR IGNORE INTO depts(dept_id, name, parent_id, sort_order, enabled, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    ('3', '质量部', '1', 20, 0, t, t),
  )

  cur.execute(
    '''
    INSERT OR IGNORE INTO users(
      user_id, username, password, real_name, phone, email, enabled, role_id, dept_id, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    ('1', 'admin', 'admin123', '系统管理员', '13800000000', 'admin@local.mes', 0, '1', '1', t, t),
  )
  cur.execute("UPDATE users SET dept_id = '1' WHERE dept_id IS NULL OR TRIM(dept_id) = ''")

  cur.execute(
    "INSERT OR IGNORE INTO system_config(id, company_name, system_name, version) VALUES (1, '本地制造企业', 'MES本地版', '1.0.0')",
  )

  default_menu_ids = flatten_menu_ids(menu_tree())
  role_menu_seed = [(role_id, menu_id) for role_id in ('1', '2') for menu_id in default_menu_ids]
  cur.executemany('INSERT OR IGNORE INTO role_menus(role_id, menu_id) VALUES (?, ?)', role_menu_seed)

  cur.execute('SELECT user_id, password FROM users')
  user_rows = cur.fetchall()
  for row in user_rows:
    raw_pwd = str(row['password'] or '')
    if raw_pwd and not is_password_hashed(raw_pwd):
      cur.execute(
        'UPDATE users SET password = ?, update_time = ? WHERE user_id = ?',
        (hash_password(raw_pwd), now_str(), str(row['user_id'])),
      )
