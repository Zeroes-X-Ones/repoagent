"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, ArrowUpRight, BarChart3, Brain, Clock3, DollarSign, Gauge, Sparkles } from "lucide-react";
import type { RunResult, RunStatus } from "./AIEngineerApp";

interface Props {
  apiBase: string;
  status: RunStatus;
  logsCount: number;
  result: RunResult | null;
}

interface AnalyticsOverview {
  total_requests: number;
  total_cost: number;
  total_cost_saved: number;
  average_compression: number;
  average_latency_ms: number;
  average_quality: number;
  success_rate: number;
}

interface RecentRequest {
  request_id: string;
  timestamp: string;
  repository: string;
  model: string;
  provider: string;
  selected_files: string[];
  compressed_token_count: number;
  original_token_count: number;
  latency_ms: number;
  estimated_cost: number;
  execution_status: string;
  quality_score: number;
}

interface RepositoryMetric {
  repository: string;
  requests: number;
  total_cost: number;
  average_latency_ms: number;
  average_quality: number;
  average_compression: number;
}

interface BenchmarkEntry {
  benchmark_id: string;
  timestamp: string;
  prompt: string;
  repository: string;
  model: string;
  provider: string;
  pipelines: Array<{
    pipeline: string;
    repository: string;
    model: string;
    provider: string;
    original_tokens: number;
    compressed_tokens: number;
    latency_ms: number;
    compression_ratio: number;
    estimated_cost: number;
    quality_score: number;
    context_size: number;
    execution_success: boolean;
  }>;
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 4 }).format(value);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: value >= 100 ? 0 : 2 }).format(value);
}

function formatTime(value: string) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function AnalyticsDashboard({ apiBase, status, logsCount, result }: Props) {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [requests, setRequests] = useState<RecentRequest[]>([]);
  const [repositories, setRepositories] = useState<RepositoryMetric[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [overviewRes, requestsRes, reposRes, benchRes] = await Promise.all([
          fetch(`${apiBase}/api/analytics/overview`),
          fetch(`${apiBase}/api/analytics/requests?limit=6`),
          fetch(`${apiBase}/api/analytics/top-repositories?limit=5`),
          fetch(`${apiBase}/api/explainability/benchmark/history`),
        ]);

        const overviewData = await overviewRes.json();
        const requestsData = await requestsRes.json();
        const reposData = await reposRes.json();
        const benchData = await benchRes.json();

        setOverview(overviewData?.data ?? null);
        setRequests(requestsData?.data ?? []);
        setRepositories(reposData?.data ?? []);
        setBenchmarks(benchData?.data ?? []);
      } catch {
        setOverview(null);
        setRequests([]);
        setRepositories([]);
        setBenchmarks([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [apiBase]);

  const latestBenchmark = useMemo(() => benchmarks[0], [benchmarks]);

  return (
    <div className="flex flex-col gap-4 p-4 lg:p-6 bg-[radial-gradient(circle_at_top_left,_rgba(88,166,255,0.14),_transparent_35%),linear-gradient(135deg,_rgba(13,17,23,0.98),_rgba(22,27,34,0.95))]">
      <div className="rounded-2xl border border-border/70 bg-surface/80 p-4 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-accent">
              <Sparkles size={14} />
              Intelligence workspace
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white">AI engineering analytics</h2>
              <p className="mt-1 max-w-2xl text-sm text-muted">
                Track retrieval quality, cost efficiency, and pipeline performance from every run in a single premium command center.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <div className="rounded-full border border-border bg-bg/70 px-3 py-2 text-muted">
              <span className="mr-2 inline-flex h-2.5 w-2.5 rounded-full bg-success" />
              {status === "running" ? "Live run in progress" : status === "completed" ? "Last run completed" : "Waiting for input"}
            </div>
            <div className="rounded-full border border-border bg-bg/70 px-3 py-2 text-muted">
              <span className="mr-2 inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
              {logsCount} log lines
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            title="Requests"
            value={overview ? formatNumber(overview.total_requests) : "—"}
            hint="Tracked pipeline runs"
            icon={<Activity size={16} />}
          />
          <MetricCard
            title="Total cost"
            value={overview ? formatCurrency(overview.total_cost) : "—"}
            hint="Estimated spend"
            icon={<DollarSign size={16} />}
          />
          <MetricCard
            title="Avg latency"
            value={overview ? `${formatNumber(overview.average_latency_ms)} ms` : "—"}
            hint="Response pacing"
            icon={<Clock3 size={16} />}
          />
          <MetricCard
            title="Success rate"
            value={overview ? `${overview.success_rate.toFixed(1)}%` : "—"}
            hint="Completed reliably"
            icon={<Gauge size={16} />}
          />
        </div>

        <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-muted">Efficiency</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Compression & savings</h3>
            </div>
            <div className="rounded-full border border-success/20 bg-success/10 p-2 text-success">
              <BarChart3 size={16} />
            </div>
          </div>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-xl border border-border/60 bg-bg/50 px-3 py-2 text-muted">
              <span>Average compression</span>
              <span className="font-semibold text-white">{overview ? `${overview.average_compression.toFixed(2)}x` : "—"}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-border/60 bg-bg/50 px-3 py-2 text-muted">
              <span>Cost saved</span>
              <span className="font-semibold text-white">{overview ? formatCurrency(overview.total_cost_saved) : "—"}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-border/60 bg-bg/50 px-3 py-2 text-muted">
              <span>Average quality</span>
              <span className="font-semibold text-white">{overview ? `${overview.average_quality.toFixed(2)}` : "—"}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-muted">Recent activity</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Latest requests</h3>
            </div>
            <div className="rounded-full border border-border bg-bg/70 px-3 py-1 text-[11px] text-muted">
              {loading ? "Loading…" : `${requests.length} captured`}
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {requests.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border/70 bg-bg/40 p-4 text-sm text-muted">
                No analytics requests yet. Start a run to populate this view.
              </div>
            ) : (
              requests.map((request) => (
                <div key={request.request_id} className="rounded-xl border border-border/60 bg-bg/50 px-3 py-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold text-white">{request.repository}</p>
                      <p className="text-[11px] text-muted">{formatTime(request.timestamp)}</p>
                    </div>
                    <div className="flex items-center gap-2 rounded-full border border-border bg-surface/50 px-2.5 py-1 text-[11px] text-muted">
                      <Brain size={12} />
                      {request.model} · {request.provider}
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted">
                    <span className="rounded-full border border-border/60 px-2.5 py-1">Quality {request.quality_score.toFixed(2)}</span>
                    <span className="rounded-full border border-border/60 px-2.5 py-1">{request.latency_ms.toFixed(0)} ms</span>
                    <span className="rounded-full border border-border/60 px-2.5 py-1">{request.selected_files.length} files</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-muted">Repository focus</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Top repositories</h3>
            </div>
            <div className="rounded-full border border-accent/20 bg-accent/10 p-2 text-accent">
              <ArrowUpRight size={16} />
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {repositories.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border/70 bg-bg/40 p-4 text-sm text-muted">
                Repository analytics will appear once requests are recorded.
              </div>
            ) : (
              repositories.map((repo) => (
                <div key={repo.repository} className="flex items-center justify-between rounded-xl border border-border/60 bg-bg/50 px-3 py-3 text-sm">
                  <div>
                    <p className="font-semibold text-white">{repo.repository}</p>
                    <p className="text-[11px] text-muted">{repo.requests} requests · {repo.average_quality.toFixed(2)} quality</p>
                  </div>
                  <div className="text-right text-[11px] text-muted">
                    <p>{formatCurrency(repo.total_cost)}</p>
                    <p>{repo.average_latency_ms.toFixed(0)} ms</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-muted">Explainability</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Current run context</h3>
            </div>
            <div className="rounded-full border border-warning/20 bg-warning/10 p-2 text-warning">
              <Brain size={16} />
            </div>
          </div>
          <div className="mt-4 rounded-xl border border-border/60 bg-bg/50 p-3 text-sm text-muted">
            {result?.explanation_preview ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-white">Explanation preview</p>
                <pre className="whitespace-pre-wrap text-[12px] leading-6 text-muted">{result.explanation_preview}</pre>
              </div>
            ) : (
              <div>
                <p className="font-medium text-white">No explanation artifact is available yet for the latest run.</p>
                <p className="mt-2">The dashboard will surface the latest explanation report as soon as the pipeline produces one.</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-muted">Benchmarks</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Pipeline comparisons</h3>
            </div>
            <div className="rounded-full border border-accent/20 bg-accent/10 p-2 text-accent">
              <BarChart3 size={16} />
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {!latestBenchmark ? (
              <div className="rounded-xl border border-dashed border-border/70 bg-bg/40 p-4 text-sm text-muted">
                Benchmark runs will appear here after the explainability benchmark endpoint is exercised.
              </div>
            ) : (
              <>
                <div className="rounded-xl border border-border/60 bg-bg/50 p-3 text-sm">
                  <p className="font-semibold text-white">{latestBenchmark.repository}</p>
                  <p className="mt-1 text-[11px] text-muted">{formatTime(latestBenchmark.timestamp)}</p>
                </div>
                {latestBenchmark.pipelines.map((pipeline) => (
                  <div key={`${latestBenchmark.benchmark_id}-${pipeline.pipeline}`} className="rounded-xl border border-border/60 bg-bg/50 px-3 py-3 text-sm">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-white">{pipeline.pipeline}</p>
                      <span className="rounded-full border border-success/20 bg-success/10 px-2 py-1 text-[11px] text-success">
                        {pipeline.execution_success ? "Healthy" : "Needs attention"}
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-muted">
                      <span className="rounded-full border border-border/60 px-2 py-1">{pipeline.latency_ms} ms</span>
                      <span className="rounded-full border border-border/60 px-2 py-1">{pipeline.compression_ratio.toFixed(2)}x compression</span>
                      <span className="rounded-full border border-border/60 px-2 py-1">{pipeline.quality_score.toFixed(2)} quality</span>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, hint, icon }: { title: string; value: string; hint: string; icon: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-surface/80 p-4">
      <div className="flex items-center justify-between">
        <p className="text-[11px] uppercase tracking-[0.24em] text-muted">{title}</p>
        <div className="rounded-full border border-border bg-bg/70 p-2 text-accent">{icon}</div>
      </div>
      <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-sm text-muted">{hint}</p>
    </div>
  );
}
