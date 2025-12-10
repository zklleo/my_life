-- ============================================================
-- Life OS Database Schema v2
-- 在 Supabase SQL Editor 中运行此脚本
-- https://supabase.com/dashboard → 你的项目 → SQL Editor
-- ============================================================

-- 如果你之前已经创建过旧表，先删除它们（可选）
-- DROP TABLE IF EXISTS idea_updates, ideas, research_logs, research_projects, daily_logs;

-- ============================================================
-- 1. 每日日志表 (Daily Logs) - 存储 Info Diet + GRE
-- ============================================================
create table if not exists daily_logs (
  date date primary key,

  -- Info Diet
  newsletter_done boolean default false,
  newsletter_time int default 0,
  newsletter_note text,
  video_done boolean default false,
  video_time int default 0,
  video_note text,
  wechat_done boolean default false,
  wechat_time int default 0,
  -- wechat_note 不再需要，但保留字段兼容性

  -- GRE (量化统计)
  gre_vocab_count int default 0,
  gre_verbal_count int default 0,
  gre_reading_count int default 0,

  -- LeetCode
  lc_easy_count int default 0,
  lc_medium_count int default 0,
  lc_hard_count int default 0,
  lc_notes text,

  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================================
-- 2. 学术项目表 (Research Projects)
-- ============================================================
create table if not exists research_projects (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  is_active boolean default true,  -- true=进行中, false=已归档
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================================
-- 3. 学术项目日志表 (Research Logs)
-- ============================================================
create table if not exists research_logs (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references research_projects(id) on delete cascade,
  date date not null,
  duration_minutes int default 0,
  content text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================================
-- 4. 奇思妙想表 (Ideas)
-- ============================================================
create table if not exists ideas (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  status text default 'Idea',  -- Idea, In Progress, Done
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================================
-- 5. Idea 更新记录表 (Idea Updates)
-- ============================================================
create table if not exists idea_updates (
  id uuid default gen_random_uuid() primary key,
  idea_id uuid references ideas(id) on delete cascade,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- ============================================================
-- 索引优化
-- ============================================================
create index if not exists idx_research_logs_project on research_logs(project_id);
create index if not exists idx_research_logs_date on research_logs(date);
create index if not exists idx_idea_updates_idea on idea_updates(idea_id);

-- ============================================================
-- 字段迁移 (给已存在的表添加新字段)
-- ============================================================
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS lc_easy_count int default 0;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS lc_medium_count int default 0;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS lc_hard_count int default 0;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS lc_notes text;
