const path = require('path');
const PptxGenJS = require('pptxgenjs');

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_16x9';
pptx.author = 'OpenAI Codex';
pptx.company = 'MES Training';
pptx.subject = 'MES project AI collaboration overview';
pptx.title = 'MES 项目基座与 AI 协作开发介绍';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN',
};

const C = {
  dark: '1E2761',
  teal: '2F63F5',
  mint: '6F90FF',
  aqua: '9BB5FF',
  cream: 'F7FAFF',
  white: 'FFFFFF',
  slate: '42557A',
  muted: '596F98',
  soft: 'EEF4FF',
  pale: 'F3F7FF',
  amber: '4F7FFF',
  line: 'D7E2F5',
};

function fullBg(slide, color) {
  slide.background = { color };
}

function addFooter(slide, page, light = true) {
  slide.addText(String(page).padStart(2, '0'), {
    x: 9.15,
    y: 5.1,
    w: 0.4,
    h: 0.25,
    fontFace: 'Calibri',
    fontSize: 11,
    bold: true,
    color: light ? C.teal : C.white,
    align: 'right',
    margin: 0,
  });
}

function addTopMotif(slide, dark = false) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 8.7,
    y: 0.35,
    w: 0.48,
    h: 0.48,
    fill: { color: dark ? C.mint : C.teal },
    line: { color: dark ? C.mint : C.teal, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 9.1,
    y: 0.6,
    w: 0.22,
    h: 0.22,
    fill: { color: dark ? C.amber : C.amber },
    line: { color: C.amber, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 8.1,
    y: 0.48,
    w: 0.45,
    h: 0.12,
    fill: { color: dark ? C.white : C.dark, transparency: dark ? 65 : 88 },
    line: { color: dark ? C.white : C.dark, transparency: 100 },
    rotate: -25,
  });
}

function addTitleBlock(slide, kicker, title, subtitle) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.55,
    y: 0.38,
    w: 2.18,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.teal },
    line: { color: C.teal, transparency: 100 },
  });
  slide.addText(kicker, {
    x: 0.72,
    y: 0.44,
    w: 1.78,
    h: 0.16,
    fontSize: 8.8,
    bold: true,
    color: C.white,
    margin: 0,
    charSpacing: 0.6,
  });
  slide.addText(title, {
    x: 0.55,
    y: 0.95,
    w: 8.2,
    h: 0.58,
    fontSize: 26,
    bold: true,
    color: C.dark,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.58,
      y: 1.55,
      w: 7.8,
      h: 0.5,
      fontSize: 11.5,
      color: C.muted,
      margin: 0,
    });
  }
  addTopMotif(slide, false);
}

function addCard(slide, x, y, w, h, opts) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: opts.bg || C.white },
    line: { color: opts.line || C.line, width: 1 },
    shadow: { type: 'outer', color: '000000', blur: 1, offset: 1, angle: 45, opacity: 0.08 },
  });
  if (opts.accent) {
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 0.09,
      h,
      fill: { color: opts.accent },
      line: { color: opts.accent, transparency: 100 },
    });
  }
  if (opts.label) {
    slide.addText(opts.label, {
      x: x + 0.22,
      y: y + 0.18,
      w: w - 0.35,
      h: 0.18,
      fontSize: 10,
      bold: true,
      color: opts.labelColor || opts.accent || C.teal,
      margin: 0,
    });
  }
  if (opts.title) {
    slide.addText(opts.title, {
      x: x + 0.22,
      y: y + (opts.label ? 0.42 : 0.2),
      w: w - 0.35,
      h: 0.45,
      fontSize: opts.titleSize || 18,
      bold: true,
      color: opts.titleColor || C.dark,
      margin: 0,
    });
  }
  if (opts.body) {
    slide.addText(opts.body, {
      x: x + 0.22,
      y: y + (opts.label ? 0.92 : 0.72),
      w: w - 0.35,
      h: h - (opts.label ? 1.05 : 0.92),
      fontSize: opts.bodySize || 11.5,
      color: opts.bodyColor || C.slate,
      margin: 0,
      breakLine: false,
      valign: 'top',
    });
  }
}

function addStep(slide, x, y, w, h, num, title, body, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: x + 0.18,
    y: y + 0.18,
    w: 0.42,
    h: 0.42,
    fill: { color },
    line: { color, transparency: 100 },
  });
  slide.addText(String(num), {
    x: x + 0.18,
    y: y + 0.255,
    w: 0.42,
    h: 0.14,
    align: 'center',
    fontSize: 10,
    bold: true,
    color: C.white,
    margin: 0,
  });
  slide.addText(title, {
    x: x + 0.72,
    y: y + 0.17,
    w: w - 0.9,
    h: 0.22,
    fontSize: 12,
    bold: true,
    color: C.dark,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.72,
    y: y + 0.48,
    w: w - 0.9,
    h: h - 0.65,
    fontSize: 10.5,
    color: C.slate,
    margin: 0,
  });
}

function addArrow(slide, x, y, w, color) {
  slide.addShape(pptx.ShapeType.chevron, {
    x,
    y,
    w,
    h: 0.28,
    fill: { color },
    line: { color, transparency: 100 },
  });
}

function addDarkCoverDecor(slide) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 7.65,
    y: 0,
    w: 2.35,
    h: 5.625,
    fill: { color: C.teal },
    line: { color: C.teal, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 7.25,
    y: 0,
    w: 0.45,
    h: 5.625,
    fill: { color: C.mint, transparency: 12 },
    line: { color: C.mint, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 7.95,
    y: 0.72,
    w: 1.2,
    h: 1.2,
    fill: { color: C.white, transparency: 90 },
    line: { color: C.white, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 8.55,
    y: 2.1,
    w: 0.72,
    h: 0.72,
    fill: { color: C.amber },
    line: { color: C.amber, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 7.7,
    y: 3.45,
    w: 1.55,
    h: 1.55,
    fill: { color: C.white, transparency: 82 },
    line: { color: C.white, transparency: 100 },
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  fullBg(slide, C.dark);
  addDarkCoverDecor(slide);
  slide.addText('MES 项目基座与 AI 协作开发介绍', {
    x: 0.72,
    y: 1.08,
    w: 6.1,
    h: 0.95,
    fontSize: 24,
    bold: true,
    color: C.white,
    margin: 0,
  });
  slide.addText('面向继续接手本项目的同事：先看懂这套项目现在有什么、还能怎么扩、怎么和 AI 一起做。', {
    x: 0.74,
    y: 2.02,
    w: 5.85,
    h: 0.48,
    fontSize: 12.5,
    color: 'D8E6FF',
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.74,
    y: 2.72,
    w: 1.55,
    h: 0.34,
    rectRadius: 0.06,
    fill: { color: C.mint },
    line: { color: C.mint, transparency: 100 },
  });
  slide.addText('Base + AI', {
    x: 0.9,
    y: 2.8,
    w: 1.15,
    h: 0.12,
    fontSize: 10,
    bold: true,
    color: C.dark,
    margin: 0,
  });
  addCard(slide, 0.75, 3.45, 1.85, 1.15, {
    accent: C.mint,
    label: 'MODULE',
    title: 'system',
    titleColor: C.white,
    body: '平台底座与系统管理',
    bodyColor: 'DCE8FF',
    bg: '27357A',
    line: '27357A',
  });
  addCard(slide, 2.78, 3.45, 1.85, 1.15, {
    accent: C.amber,
    label: 'MODULE',
    title: 'sales',
    titleColor: C.white,
    body: '销售示范业务域',
    bodyColor: 'DAE7FF',
    bg: '27357A',
    line: '27357A',
  });
  addCard(slide, 4.81, 3.45, 1.85, 1.15, {
    accent: C.teal,
    label: 'MODULE',
    title: 'production',
    titleColor: C.white,
    body: '生产执行示范业务域',
    bodyColor: 'DCE8FF',
    bg: '27357A',
    line: '27357A',
  });
  slide.addText('适用对象：需要理解项目、借助 AI 持续开发与扩展本仓库的同事', {
    x: 0.78,
    y: 5.05,
    w: 5.4,
    h: 0.18,
    fontSize: 9.5,
    color: 'BDD0FF',
    margin: 0,
  });
  addFooter(slide, 1, false);
}

// Slide 2
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(
    slide,
    'PROJECT STAGE',
    '项目目标与当前阶段',
    '先别急着看代码。先知道这套项目是干嘛的、已经做到哪、哪些还没做。',
  );
  addCard(slide, 0.68, 2.02, 8.34, 1.14, {
    accent: C.teal,
    label: 'GOAL',
    title: '这套基座要解决什么',
    titleSize: 18,
    body: '先把登录、菜单、权限、增删改查和验证流程这些常用底子搭好，后面做新模块时就不用每次重来。',
    bodySize: 11.5,
  });
  addCard(slide, 0.68, 3.55, 2.6, 1.58, {
    accent: C.amber,
    label: 'STAGE',
    title: '现在做到哪一步',
    titleSize: 17,
    body: '基座已经搭好了。\n销售和生产两条示例链也能跑。\n现在重点是继续扩功能。',
    bodySize: 10.8,
  });
  addCard(slide, 3.55, 3.55, 2.6, 1.58, {
    accent: C.mint,
    label: 'LIVE NOW',
    title: '现在已经能用的部分',
    titleSize: 17,
    body: 'system / sales / production\n这三块已经接进前后端、菜单和权限。',
    bodySize: 10.8,
  });
  addCard(slide, 6.42, 3.55, 2.6, 1.58, {
    accent: C.teal,
    label: 'NOT YET',
    title: '现在还别误会的部分',
    titleSize: 17,
    body: 'task / planning / process / quality 还没正式启用。\n现在不是“全部做完”，而是“能继续扩”。',
    bodySize: 10.4,
  });
  addFooter(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'TECH STACK', '这套项目现在用什么技术栈', '先知道前端、后端、验证各自用什么，后面看代码时才不容易发懵。');
  addCard(slide, 0.72, 2.02, 4.0, 1.32, {
    accent: C.teal,
    label: 'FRONTEND STACK',
    title: '前端这一侧',
    titleSize: 17,
    body: 'Vue 3 + TypeScript + Vite\nPinia + Vue Router\nElement Plus + Axios',
    bodySize: 11.1,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.32, {
    accent: C.amber,
    label: 'BACKEND STACK',
    title: '后端这一侧',
    titleSize: 17,
    body: 'FastAPI + PostgreSQL\n登录权限、JWT 和演示数据\nrouter / service / repository 分层',
    bodySize: 10.8,
  });
  addCard(slide, 0.72, 3.62, 4.0, 1.24, {
    accent: C.mint,
    label: 'DEV FLOW',
    title: '开发和生成',
    titleSize: 17,
    body: '前端 / 后端 / 全栈三类脚手架\n用来先把模块骨架起出来。',
    bodySize: 10.7,
  });
  addCard(slide, 5.02, 3.62, 4.0, 1.24, {
    accent: C.teal,
    label: 'VERIFY FLOW',
    title: '验证和交付',
    titleSize: 17,
    body: 'Python 语法、单测、type-check、构建、baseline\n用来统一验收，不靠感觉说“做完了”。',
    bodySize: 10.4,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.0,
    y: 5.04,
    w: 8.0,
    h: 0.28,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('一句话：前端做页面，后端管权限和数据，脚手架起步，baseline 验收。', {
    x: 1.24,
    y: 5.12,
    w: 7.5,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BASELINE CAPABILITIES', '项目基座已经提供了什么', '换句话说：很多底层活已经有人替你搭好了。');
  addCard(slide, 0.65, 2.06, 2.65, 1.18, {
    accent: C.teal,
    label: 'CAPABILITY 01',
    title: '统一布局',
    titleSize: 15,
    body: '页面框架、导航和移动端抽屉都已经有。',
  });
  addCard(slide, 3.48, 2.06, 2.65, 1.18, {
    accent: C.amber,
    label: 'CAPABILITY 02',
    title: '登录与权限',
    titleSize: 15,
    body: '登录、角色、菜单权限和页面拦截都已经接好。',
  });
  addCard(slide, 6.31, 2.06, 2.65, 1.18, {
    accent: C.mint,
    label: 'CAPABILITY 03',
    title: '本地后端',
    titleSize: 15,
    body: '本地就能跑 FastAPI + PostgreSQL，不用先找远程环境。',
  });
  addCard(slide, 0.65, 3.62, 2.65, 1.35, {
    accent: C.teal,
    label: 'CAPABILITY 04',
    title: 'CRUD 样板',
    titleSize: 15,
    body: '列表、搜索、分页、弹窗表单这些常见写法可以直接复用。',
  });
  addCard(slide, 3.47, 3.62, 2.65, 1.35, {
    accent: C.amber,
    label: 'CAPABILITY 05',
    title: '脚手架与 registry',
    titleSize: 15,
    body: '新模块有标准生成入口，不用复制旧代码硬拼。',
  });
  addCard(slide, 6.29, 3.62, 2.65, 1.35, {
    accent: C.mint,
    label: 'CAPABILITY 06',
    title: 'Baseline 验证',
    titleSize: 15,
    body: '改完可以统一检查，减少把基座改坏的风险。',
  });
  addFooter(slide, 4);
}

// Slide 5
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'CURRENT STATE', '这个仓库现在到底是什么', '这页专门纠正旧印象：不要再把它当成“老示例仓库”。');
  addCard(slide, 0.72, 2.02, 3.95, 2.28, {
    accent: C.amber,
    label: 'OLD IMPRESSION',
    title: '最容易带错的旧印象',
    titleSize: 18,
    body: '它只是老的系统管理示例仓库。\n菜单能看到，不代表业务真的跑得起来。\n新功能主要靠复制旧代码去拼。',
    bodySize: 11.2,
  });
  addCard(slide, 5.0, 2.02, 4.02, 2.28, {
    accent: C.teal,
    label: 'REAL POSITION',
    title: '现在更接近的真实定位',
    titleSize: 18,
    body: '它已经是一套可继续扩展的业务系统基座。\nsystem / sales / production 已经接进前后端、菜单和权限。\n新增功能默认应该走脚手架、注册点和 baseline。',
    bodySize: 11.0,
  });
  ['system', 'sales', 'production'].forEach((name, idx) => {
    const x = 1.28 + idx * 2.46;
    const accent = idx === 1 ? C.amber : idx === 2 ? C.mint : C.teal;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 4.5,
      w: 1.95,
      h: 0.42,
      rectRadius: 0.07,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.16,
      y: 4.6,
      w: 0.18,
      h: 0.18,
      fill: { color: accent },
      line: { color: accent, transparency: 100 },
    });
    slide.addText(name, {
      x: x + 0.42,
      y: 4.59,
      w: 1.28,
      h: 0.12,
      fontSize: 11,
      bold: true,
      color: C.dark,
      margin: 0,
      fontFace: 'Consolas',
      align: 'center',
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.05,
    y: 4.98,
    w: 7.9,
    h: 0.46,
    rectRadius: 0.06,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('结论：要以当前代码和启用配置为准，不要再以旧印象来理解这个仓库。', {
    x: 1.35,
    y: 5.14,
    w: 7.3,
    h: 0.18,
    fontSize: 11,
    color: C.dark,
    margin: 0,
    align: 'center',
  });
  addFooter(slide, 5);
}

// Slide 6
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SYSTEM MAP', '系统地图：前端、后端、验证各管什么', '只记一句话：页面在前端，权限和数据在后端，验证负责兜底。');
  addCard(slide, 0.72, 2.04, 2.62, 2.15, {
    accent: C.teal,
    label: 'FRONTEND',
    title: '前端负责你看到和点到的东西',
    titleSize: 17,
    body: '• 页面、表格、表单\n• 页面跳转和菜单显示\n• 登录后的页面状态\n• 这个页面前端这边让不让进',
    bodySize: 11.5,
  });
  addCard(slide, 3.67, 2.04, 2.62, 2.15, {
    accent: C.amber,
    label: 'BACKEND',
    title: '后端负责系统认不认、给不给数据',
    titleSize: 17,
    body: '• 菜单树和权限码\n• 角色到底能看哪些菜单\n• 业务接口和模块路由\n• 初始化演示数据',
    bodySize: 11.5,
  });
  addCard(slide, 6.62, 2.04, 2.62, 2.15, {
    accent: C.mint,
    label: 'VERIFY',
    title: '验证负责最后兜底',
    titleSize: 17,
    body: '• Python 能不能正常跑\n• 后端公共能力有没有被改坏\n• 接口能不能正常通\n• 前端类型和构建能不能过',
    bodySize: 11.5,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.4,
    y: 4.55,
    w: 7.2,
    h: 0.46,
    rectRadius: 0.05,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('一个功能打不开，常见不是页面写错，而是前后端和权限这条线没有对上。', {
    x: 1.7,
    y: 4.64,
    w: 6.6,
    h: 0.22,
    fontSize: 10.2,
    bold: true,
    color: C.white,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 6);
}

// Slide 7
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BASE LAYERS', '这个基座其实分成 5 层', '后面新模块能接得快，不是因为 AI 会“魔法生成”，而是这些公共层已经先搭好了。');
  const layerRows = [
    ['LAYER 01', '页面壳和导航', '统一布局、侧边菜单、顶部栏、移动端容器。新页面不用从头搭外框。', C.teal],
    ['LAYER 02', '登录和权限', '登录态、角色、菜单权限、页面拦截。很多“能不能进页面”的判断已经在基座里。', C.amber],
    ['LAYER 03', '前端公共能力', 'request、store、通用表格表单、CRUD 写法。做页面时通常只补业务字段和交互。', C.mint],
    ['LAYER 04', '后端公共能力', '应用启动、数据库、菜单树、seed、router / service / repository 这些骨架已经在。', C.teal],
    ['LAYER 05', '生成和验证', 'scaffold、registry、baseline。新模块按固定入口生成，改完按固定方式验。', C.amber],
  ];
  layerRows.forEach(([label, title, body, accent], idx) => {
    const y = 1.98 + idx * 0.67;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.92,
      y,
      w: 8.05,
      h: 0.55,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: 0.92,
      y,
      w: 0.12,
      h: 0.55,
      fill: { color: accent },
      line: { color: accent, transparency: 100 },
    });
    slide.addText(label, {
      x: 1.2,
      y: y + 0.11,
      w: 0.85,
      h: 0.1,
      fontSize: 9.5,
      bold: true,
      color: accent,
      margin: 0,
    });
    slide.addText(title, {
      x: 2.0,
      y: y + 0.1,
      w: 1.95,
      h: 0.14,
      fontSize: 13,
      bold: true,
      color: C.dark,
      margin: 0,
      fit: 'shrink',
    });
    slide.addText(body, {
      x: 4.0,
      y: y + 0.1,
      w: 4.55,
      h: 0.18,
      fontSize: 9.8,
      color: C.slate,
      margin: 0,
      fit: 'shrink',
    });
  });
  addFooter(slide, 7);
}

// Slide 8
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'FRONTEND BASE', '前端基座已经替你做好哪些事', '如果你主要做前端，很多常用能力已经在，不是从空白页面开始。');
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'FRONTEND 01',
    title: '路由和页面拦截',
    titleSize: 17,
    body: '页面入口、默认跳转、未授权拦截、已启用模块过滤，这些规则都已经有。',
    bodySize: 11.2,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'FRONTEND 02',
    title: '菜单和布局容器',
    titleSize: 17,
    body: '主布局、侧栏、顶部区域、移动端抽屉，以及后端菜单回退机制都已经有。',
    bodySize: 11.0,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'FRONTEND 03',
    title: '统一请求和状态',
    titleSize: 17,
    body: 'request 封装、token 注入、错误处理、userStore、menuStore 这些公共逻辑不用重写。',
    bodySize: 10.9,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'FRONTEND 04',
    title: '通用页面写法',
    titleSize: 17,
    body: '列表、搜索、分页、弹窗表单、类型定义、store 模式都有现成参考。',
    bodySize: 11.1,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.05,
    y: 4.9,
    w: 7.9,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('大多数前端新增页，不是从零做页面，而是在这套公共写法上把业务字段和交互补完整。', {
    x: 1.3,
    y: 5.01,
    w: 7.4,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 8);
}

// Slide 9
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BACKEND BASE', '后端基座已经替你做好哪些事', '如果你主要做后端，也不是从空白 FastAPI 项目开始。');
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'BACKEND 01',
    title: '启动和安全基础',
    titleSize: 17,
    body: 'main.py、JWT、密码哈希、CORS、环境加载这些启动级能力已经有。',
    bodySize: 11.2,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'BACKEND 02',
    title: '菜单和权限权威源',
    titleSize: 17,
    body: '菜单树、角色菜单、permission 语义已经集中在后端，不需要每次重新发明一套。',
    bodySize: 10.9,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'BACKEND 03',
    title: '数据初始化和演示数据',
    titleSize: 17,
    body: 'init_db、schema、seed、默认演示账号都已经在，方便本地联调和培训演示。',
    bodySize: 10.9,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'BACKEND 04',
    title: '模块化后端结构',
    titleSize: 17,
    body: 'modules 目录、router / deps / service / repository 这一套分层结构已经定好。',
    bodySize: 11.0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.02,
    y: 4.9,
    w: 7.95,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('大多数后端新增模块，重点不是重搭框架，而是在这套结构里补业务表、接口和服务逻辑。', {
    x: 1.28,
    y: 5.01,
    w: 7.42,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 9);
}

// Slide 10
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BASE RULES', '这套基座里，哪些规则已经固定下来了', '这些不是“建议”，而是后面继续开发时默认要遵守的公共约定。');
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'RED LINE 01',
    title: 'ID 和成功码别乱',
    titleSize: 17,
    body: 'ID 默认用 string；接口成功按 code = 0 或 200 处理。本地库统一走 PostgreSQL，否则前后端一对接就容易出怪问题。',
    bodySize: 10.9,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'RED LINE 02',
    title: '权限四件套要一起改',
    titleSize: 17,
    body: 'route、menu、layout、permission 要一起改；前端 functionCode 要和后端 permission 对齐，少一处就可能“菜单有了但进不去”。',
    bodySize: 10.8,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'RED LINE 03',
    title: '启用边界看 frameworkConfig',
    titleSize: 17,
    body: '哪些业务域现在能用，以 frameworkConfig.ts 为准；没启用的前缀不要直接当正式入口用。',
    bodySize: 10.8,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'RED LINE 04',
    title: '新增模块先 scaffold，再跑 baseline',
    titleSize: 17,
    body: 'seed 放 init_db；共享改动要跑 baseline；新增模块优先 scaffold，不要手工复制老模块。',
    bodySize: 10.8,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.05,
    y: 4.9,
    w: 7.9,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('新功能能不能用，常常不是代码没写完，而是这四处没有一起改。', {
    x: 1.3,
    y: 5.01,
    w: 7.4,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 10);
}

// Slide 11
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'KEY FILES', '新同事先认识哪些目录和关键文件', '第一次接手别从头翻完整个仓库，先看这 6 处最值钱。');
  const fileCards = [
    [0.72, 2.0, 2.62, 1.18, 'RULES', 'AGENTS.md', '先知道项目规则和默认做法。', C.teal, 'Consolas'],
    [3.67, 2.0, 2.62, 1.18, 'BOUNDARY', 'frameworkConfig.ts', '先知道哪些业务域当前启用。', C.amber, 'Consolas'],
    [6.62, 2.0, 2.62, 1.18, 'AUTHORITY', 'menu.py', '先看后端菜单和权限从哪来。', C.mint, 'Consolas'],
    [0.72, 3.5, 2.62, 1.18, 'ENTRY', 'router + MainLayout', '页面入口、跳转和拦截从这里查。', C.teal, 'Microsoft YaHei'],
    [3.67, 3.5, 2.62, 1.18, 'WORKFLOW', 'scaffold + verify', '新增模块和交付验收从这里走。', C.amber, 'Consolas'],
    [6.62, 3.5, 2.62, 1.18, 'DOCS', 'training docs', '看培训材料、AI 协作说明和提示词模板。', C.mint, 'Consolas'],
  ];
  fileCards.forEach(([x, y, w, h, label, title, body, accent, face]) => {
    addCard(slide, x, y, w, h, {
      accent,
      label,
      body,
      bodySize: 10.8,
    });
    if (face) {
      slide.addText(title, {
        x: x + 0.22,
        y: y + 0.42,
        w: w - 0.35,
        h: 0.28,
        fontSize: 16.2,
        bold: true,
        color: C.dark,
        margin: 0,
        fontFace: face,
        fit: 'shrink',
      });
    }
  });
  addFooter(slide, 11);
}

// Slide 12
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'DOMAIN DEMO', '当前业务域在展示什么', '把这三块先认熟，你后面才知道新功能该往哪里挂。');
  addCard(slide, 0.72, 2.0, 2.58, 2.15, {
    accent: C.teal,
    label: 'SYSTEM',
    title: '平台底座',
    titleSize: 18,
    body: '账户、角色、参数、菜单、日志这些基础管理能力。\n\n你可以把它理解成“平台底子”。',
    bodySize: 11.5,
  });
  addCard(slide, 3.65, 2.0, 2.58, 2.15, {
    accent: C.amber,
    label: 'SALES',
    title: '销售示例域',
    titleSize: 18,
    body: '产品 -> 报价 -> 合同 -> 回款 -> 佣金。\n\n它是在演示：这套基座能接一条完整业务链。',
    bodySize: 11.5,
  });
  addCard(slide, 6.58, 2.0, 2.58, 2.15, {
    accent: C.mint,
    label: 'PRODUCTION',
    title: '生产示例域',
    titleSize: 18,
    body: '工单 -> 报工 -> 入库 -> 看板。\n\n它是在演示：另一条业务线也能共用同一套底座。',
    bodySize: 11.5,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.95,
    y: 4.48,
    w: 8.0,
    h: 0.46,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('这三块不是为了展示页面好看，而是在告诉你：同一套底座可以继续接更多模块。', {
    x: 1.18,
    y: 4.63,
    w: 7.55,
    h: 0.16,
    fontSize: 11,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 12);
}

// Slide 13
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'DAILY ENTRY', '接手后的日常开发入口', '先把现有系统跑通，再谈继续开发。这样最不容易把环境问题当成代码问题。');
  addStep(slide, 0.72, 2.05, 4.0, 1.1, 1, '准备环境', '安装前端依赖、后端虚拟环境与 PostgreSQL 本地库。', C.teal);
  addStep(slide, 5.02, 2.05, 4.0, 1.1, 2, '启动服务', 'npm run dev / npm run backend:dev', C.amber);
  addStep(slide, 0.72, 3.45, 4.0, 1.1, 3, '走通样例链', '用 admin 登录，至少点通一条 sales 或 production 链路。', C.mint);
  addStep(slide, 5.02, 3.45, 4.0, 1.1, 4, '执行验证', '统一执行：bash scripts/verify_framework_baseline.sh', C.teal);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.0,
    y: 4.78,
    w: 8.0,
    h: 0.58,
    rectRadius: 0.08,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText('建议默认顺序', {
    x: 1.28,
    y: 4.97,
    w: 1.1,
    h: 0.14,
    fontSize: 10.5,
    bold: true,
    color: C.teal,
    margin: 0,
  });
  slide.addText('先确认“系统能跑”，再确认“现成流程能走”，最后再让 AI 接手具体任务。这样不容易把环境问题误判成代码 bug。', {
    x: 2.42,
    y: 4.97,
    w: 6.25,
    h: 0.14,
    fontSize: 10.5,
    color: C.slate,
    margin: 0,
  });
  addFooter(slide, 13);
}

// Slide 14
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'EXPANSION MODES', '用这个基座继续开发，常见就是 4 类事情', '你后面遇到的事，大多都能归到这 4 类。先分对类，AI 才好接手。');
  addCard(slide, 0.72, 2.0, 4.0, 1.18, {
    accent: C.teal,
    label: 'MODE 01',
    title: '新增完整业务模块',
    titleSize: 17,
    body: '前后端都要加。标准做法是先走 fullstack scaffold。',
    bodySize: 11.5,
  });
  addCard(slide, 5.02, 2.0, 4.0, 1.18, {
    accent: C.amber,
    label: 'MODE 02',
    title: '给现有模块补页面',
    titleSize: 17,
    body: '接口已经有了，只补列表、表单、详情或交互。',
    bodySize: 11.5,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'MODE 03',
    title: '给现有模块补后端能力',
    titleSize: 17,
    body: '页面已经有了，只补接口、权限、演示数据或后端结构。',
    bodySize: 11.5,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'MODE 04',
    title: '修联动问题或做重构',
    titleSize: 17,
    body: '重点不是某个页面，而是 route、menu、permission、registry、baseline 这一串。',
    bodySize: 11.5,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.2,
    y: 4.9,
    w: 7.55,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('记忆方式：整块新增先走脚手架，局部补强和排错就在现有结构上改。', {
    x: 1.48,
    y: 5.01,
    w: 7.0,
    h: 0.12,
    fontSize: 10.8,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 14);
}

// Slide 15
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'EXPANSION PATH', '标准扩展路径：从需求到交付', '别急着开写。先把要挂哪里、怎么接进去、最后怎么验清楚。');
  addStep(slide, 0.7, 2.02, 2.55, 0.92, 1, '先定挂到哪', '先判断放到 system、sales 还是 production。', C.teal);
  addStep(slide, 3.48, 2.02, 2.55, 0.92, 2, '再选怎么做', '决定用 fullstack、frontend、backend，还是在旧模块上改。', C.amber);
  addStep(slide, 6.26, 2.02, 2.55, 0.92, 3, '先把骨架搭出来', '先把目录、页面、接口和基础接线点生出来。', C.mint);
  addStep(slide, 1.62, 3.4, 2.75, 0.92, 4, '把该接的都接上', '把 route、menu、permission、registry、seed、授权接齐。', C.teal);
  addStep(slide, 4.62, 3.4, 2.75, 0.92, 5, '再补真实业务', '把字段、SQL、文案和真实逻辑换成正式内容。', C.amber);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.85,
    y: 4.75,
    w: 6.35,
    h: 0.44,
    rectRadius: 0.05,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('最后要能说清三件事：你改了什么、测了什么、还剩什么风险。', {
    x: 2.12,
    y: 4.86,
    w: 5.8,
    h: 0.18,
    fontSize: 10.2,
    bold: true,
    color: C.white,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 15);
}

// Slide 16
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(
    slide,
    'REAL EXAMPLE',
    '真实扩展示例：新增一个质检报告模块',
    '拿一个最像真实工作的例子，把整条扩展路径讲明白。',
  );
  addStep(slide, 0.62, 2.05, 2.6, 0.92, 1, '先决定放哪块', '虽然叫质检，但现在先挂 production，不另开 quality 一级模块。', C.teal);
  addStep(slide, 3.35, 2.05, 2.6, 0.92, 2, '选择 fullstack scaffold', '因为页面、接口、菜单、权限都要一起补。', C.amber);
  addStep(slide, 6.08, 2.05, 2.6, 0.92, 3, '把参数先定清', '模块名、挂载位置、路由、功能码和权限码这些先定好。', C.mint);
  addStep(slide, 0.62, 3.35, 2.6, 0.92, 4, '先出骨架', '先生成 view、api、type、store 和后端模块目录。', C.teal);
  addStep(slide, 3.35, 3.35, 2.6, 0.92, 5, '补齐接线', '把 route、menu、permission、registry，再把 seed 和授权补上。', C.amber);
  addStep(slide, 6.08, 3.35, 2.6, 0.92, 6, '换成真实业务再验', '把占位字段和 SQL 换掉，再跑 baseline。', C.mint);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 4.45,
    w: 8.55,
    h: 0.78,
    rectRadius: 0.06,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('AI 必填 5 项', {
    x: 0.98,
    y: 4.58,
    w: 1.0,
    h: 0.14,
    fontSize: 10.5,
    bold: true,
    color: C.teal,
    margin: 0,
  });
  const promptFields = [
    ['模块名', 'quality_report'],
    ['业务域', 'production'],
    ['路由', '/production/quality-report'],
    ['功能码', 'production-quality-report'],
    ['权限码', 'SRS-FUNC-QUALITY-REPORT'],
  ];
  promptFields.forEach(([label, value], idx) => {
    const x = 2.18 + idx * 1.38;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 4.54,
      w: 1.28,
      h: 0.5,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addText(label, {
      x: x + 0.12,
      y: 4.62,
      w: 1.04,
      h: 0.1,
      fontSize: 8.2,
      bold: true,
      color: C.muted,
      margin: 0,
      align: 'center',
    });
    slide.addText(value, {
      x: x + 0.08,
      y: 4.78,
      w: 1.12,
      h: 0.12,
      fontSize: idx >= 3 ? 7.3 : 7.7,
      bold: true,
      color: C.dark,
      margin: 0,
      align: 'center',
      fontFace: 'Consolas',
      fit: 'shrink',
    });
  });
  addFooter(slide, 16);
}

// Slide 17
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'LINKAGE CHAIN', '新功能接入，不是只改一个页面', '一个功能真能用，通常不止改一个页面，而是下面这一串要一起动。');
  addCard(slide, 0.72, 2.08, 2.45, 2.0, {
    accent: C.teal,
    label: 'FRONTEND',
    title: '前端接入 4 项',
    titleSize: 18,
    body: '页面\n路由\n菜单\n布局过滤',
    bodySize: 12,
  });
  addCard(slide, 3.77, 2.08, 2.15, 2.0, {
    accent: C.amber,
    label: 'PERMISSION',
    title: '权限接入 3 项',
    titleSize: 18,
    body: '功能码\n权限码\n菜单授权',
    bodySize: 12,
  });
  addCard(slide, 6.52, 2.08, 2.52, 2.0, {
    accent: C.mint,
    label: 'VERIFY',
    title: '收口验证 2 项',
    titleSize: 18,
    body: 'baseline\n关键流程回归\n\nbaseline 就是共享基座的统一验收。',
    bodySize: 11.4,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.3,
    y: 4.52,
    w: 7.35,
    h: 0.38,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('一个页面能打开，不代表这个功能已经真正接进系统。', {
    x: 1.62,
    y: 4.64,
    w: 6.7,
    h: 0.14,
    fontSize: 11,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 17);
}

// Slide 18
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'AI ROLE', 'AI 在这个项目里应该扮演什么角色', '在这个项目里，AI 更像能干活的工程搭子，不是自己拍板的产品经理。');
  addCard(slide, 0.65, 2.0, 4.0, 2.55, {
    accent: C.teal,
    label: '适合 AI',
    title: '适合 AI 去做',
    titleSize: 22,
    body: '• 先把当前仓库看明白\n• 跑脚手架、补接线\n• 排查路由、菜单、权限这类联动问题\n• 帮你汇总改动和验证结果',
    bodySize: 12,
  });
  addCard(slide, 5.0, 2.0, 4.0, 2.55, {
    accent: C.amber,
    label: '不适合 AI',
    title: '不要让 AI 这么做',
    titleSize: 22,
    body: '• 不看规则和现状就直接改\n• 绕开脚手架，直接往主文件里堆\n• 不跑 baseline 就说做完了\n• 把占位字段当成正式业务定义',
    bodySize: 12,
  });
  addFooter(slide, 18);
}

// Slide 19
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'AUTHORITY MODEL', '谁说了算：AI 直接做、先确认、人工拍板', '判断标准很简单：有现成规则的让 AI 做，没有唯一答案的先确认，会改业务含义的必须人定。');
  const drawDecision = (y, color, label, title, body) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.72,
      y,
      w: 8.3,
      h: 0.88,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: 0.72,
      y,
      w: 0.1,
      h: 0.88,
      fill: { color },
      line: { color, transparency: 100 },
    });
    slide.addText(label, {
      x: 0.95,
      y: y + 0.12,
      w: 0.8,
      h: 0.12,
      fontSize: 10,
      bold: true,
      color,
      margin: 0,
    });
    slide.addText(title, {
      x: 0.95,
      y: y + 0.34,
      w: 3.0,
      h: 0.2,
      fontSize: 18,
      bold: true,
      color: C.dark,
      margin: 0,
    });
    slide.addText(body, {
      x: 4.15,
      y: y + 0.37,
      w: 4.45,
      h: 0.18,
      fontSize: 10.5,
      color: C.slate,
      margin: 0,
    });
  };
  drawDecision(2.1, C.teal, '第一层', '规则已经很明确', '像脚手架、接 registry、对齐 permission、跑 baseline，这些直接让 AI 做。');
  drawDecision(3.18, C.amber, '第二层', '大方向对，但有几种选法', '比如挂 sales 还是 production、菜单怎么叫、字段要不要收缩，先让 AI 给建议。');
  drawDecision(4.26, C.mint, '第三层', '会改业务意思或系统边界', '比如真实字段、表结构、一级模块、登录和权限主干，这种必须人拍板。');
  addFooter(slide, 19);
}

// Slide 20
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'AI STARTUP', '同事第一次让 AI 接手时，该怎么做', '别一上来就说“帮我改”。先把项目规则和当前现状给 AI。');
  addStep(slide, 0.62, 2.15, 2.6, 1.15, 1, '先读规则', 'AGENTS、CLAUDE、training、对应 skill。先让 AI 知道这套项目按什么规矩干活。', C.teal);
  addStep(slide, 3.7, 2.15, 2.6, 1.15, 2, '再读入口', 'frameworkConfig、router、MainLayout、menu.py。先给 AI 一张系统地图。', C.amber);
  addStep(slide, 6.78, 2.15, 2.6, 1.15, 3, '最后再给任务', '说清要改什么、不要改什么、挂到哪里、做完怎么验。', C.mint);
  addArrow(slide, 3.28, 2.6, 0.3, C.teal);
  addArrow(slide, 6.36, 2.6, 0.3, C.amber);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.45,
    y: 3.95,
    w: 7.1,
    h: 0.82,
    rectRadius: 0.08,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('一句话：先给 AI 地图，再给 AI 任务。这样结果会准很多。', {
    x: 1.75,
    y: 4.23,
    w: 6.5,
    h: 0.18,
    fontSize: 12,
    bold: true,
    color: C.dark,
    margin: 0,
    align: 'center',
  });
  addFooter(slide, 20);
}

// Slide 21
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SKILL BASICS', '先认识 Skill：它到底是什么', '这个词别想复杂。你就把它当成 AI 的固定工作办法。');
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'WHAT IT IS',
    title: '你可以把它理解成',
    titleSize: 17,
    body: '一份固定的工作说明书：先读什么、按什么顺序做、哪些步骤不能跳过。',
    bodySize: 11.5,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'WHY IT HELPS',
    title: '它帮你省掉什么',
    titleSize: 17,
    body: '不用每次都从头给 AI 讲规矩。不同同事接手时，也能让 AI 按同一套方法做事。',
    bodySize: 11.2,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'WHAT IT CONTAINS',
    title: '里面一般会写什么',
    titleSize: 17,
    body: '什么时候用、先看哪些文件、推荐步骤、默认验证、常见坑位和不能跳过的护栏。',
    bodySize: 11.2,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'WHAT IT IS NOT',
    title: 'Skill 不是魔法插件',
    titleSize: 17,
    body: '它不会代替人来决定真实业务语义，也不会跳过项目现有的脚手架、权限和验证规则。',
    bodySize: 11.0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.15,
    y: 4.88,
    w: 7.7,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('一句话记住：skill 的价值，不是让 AI 更会聊天，而是先让它按对的方法干活。', {
    x: 1.42,
    y: 4.99,
    w: 7.15,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 21);
}

// Slide 22
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'PROJECT SKILL', '这个项目专用的 Skill', '这不是给 AI 加一个新名词，而是让它按这套基座的工法做事。');
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 1.86,
    w: 3.38,
    h: 0.34,
    rectRadius: 0.06,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('universal-fullstack-framework', {
    x: 0.95,
    y: 1.95,
    w: 2.92,
    h: 0.12,
    fontFace: 'Consolas',
    fontSize: 10.2,
    bold: true,
    color: C.white,
    margin: 0,
    align: 'center',
  });
  addCard(slide, 0.72, 2.34, 2.6, 1.92, {
    accent: C.teal,
    label: 'WHEN TO USE',
    title: '什么时候用',
    titleSize: 18,
    body: '新增模块\n整理或重构基座\n排查前后端联动问题\n把 mock 或远程依赖换成本地实现\n共享链路回归加固',
    bodySize: 11.0,
  });
  addCard(slide, 3.7, 2.34, 2.6, 1.92, {
    accent: C.amber,
    label: 'DEFAULT METHOD',
    title: '它默认怎么干',
    titleSize: 18,
    body: '先保护公共基座别改乱\n先把路由、菜单、接口对齐\n优先用脚手架和注册点\n优先接本地 FastAPI + PostgreSQL',
    bodySize: 10.8,
  });
  addCard(slide, 6.68, 2.34, 2.6, 1.92, {
    accent: C.mint,
    label: 'DEFAULT GUARDRAILS',
    title: '它默认盯什么',
    titleSize: 18,
    body: 'functionCode 要对上 permission\nroute / menu / layout 要一起动\n新增模块先做最小可用\n共享改动优先跑 baseline',
    bodySize: 10.8,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.95,
    y: 4.62,
    w: 8.15,
    h: 0.42,
    rectRadius: 0.05,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('它不是替你决定业务，而是把“怎么沿着现有基座继续做”先写成 AI 必须遵守的流程。', {
    x: 1.25,
    y: 4.74,
    w: 7.55,
    h: 0.14,
    fontSize: 10.6,
    bold: true,
    color: C.white,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 22);
}

// Slide 23
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SKILL FLOW', '这个专属 Skill 用了以后，AI 会按什么顺序做', '它不是“给 AI 加一个名字”而已，而是会让 AI 默认按这条顺序推进。');
  addStep(slide, 0.68, 2.05, 2.62, 0.9, 1, '先保住基座', '先确认哪些是公共底座，尽量别为了新需求把主干改乱。', C.teal);
  addStep(slide, 3.4, 2.05, 2.62, 0.9, 2, '先对齐前后端合同', '先看 route、menu、API、字段、返回格式是不是一一对应。', C.amber);
  addStep(slide, 6.12, 2.05, 2.62, 0.9, 3, '优先接本地后端', '优先走 FastAPI + PostgreSQL + seed，而不是先靠 mock 顶着。', C.mint);
  addStep(slide, 2.0, 3.45, 2.9, 0.9, 4, '新增模块先用脚手架', '前后端都要改时优先 fullstack scaffold，其次再拆 frontend / backend。', C.teal);
  addStep(slide, 5.1, 3.45, 2.9, 0.9, 5, '最后统一验证', '共享改动优先跑 baseline，再看 smoke 和关键流程有没有通过。', C.amber);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.45,
    y: 4.82,
    w: 7.1,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('所以用了这个 skill 以后，AI 正常不会一上来复制旧模块，也不会跳过验证直接说“已完成”。', {
    x: 1.7,
    y: 4.93,
    w: 6.6,
    h: 0.12,
    fontSize: 10.5,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 23);
}

// Slide 24
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SKILL GUARDRAILS', '这个专属 Skill 会默认盯哪些风险和交付项', '它不只是告诉 AI 怎么做，还会默认盯住一批最容易出问题的地方。');
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'RISK 01',
    title: '联动风险',
    titleSize: 17,
    body: '新增或移动模块时，route、menu、permission、layout 这些要一起检查，少一个都可能出问题。',
    bodySize: 10.9,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'RISK 02',
    title: '数据和演示风险',
    titleSize: 17,
    body: 'seed 不是随便塞几条数据，而是要能支撑一整条业务链跑起来，别只在前端写假数据。',
    bodySize: 10.8,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'RISK 03',
    title: '环境和依赖风险',
    titleSize: 17,
    body: '像 python-multipart、端口占用、虚拟环境装错依赖，这些它都会当成默认检查点。',
    bodySize: 10.7,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'DELIVERY',
    title: '交付时要说清什么',
    titleSize: 17,
    body: '改了哪些文件、解决了什么问题、跑了哪些验证、结果如何、还剩哪些风险。',
    bodySize: 10.8,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.05,
    y: 4.9,
    w: 7.9,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('你可以把这页理解成：这个 skill 不只教 AI 怎么写代码，还会逼它别漏检查、别漏说明。', {
    x: 1.3,
    y: 5.01,
    w: 7.4,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 24);
}

// Slide 25
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'CORE MECHANISM', '这 4 个词分别干什么', '别把它们当术语背，直接记“各自解决什么问题”。');
  addCard(slide, 0.72, 2.05, 3.92, 1.18, {
    accent: C.teal,
    label: 'SKILL',
    title: '定做法',
    titleSize: 18,
    body: '告诉 AI 先看什么、先做什么、哪些步骤不能跳过。',
    bodySize: 11.3,
  });
  addCard(slide, 5.02, 2.05, 3.92, 1.18, {
    accent: C.amber,
    label: 'SCAFFOLD',
    title: '出骨架',
    titleSize: 18,
    body: '先生成目录、页面、接口和基础接线点，避免手工乱拼。',
    bodySize: 11.3,
  });
  addArrow(slide, 4.72, 2.46, 0.22, C.teal);
  addCard(slide, 0.72, 3.48, 3.92, 1.18, {
    accent: C.mint,
    label: 'REGISTRY',
    title: '接系统',
    titleSize: 18,
    body: '把新模块注册进路由、菜单和后端入口，让它真正出现在系统里。',
    bodySize: 11.0,
  });
  addCard(slide, 5.02, 3.48, 3.92, 1.18, {
    accent: C.teal,
    label: 'BASELINE',
    title: '做验收',
    titleSize: 18,
    body: '确认共享基座没有被这次改动带坏，交付前统一收口。',
    bodySize: 11.0,
  });
  addArrow(slide, 4.72, 3.89, 0.22, C.mint);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.85,
    y: 4.92,
    w: 6.3,
    h: 0.42,
    rectRadius: 0.05,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('一句话：先定做法，再出骨架，再接系统，最后验收。', {
    x: 2.18,
    y: 5.04,
    w: 5.62,
    h: 0.14,
    fontSize: 10.6,
    bold: true,
    color: C.white,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 25);
}

// Slide 26
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SKILL TRANSLATION', '把这份 Skill 翻成人话，可以怎么理解', '把工程说明书翻成同事更容易听懂的中文版本。');
  const translatedRows = [
    ['01', '先把基座稳住', '先保住认证、系统管理、权限、日志和一条基础 CRUD，不要一上来就把主干改乱。', C.teal],
    ['02', '先把前后端对齐', '先把前端 API 和后端接口一一对应，缺哪个补哪个，不要两边各猜各的。', C.amber],
    ['03', '优先走本地真实链路', 'remote / mock 能换就换，优先接本地 FastAPI + PostgreSQL + seed。', C.mint],
    ['04', '统一开发写法', '前端走统一 request / store / CRUD 模式，后端走模块化分层和注册机制。', C.teal],
    ['05', '小步扩展，小步验证', '每次先做一段最小可用，做完就验，再继续往下做。', C.amber],
  ];
  translatedRows.forEach(([num, title, body, accent], idx) => {
    const y = 2.0 + idx * 0.63;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.82,
      y,
      w: 8.18,
      h: 0.5,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.ellipse, {
      x: 1.0,
      y: y + 0.12,
      w: 0.24,
      h: 0.24,
      fill: { color: accent },
      line: { color: accent, transparency: 100 },
    });
    slide.addText(num, {
      x: 1.0,
      y: y + 0.2,
      w: 0.24,
      h: 0.08,
      fontSize: 8.8,
      bold: true,
      color: C.white,
      align: 'center',
      margin: 0,
    });
    slide.addText(title, {
      x: 1.42,
      y: y + 0.13,
      w: 1.95,
      h: 0.12,
      fontSize: 12.5,
      bold: true,
      color: C.dark,
      margin: 0,
    });
    slide.addText(body, {
      x: 3.42,
      y: y + 0.13,
      w: 5.2,
      h: 0.16,
      fontSize: 9.6,
      color: C.slate,
      margin: 0,
      fit: 'shrink',
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.15,
    y: 5.16,
    w: 7.7,
    h: 0.28,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('一句话：先把底子稳住，再把前后端对齐，然后沿着本地真实链路一点点往外扩。', {
    x: 1.4,
    y: 5.24,
    w: 7.2,
    h: 0.12,
    fontSize: 10.4,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 26);
}

// Slide 27
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SKILL SCRIPTS', '这个 Skill 会用到哪些主脚本', '前面三个负责起骨架，最后一个负责验基座。');
  addCard(slide, 0.72, 2.02, 4.0, 1.28, {
    accent: C.teal,
    label: 'FULLSTACK',
    title: 'scripts/scaffold_fullstack_module.py',
    titleSize: 14.5,
    body: '同时生成前后端模块骨架，是标准新增模块时的默认入口。',
    bodySize: 10.6,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.28, {
    accent: C.amber,
    label: 'BACKEND',
    title: 'backend/scripts/scaffold_backend_module.py',
    titleSize: 14.2,
    body: '只生成后端 module / router / service / repository，并写入后端路由注册表。',
    bodySize: 10.2,
  });
  addCard(slide, 0.72, 3.55, 4.0, 1.28, {
    accent: C.mint,
    label: 'FRONTEND',
    title: 'scripts/scaffold_frontend_module.py',
    titleSize: 14.5,
    body: '只生成前端 types / api / view / store，并补 route / menu registry。',
    bodySize: 10.2,
  });
  addCard(slide, 5.02, 3.55, 4.0, 1.28, {
    accent: C.teal,
    label: 'VERIFY',
    title: 'scripts/verify_framework_baseline.sh',
    titleSize: 14.6,
    body: '统一 baseline 验收入口，会把编译、单测、HTTP smoke、type-check、build 串起来。',
    bodySize: 10.0,
  });
  addFooter(slide, 27);
}

// Slide 28
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BASELINE FILES', 'baseline 里每个校验脚本分别在查什么', '不是“随便跑个脚本”，而是在查骨架、注册、接口和交付链路。');
  const baselineChecks = [
    ['backend/main.py', '后端主入口语法检查', C.teal],
    ['test_backend_scaffold.py', '后端脚手架生成与路由注册测试', C.amber],
    ['test_frontend_scaffold.py', '前端脚手架、路由和菜单注册测试', C.mint],
    ['test_fullstack_scaffold.py', '前后端一起生成时的联动测试', C.teal],
    ['test_menu_registry.py', '后端菜单注册并入菜单树测试', C.amber],
    ['test_router_registry.py', '后端路由注册动态挂载测试', C.mint],
    ['test_http_smoke.py', '登录、菜单、refresh、基础接口 smoke', C.teal],
    ['test_modular_routes.py', '模块化 router 组合是否正常', C.amber],
  ];
  baselineChecks.forEach(([file, desc, accent], idx) => {
    const col = idx % 2;
    const row = Math.floor(idx / 2);
    const x = col === 0 ? 0.72 : 5.02;
    const y = 1.98 + row * 0.76;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w: 4.0,
      h: 0.62,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 0.1,
      h: 0.62,
      fill: { color: accent },
      line: { color: accent, transparency: 100 },
    });
    slide.addText(file, {
      x: x + 0.2,
      y: y + 0.12,
      w: 1.78,
      h: 0.1,
      fontFace: 'Consolas',
      fontSize: 9.5,
      bold: true,
      color: C.dark,
      margin: 0,
      fit: 'shrink',
    });
    slide.addText(desc, {
      x: x + 1.98,
      y: y + 0.12,
      w: 1.78,
      h: 0.16,
      fontSize: 8.9,
      color: C.slate,
      margin: 0,
      fit: 'shrink',
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.0,
    y: 5.12,
    w: 8.0,
    h: 0.28,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('除此之外，verify 脚本最后还会继续跑前端 type-check 和 build-only。', {
    x: 1.3,
    y: 5.2,
    w: 7.4,
    h: 0.12,
    fontSize: 10.2,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 28);
}

// Slide 29
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'SCAFFOLD ENTRY', '新增模块时，先判断走哪条入口', '先分清这次只改前端、只改后端，还是两边都改。');
  addCard(slide, 0.7, 2.05, 2.6, 2.2, {
    accent: C.teal,
    label: 'ONLY BACKEND',
    title: 'backend scaffold',
    titleSize: 18,
    body: '只补后端模块\n\nbackend/scripts/scaffold_backend_module.py',
    bodySize: 12,
  });
  addCard(slide, 3.65, 2.05, 2.6, 2.2, {
    accent: C.amber,
    label: 'ONLY FRONTEND',
    title: 'frontend scaffold',
    titleSize: 18,
    body: '只补前端页面\n\nscripts/scaffold_frontend_module.py',
    bodySize: 12,
  });
  addCard(slide, 6.6, 2.05, 2.6, 2.2, {
    accent: C.mint,
    label: 'FULLSTACK',
    title: 'fullstack scaffold',
    titleSize: 18,
    body: '前后端一起补\n\nscripts/scaffold_fullstack_module.py',
    bodySize: 12,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.25,
    y: 2.17,
    w: 1.1,
    h: 0.28,
    rectRadius: 0.06,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('默认优先', {
    x: 7.42,
    y: 2.25,
    w: 0.76,
    h: 0.1,
    fontSize: 9,
    bold: true,
    color: C.white,
    margin: 0,
    align: 'center',
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.55,
    y: 4.58,
    w: 6.95,
    h: 0.48,
    rectRadius: 0.06,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('大多数标准新增功能，默认先选 fullstack scaffold，不要上来就复制旧模块。', {
    x: 1.85,
    y: 4.74,
    w: 6.35,
    h: 0.14,
    fontSize: 12,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 29);
}

// Slide 30
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(
    slide,
    'BOUNDARIES',
    '当前边界与不要误判的点',
    '这页专门提醒：哪些看起来像“已经好了”，其实还没有。',
  );
  addCard(slide, 0.72, 2.02, 4.0, 1.18, {
    accent: C.teal,
    label: 'MISJUDGMENT 01',
    title: '看到 sales / production，不等于完整 MES 做完',
    titleSize: 16,
    body: '它们是在演示这套基座怎么扩，不代表所有真实业务规则都已经定好了。',
    bodySize: 11.2,
  });
  addCard(slide, 5.02, 2.02, 4.0, 1.18, {
    accent: C.amber,
    label: 'MISJUDGMENT 02',
    title: '菜单能看见，不等于权限一定正确',
    titleSize: 16,
    body: '还要继续看 functionCode、permission、allowedMenuIds 和页面拦截是不是都对上。',
    bodySize: 11.2,
  });
  addCard(slide, 0.72, 3.45, 4.0, 1.18, {
    accent: C.mint,
    label: 'MISJUDGMENT 03',
    title: '脚手架生成完，不等于模块可以交付',
    titleSize: 16,
    body: '生成出来的只是最小骨架；占位字段、文案、SQL、seed 都还要换成正式业务内容。',
    bodySize: 11.2,
  });
  addCard(slide, 5.02, 3.45, 4.0, 1.18, {
    accent: C.teal,
    label: 'MISJUDGMENT 04',
    title: '仓库里有 mock 文件，不等于当前默认走 mock',
    titleSize: 16,
    body: '现在培训和联调默认应该走本地 FastAPI + PostgreSQL + seed，不是走 mock。',
    bodySize: 11.2,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.02,
    y: 4.9,
    w: 7.95,
    h: 0.34,
    rectRadius: 0.05,
    fill: { color: C.soft },
    line: { color: C.line, width: 1 },
  });
  slide.addText('拿不准当前边界时，先看 frameworkConfig.ts、router、menu.py 和 verify 结果，不要只凭感觉。', {
    x: 1.28,
    y: 5.01,
    w: 7.42,
    h: 0.12,
    fontSize: 10.6,
    bold: true,
    color: C.dark,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 30);
}

// Slide 31
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'BASELINE', '代码写完，不等于任务完成', '页面能打开，只算开始；baseline 过了，才算能交。');
  addStep(slide, 0.72, 2.05, 2.8, 0.8, 1, '先看 Python 语法和脚本', '不过：一运行就会报 import 或脚本错误。', C.teal);
  addStep(slide, 3.62, 2.05, 2.8, 0.8, 2, '确认后端公共能力', '不过：脚手架、注册点和模块路由可能被带坏。', C.amber);
  addStep(slide, 6.52, 2.05, 2.8, 0.8, 3, '确认接口能通', '不过：登录、菜单、refresh 和 CRUD 这条线会断。', C.mint);
  addStep(slide, 2.15, 3.25, 2.8, 0.8, 4, '确认前端类型', '不过：Vue / TS 类型会被这次改动带坏。', C.teal);
  addStep(slide, 5.05, 3.25, 2.8, 0.8, 5, '确认真实构建', '不过：页面能开，发布却过不了 build。', C.amber);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 2.45,
    y: 4.45,
    w: 5.1,
    h: 0.5,
    rectRadius: 0.05,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('统一入口：bash scripts/verify_framework_baseline.sh', {
    x: 2.7,
    y: 4.62,
    w: 4.6,
    h: 0.14,
    fontSize: 12,
    bold: true,
    color: C.white,
    align: 'center',
    margin: 0,
  });
  addFooter(slide, 31);
}

// Slide 32
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'STANDARD FLOW', '和 AI 协作时的标准流程', '这页不是讲模块怎么接，而是讲你和 AI 怎么配合不跑偏。');
  addStep(slide, 0.68, 2.08, 2.62, 0.9, 1, '先说清任务', '说清这次要做什么、不要改什么、验收到什么程度。', C.teal);
  addStep(slide, 3.4, 2.08, 2.62, 0.9, 2, '先把规则喂给 AI', '先读 AGENTS、training 文档和对应 skill。', C.amber);
  addStep(slide, 6.12, 2.08, 2.62, 0.9, 3, '再让 AI 读现状', '先看当前启用边界、路由、菜单和关键入口。', C.mint);
  addStep(slide, 2.0, 3.45, 2.9, 0.9, 4, '再开始改', '标准新增模块优先走 scaffold，局部问题再手工修改。', C.teal);
  addStep(slide, 5.1, 3.45, 2.9, 0.9, 5, '最后要求验证和说明', '说清修改文件、验证结果和剩余风险。', C.amber);
  addFooter(slide, 32);
}

// Slide 33
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'TROUBLESHOOTING', '常见问题从哪里开始查', '先按固定顺序查，别一出问题就盯着页面代码猛改。');
  addCard(slide, 0.72, 2.05, 4.02, 1.3, {
    accent: C.teal,
    label: 'CASE 01',
    title: '菜单不显示',
    titleSize: 16,
    body: '先看这个前缀有没有启用，再看后端菜单树和 registry 有没有接进去。',
  });
  addCard(slide, 5.0, 2.05, 4.02, 1.3, {
    accent: C.amber,
    label: 'CASE 02',
    title: '页面被重定向',
    titleSize: 16,
    body: '先看 functionCode、permission、allowedMenuIds 这些权限相关的值有没有对上。',
  });
  addCard(slide, 0.72, 3.62, 4.02, 1.3, {
    accent: C.mint,
    label: 'CASE 03',
    title: '模块生成后不完整',
    titleSize: 16,
    body: '先确认脚手架是不是走对了，再把占位字段、文案和 SQL 换成真的。',
  });
  addCard(slide, 5.0, 3.62, 4.02, 1.3, {
    accent: C.teal,
    label: 'CASE 04',
    title: '验证失败',
    titleSize: 16,
    body: '先看卡在哪一步：Python、后端测试、接口、type-check 还是 build。',
  });
  addFooter(slide, 33);
}

// Slide 34
{
  const slide = pptx.addSlide();
  fullBg(slide, C.cream);
  addTitleBlock(slide, 'PROMPT TEMPLATE', '给 AI 一个“能干活”的任务描述', '想让 AI 真干活，至少把这 5 件事交代清楚。');
  const promptTiles = [
    ['01', '目标', '这次到底要做什么', C.teal],
    ['02', '边界', '哪些东西不要改', C.amber],
    ['03', '挂载点', '挂到哪里，路由和功能码是什么', C.mint],
    ['04', '先读', '先读哪些规则和关键入口', C.teal],
    ['05', '验收', '做完跑什么验证，要汇报什么结果', C.amber],
  ];
  promptTiles.forEach(([num, title, body, color], idx) => {
    const x = 0.72 + idx * 1.72;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.02,
      w: 1.48,
      h: 0.9,
      rectRadius: 0.07,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    slide.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.12,
      y: 2.15,
      w: 0.22,
      h: 0.22,
      fill: { color },
      line: { color, transparency: 100 },
    });
    slide.addText(num, {
      x: x + 0.12,
      y: 2.22,
      w: 0.22,
      h: 0.08,
      fontSize: 8.5,
      bold: true,
      color: C.white,
      align: 'center',
      margin: 0,
    });
    slide.addText(title, {
      x: x + 0.42,
      y: 2.14,
      w: 0.92,
      h: 0.12,
      fontSize: 12,
      bold: true,
      color: C.dark,
      margin: 0,
      fit: 'shrink',
    });
    slide.addText(body, {
      x: x + 0.14,
      y: 2.45,
      w: 1.18,
      h: 0.28,
      fontSize: 8.8,
      color: C.slate,
      margin: 0,
      fit: 'shrink',
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72,
    y: 3.18,
    w: 8.55,
    h: 1.72,
    rectRadius: 0.06,
    fill: { color: C.dark },
    line: { color: C.dark, transparency: 100 },
  });
  slide.addText('可直接照抄的提示词开头', {
    x: 1.0,
    y: 3.38,
    w: 2.1,
    h: 0.14,
    fontSize: 11,
    bold: true,
    color: C.mint,
    margin: 0,
  });
  slide.addText('请基于当前 MES 基座处理这个任务：\n- 目标：新增 xxx 模块 / 修复 xxx 联动问题\n- 边界：不要改登录主干，不要改未启用业务域\n- 挂载点：放到 production，路由前缀 xxx，functionCode xxx\n- 先读：AGENTS.md、frameworkConfig.ts、router、menu.py\n- 验收：运行 baseline，并说明修改文件、验证结果和剩余风险', {
    x: 1.0,
    y: 3.66,
    w: 7.95,
    h: 0.98,
    fontFace: 'Consolas',
    fontSize: 11,
    color: C.white,
    margin: 0,
    fit: 'shrink',
  });
  slide.addText('参考：docs/training/ai-prompt-playbook.md', {
    x: 6.12,
    y: 4.66,
    w: 2.7,
    h: 0.12,
    fontSize: 9.6,
    color: 'D7E2F5',
    margin: 0,
    align: 'right',
  });
  addFooter(slide, 34);
}

// Slide 35
{
  const slide = pptx.addSlide();
  fullBg(slide, C.dark);
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 10,
    h: 0.28,
    fill: { color: C.teal },
    line: { color: C.teal, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 5.34,
    w: 10,
    h: 0.285,
    fill: { color: C.mint },
    line: { color: C.mint, transparency: 100 },
  });
  slide.addText('结论与参考材料', {
    x: 0.8,
    y: 1.0,
    w: 2.8,
    h: 0.25,
    fontSize: 16,
    bold: true,
    color: C.mint,
    margin: 0,
  });
  slide.addText('这套项目不是从零写页面，而是沿着现有基座继续加东西。', {
    x: 0.8,
    y: 1.58,
    w: 8.2,
    h: 0.62,
    fontSize: 22,
    bold: true,
    color: C.white,
    margin: 0,
    valign: 'mid',
  });
  const closingSteps = [
    ['Skill', '先定做法', C.mint],
    ['Scaffold', '先出骨架', C.teal],
    ['Registry', '再接系统', C.amber],
    ['Baseline', '最后验收', C.white],
  ];
  closingSteps.forEach(([label, body, accent], idx) => {
    const x = 0.84 + idx * 2.05;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.48,
      w: 1.74,
      h: 0.68,
      rectRadius: 0.06,
      fill: { color: C.white, transparency: 88 },
      line: { color: C.white, transparency: 82, width: 1 },
    });
    slide.addText(label, {
      x: x + 0.14,
      y: 2.62,
      w: 1.46,
      h: 0.12,
      fontFace: 'Consolas',
      fontSize: 11,
      bold: true,
      color: accent === C.white ? 'E8F1FF' : accent,
      margin: 0,
      align: 'center',
    });
    slide.addText(body, {
      x: x + 0.14,
      y: 2.84,
      w: 1.46,
      h: 0.1,
      fontSize: 10,
      color: C.white,
      margin: 0,
      align: 'center',
    });
  });
  slide.addText('建议继续阅读：', {
    x: 0.84,
    y: 3.75,
    w: 1.6,
    h: 0.18,
    fontSize: 12,
    bold: true,
    color: 'D8E6FF',
    margin: 0,
  });
  slide.addText('• docs/training/ai-collaboration-guide.md\n• docs/training/ai-prompt-playbook.md\n• docs/training/framework-baseline-training.md\n• docs/training/scaffold-registry-verify-training.md', {
    x: 1.05,
    y: 4.08,
    w: 5.6,
    h: 0.95,
    fontSize: 11.5,
    color: C.white,
    margin: 0,
  });
  addTopMotif(slide, true);
  addFooter(slide, 35, false);
}

const output = path.resolve(process.cwd(), 'docs/training/project-ai-dev-training.pptx');

pptx.writeFile({ fileName: output }).then(() => {
  console.log(output);
}).catch((error) => {
  console.error(error);
  process.exit(1);
});
