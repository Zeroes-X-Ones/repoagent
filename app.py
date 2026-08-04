import streamlit as st

from demo_data import get_demo_state

st.set_page_config(page_title="Paritok AI Platform", page_icon="⚡", layout="wide")

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp {
      background: radial-gradient(circle at top left, rgba(59,130,246,0.24), transparent 25%),
                  linear-gradient(135deg, #07111f 0%, #0b1324 100%);
    }
    .block-container {
      padding-top: 1.4rem;
      padding-bottom: 2rem;
    }
    .hero {
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 24px;
      padding: 24px;
      background: linear-gradient(135deg, rgba(16,24,38,0.95), rgba(9,14,24,0.92));
      box-shadow: 0 18px 50px rgba(0,0,0,0.28);
      margin-bottom: 16px;
    }
    .card {
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255,255,255,0.04);
      backdrop-filter: blur(16px);
      min-height: 132px;
      margin-bottom: 10px;
    }
    .card h4, .card h3 { margin: 0; }
    .kpi { font-size: 1.7rem; font-weight: 700; color: #f8fafc; }
    .muted { color: #94a3b8; font-size: 0.88rem; }
    .accent { color: #7dd3fc; }
    .success { color: #86efac; }
    .warning { color: #fbbf24; }
    .pill {
      display: inline-block;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.76rem;
      border: 1px solid rgba(255,255,255,0.13);
      color: #e2e8f0;
      background: rgba(255,255,255,0.06);
    }
    .pipeline-node {
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 16px;
      padding: 12px;
      background: rgba(255,255,255,0.04);
      min-height: 108px;
      text-align: center;
    }
    .pipeline-node.active { border-color: #7dd3fc; box-shadow: inset 0 0 0 1px rgba(125,211,252,0.35); }
    .pipeline-node.done { border-color: #86efac; }
    .pipeline-arrow { text-align:center; color:#7dd3fc; padding-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

state = get_demo_state()

with st.sidebar:
    st.markdown("## ⚡ Paritok")
    st.caption("Premium AI developer platform")
    nav = st.radio(
        "Navigation",
        ["Overview", "Repositories", "Agent", "Compression", "Analytics", "Benchmarks", "History", "Settings"],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.metric("Pipeline", "Healthy", "+12.4%")
    st.metric("Retention", "94%", "+4.1%")
    st.markdown("</div>", unsafe_allow_html=True)

if nav == "Overview":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Overview</h1><div class='muted' style='margin-top:8px;'>A cinematic control center for high-signal AI execution.</div></div>", unsafe_allow_html=True)

    overview = state["overview"]
    cards = [
        ("Original Tokens", f"{overview['original_tokens']:,}", "+6.2%", "🧠", "Live context volume"),
        ("Compressed Tokens", f"{overview['compressed_tokens']:,}", "-77.6%", "⚡", "Compressed footprint"),
        ("Tokens Saved", f"{overview['tokens_saved']:,}", "+18.3%", "💾", "Preserved signal"),
        ("Compression Ratio", f"{overview['compression_ratio']}%", "+3.1%", "📉", "Reduction efficiency"),
        ("Estimated Cost", f"${overview['estimated_cost']:.3f}", "-12.8%", "💸", "Spend efficiency"),
        ("Estimated Cost Saved", f"${overview['estimated_cost_saved']:.3f}", "+9.2%", "🛡️", "Cost avoided"),
        ("Latency", f"{overview['latency']} ms", "-21%", "⏱️", "Time to answer"),
        ("Quality Score", f"{overview['quality_score']:.2f}", "+0.04", "🎯", "Output confidence"),
    ]

    cols = st.columns(4)
    for idx, card in enumerate(cards):
        col = cols[idx % 4]
        with col:
            st.markdown(
                f"<div class='card'><div class='pill'>{card[3]} {card[4]}</div><div class='kpi' style='margin-top:10px;'>{card[1]}</div><div class='muted' style='margin-top:6px;'>{card[0]}</div><div class='accent' style='margin-top:10px;'>{card[2]}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='hero' style='margin-top:10px;'><h3 style='margin:0;'>Live Pipeline</h3><div class='muted' style='margin-top:8px;'>Each stage animates as the system advances through repository understanding, retrieval, compression, verification, and PR creation.</div></div>", unsafe_allow_html=True)
    stages = state["pipeline_stages"]
    for i, stage in enumerate(stages):
        if i < len(stages) - 1:
            st.markdown(f"<div class='pipeline-arrow'>↓</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='pipeline-node {'active' if stage['status'] == 'active' else 'done' if stage['status'] == 'done' else ''}'><div class='accent' style='font-size:0.7rem; text-transform:uppercase;'>Stage {i + 1}</div><div style='font-weight:650; margin-top:6px;'>{stage['name']}</div><div class='muted' style='margin-top:6px;'>{stage['detail']}</div><div class='success' style='margin-top:8px;'>{stage['status']}</div></div>",
            unsafe_allow_html=True,
        )

elif nav == "Repositories":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Repositories</h1><div class='muted' style='margin-top:8px;'>A high-clarity workspace for the most relevant agent context.</div></div>", unsafe_allow_html=True)
    for repo in state["repositories"]:
        with st.expander(repo["name"], expanded=True):
            files = repo["files"]
            for file in files:
                st.markdown(f"- {file['path']} · {file['status']} · score {file['importance']:.2f} · {file['reason']}")

elif nav == "Agent":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Agent</h1><div class='muted' style='margin-top:8px;'>A focused operating surface for the workspace agent, execution logic, and review flow.</div></div>", unsafe_allow_html=True)
    st.info("The agent is operating with a premium, demo-ready experience that is ready for live backend replacement.")

elif nav == "Compression":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Compression</h1><div class='muted' style='margin-top:8px;'>A polished view of selected context, removed noise, and retained importance.</div></div>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown("### Repository Tree")
        for repo in state["repositories"]:
            st.markdown(f"**{repo['name']}**")
            for file in repo["files"]:
                st.markdown(f"- {file['path']} · {file['status']}")
    with right:
        st.markdown("### Before / After Context")
        repo = state["repositories"][0]
        st.text_area("Before Context", repo["before_context"], height=140)
        st.text_area("After Context", repo["after_context"], height=140)

elif nav == "Analytics":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Analytics</h1><div class='muted' style='margin-top:8px;'>Token reduction, cost, latency, usage, and quality trends in one elegant control room.</div></div>", unsafe_allow_html=True)
    st.line_chart({"Token Reduction": state["analytics"]["token_reduction"], "Compression Trend": state["analytics"]["compression_trend"]})
    st.bar_chart({"Latency": state["analytics"]["latency"], "Cost": state["analytics"]["cost"]})
    st.line_chart({"Request History": [item["value"] for item in state["analytics"]["request_history"]]})

elif nav == "Benchmarks":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Benchmarks</h1><div class='muted' style='margin-top:8px;'>A professional comparison of the baseline versus the Paritok-enabled flow.</div></div>", unsafe_allow_html=True)
    bench = state["benchmarks"]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h3>Without Paritok</h3><div class='kpi' style='margin-top:8px;'>{:,} tokens</div><div class='muted' style='margin-top:6px;'>Latency {}</div></div>".format(bench["without_paritok"]["tokens"], bench["without_paritok"]["latency"]), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>With Paritok</h3><div class='kpi' style='margin-top:8px;'>{:,} tokens</div><div class='muted' style='margin-top:6px;'>Latency {}</div></div>".format(bench["with_paritok"]["tokens"], bench["with_paritok"]["latency"]), unsafe_allow_html=True)

elif nav == "History":
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>History</h1><div class='muted' style='margin-top:8px;'>Previous executions with context, compression, and quality summaries.</div></div>", unsafe_allow_html=True)
    for item in state["history"]:
        with st.expander(f"{item['id']} · {item['repository']}", expanded=False):
            st.write(item["summary"])
            st.caption(f"Prompt: {item['prompt']}")
            st.write(f"Compression: {item['compression']} · Quality: {item['quality']} · Cost: {item['cost']} · Latency: {item['latency']}")

else:
    st.markdown("<div class='hero'><h1 style='margin:0; font-size:2rem;'>Settings</h1><div class='muted' style='margin-top:8px;'>Ready for live backend wiring without exposing empty states.</div></div>", unsafe_allow_html=True)
    st.success("Demo mode enabled. The interface is prepared for future API-backed data with minimal structural changes.")
