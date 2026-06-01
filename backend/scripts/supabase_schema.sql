-- Run this in Supabase SQL Editor

create table wbs_jobs (
  id uuid primary key,
  project_title text,
  company_name text,
  project_manager text,
  rough_scope text,
  project_config jsonb,
  status text default 'pending',
  created_at timestamptz,
  completed_at timestamptz
);

create table wbs_job_logs (
  id bigserial primary key,
  job_id uuid references wbs_jobs(id) on delete cascade,
  agent_name text,
  message text,
  level text default 'info',
  created_at timestamptz
);

create table wbs_token_usage (
  id bigserial primary key,
  job_id uuid references wbs_jobs(id) on delete cascade,
  agent_name text,
  model text,
  input_tokens int default 0,
  output_tokens int default 0,
  created_at timestamptz
);

create table wbs_output_files (
  id bigserial primary key,
  job_id uuid references wbs_jobs(id) on delete cascade,
  file_type text,
  file_path text,
  public_url text,
  email_sent boolean default false,
  email_sent_at timestamptz,
  created_at timestamptz
);
