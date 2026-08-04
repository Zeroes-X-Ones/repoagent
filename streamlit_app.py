import streamlit as st

from demo_data import get_demo_state

st.set_page_config(page_title="Paritok AI Platform", page_icon="⚡", layout="wide")

st.markdown(
    """
    <style>
    :root {
      color-scheme: dark;
    }
    .stApp {
      background: radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 24%),
                  linear-gradient(135deg, #07111f 0%, #0b1324 100%);
    }
    .block-container {
      padding-top: 2rem;
      padding-bottom: 2rem;
    }
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
    st.metric("Pipeline", "Healthy", "+12.4%")
    st.metric("Retention", "94%", "+4.1%")

nav = nav or "Overview"

if nav == "Overview":
    st.markdown("# Overview")
    st.caption("A cinematic control center for high-signal AI execution")
    cols = st.columns(4)
    metrics = [
        ("Original Tokens", state["overview"]["original_tokens"], "+6.2%"),
        ("Compressed Tokens", state["overview"]["compressed_tokens"], "-77.6%"),
        ("Tokens Saved", state["overview"]["tokens_saved"], "+18.3%"),
        ("Compression Ratio", f"{state['overview']['compression_ratio']}%", "+3.1%"),
    ]
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, f"{value:,}" if isinstance(value, int) else value, delta)

    st.markdown("### Live Pipeline")
    pipeline = st.container()
    with pipeline:
        cols = st.columns(7)
        for col, stage in zip(cols, state["pipeline_stages"]):
            with col:
                st.markdown(
                    f"<div style='border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px; background:rgba(255,255,255,0.04); min-height:120px;'>"
                    f"<div style='font-size:12px; text-transform:uppercase; color:#7dd3fc;'>{stage['name']}</div>"
                    f"<div style='font-size:18px; font-weight:600; color:white; margin-top:8px;'>{stage['detail']}</div>"
                    f"<div style='margin-top:12px; color:#86efac;'>● {stage['status']}</div></div>",
                    unsafe_allow_html=True,
                )

elif nav == "Compression":
    st.markdown("# Compression")
    repo = state["repositories"][0]
    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown("### Repository Tree")
        for file in repo["files"]:
            st.markdown(f"- {file['path']} · {file['status']} · score {file['importance']:.2f}")
    with right:
        st.markdown("### Context Comparison")
        st.text_area("Before Context", repo["before_context"], height=140)
        st.text_area("After Context", repo["after_context"], height=140)

elif nav == "Analytics":
    st.markdown("# Analytics")
    st.bar_chart({"Reduction": state["analytics"]["token_reduction"]})
    st.line_chart({"Latency": state["analytics"]["latency"], "Cost": state["analytics"]["cost"]})

elif nav == "Benchmarks":
    st.markdown("# Benchmarks")
    bench = state["benchmarks"]
    left, right = st.columns(2)
    left.metric("Without Paritok", f"{bench['without_paritok']['tokens']:,} tokens")
    right.metric("With Paritok", f"{bench['with_paritok']['tokens']:,} tokens")

elif nav == "History":
    st.markdown("# History")
    for item in state["history"]:
        st.markdown(f"### {item['id']} · {item['repository']}")
        st.write(item["summary"])

else:
    st.markdown(f"# {nav}")
    st.info("Demo-ready experience for the premium platform surface.")
