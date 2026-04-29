from __future__ import annotations

from datetime import datetime
from typing import Any, Callable


def seed_demo_common_data(cur: Any, *, now_str: Callable[[], str]) -> None:
  t = now_str()

  cur.execute('SELECT COUNT(1) AS cnt FROM crud_items')
  cnt = int(cur.fetchone()['cnt'])
  if cnt == 0:
    seed = [
      ('item-1', '示例物料A', 'MAT-001', '本地初始化数据', 0, t, t),
      ('item-2', '示例物料B', 'MAT-002', '可直接编辑删除', 0, t, t),
    ]
    cur.executemany(
      '''
      INSERT INTO crud_items(id, name, code, remark, status, create_time, update_time)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ''',
      seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM projects')
  project_cnt = int(cur.fetchone()['cnt'])
  if project_cnt == 0:
    project_seed = [
      (
        'proj-1',
        'PRJ-2026-001',
        '数字化仓储升级',
        '王工',
        1,
        1,
        45,
        '2026-03-01',
        '2026-05-30',
        '示例重点项目',
        t,
        t,
      ),
      (
        'proj-2',
        'PRJ-2026-002',
        '质量追溯平台',
        '李工',
        2,
        0,
        10,
        '2026-03-10',
        '2026-06-30',
        '示例规划项目',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO projects(
        id, project_code, project_name, owner_name, priority, status, progress,
        start_date, end_date, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      project_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM basic_infos')
  basic_cnt = int(cur.fetchone()['cnt'])
  if basic_cnt == 0:
    basic_seed = [
      ('公司A', 1, None, t, t),
      ('进行中', 2, None, t, t),
      ('销售一部', 3, None, t, t),
      ('标准类', 4, None, t, t),
      ('快递', 5, None, t, t),
      ('仓库收货', 6, None, t, t),
      ('A级', 7, None, t, t),
      ('焊接', 8, None, t, t),
      ('标准工艺库', 9, None, t, t),
      ('A仓位', 11, None, t, t),
      ('顺丰', 12, None, t, t),
      ('通用设备', 13, None, t, t),
      ('测试设备', 14, None, t, t),
      ('总部部门', 15, None, t, t),
      ('成品', 99, None, t, t),
    ]
    cur.executemany(
      '''
      INSERT INTO basic_infos(name, type, parent_id, create_time, update_time)
      VALUES (?, ?, ?, ?, ?)
      ''',
      basic_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM workstations')
  workstation_cnt = int(cur.fetchone()['cnt'])
  if workstation_cnt == 0:
    workstation_seed = [
      (
        'ws-1',
        1001,
        '装配工位A',
        1,
        1,
        '1',
        '2',
        '1',
        '本地初始化工位',
        t,
        t,
      ),
      (
        'ws-2',
        1002,
        '测试工位B',
        2,
        1,
        '1',
        '3',
        '1',
        '本地初始化工位',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO workstations(
        id, workstation_no, workstation_name, workstation_type, status,
        responsible_person, dept_id, process_library_id, remarks, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      workstation_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM devices')
  device_cnt = int(cur.fetchone()['cnt'])
  if device_cnt == 0:
    device_seed = [
      (
        'dev-1',
        '扫码枪A',
        'DEV-001',
        'SM-100',
        '13',
        'ws-1',
        '1',
        1,
        '本地初始化设备',
        '',
        t,
        t,
      ),
      (
        'dev-2',
        '测试仪B',
        'DEV-002',
        'TM-200',
        '14',
        'ws-2',
        '1',
        2,
        '本地初始化设备',
        '',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO devices(
        id, device_name, device_number, model, device_category_id, workstation_id,
        responsible_person, status, remarks, scrap_reason, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      device_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM scan_binding_processes')
  scan_cnt = int(cur.fetchone()['cnt'])
  if scan_cnt == 0:
    cur.execute(
      '''
      INSERT INTO scan_binding_processes(scan_asset_number, identifier, process_id, create_time, update_time)
      VALUES (?, ?, ?, ?, ?)
      ''',
      ('DEV-001', 'SCANNER-A', 1, t, t),
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM code_rules')
  rule_cnt = int(cur.fetchone()['cnt'])
  if rule_cnt == 0:
    code_rule_seed = [
      ('rule-1', 1, 'TASK', '生产任务编码规则', 0, '默认规则', t, t),
      ('rule-2', 2, 'WO', '工序工单编码规则', 0, '默认规则', t, t),
      ('rule-3', 3, 'PRD', '产品信息编码规则', 0, '默认规则', t, t),
    ]
    cur.executemany(
      '''
      INSERT INTO code_rules(id, type, prefix, rule_name, is_enable, remark, create_time, update_time)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      code_rule_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM sys_log_users')
  log_cnt = int(cur.fetchone()['cnt'])
  if log_cnt == 0:
    log_seed = [
      (1, '管理员登录系统', 'LOG-1001', '系统管理员', '1', '系统管理员', t, t, 'LOCAL'),
      (1, '更新系统参数配置', 'LOG-1002', '系统管理员', '1', '系统管理员', t, t, 'LOCAL'),
      (0, '查看工位信息列表', 'LOG-1003', '普通用户', '2', '普通用户', t, t, 'LOCAL'),
    ]
    cur.executemany(
      '''
      INSERT INTO sys_log_users(
        type, content, sys_log_id, creator, create_by, real_name, create_time, update_time, tenant_code
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      log_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM sys_backup_infos')
  backup_cnt = int(cur.fetchone()['cnt'])
  if backup_cnt == 0:
    backup_seed = [
      (
        'bak-1',
        f'local-backup-{datetime.now().strftime("%Y%m%d")}-manual.sql',
        1,
        1,
        '-- local backup snapshot',
        '系统管理员',
        t,
        t,
      ),
      (
        'bak-2',
        f'local-backup-{datetime.now().strftime("%Y%m%d")}-auto.sql',
        2,
        1,
        '-- auto backup snapshot',
        '系统管理员',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO sys_backup_infos(
        id, name, type, status, file_content, create_name, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      backup_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM sys_backup_configs')
  backup_cfg_cnt = int(cur.fetchone()['cnt'])
  if backup_cfg_cnt == 0:
    cur.execute(
      '''
      INSERT INTO sys_backup_configs(
        id, name, enabled, cron_expression, retention_days, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
      ''',
      ('plan-1', '默认备份计划', 1, '0 0 2 * * ?', 30, t, t),
    )
