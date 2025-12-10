import streamlit as st
from supabase import create_client
from datetime import date, datetime, timedelta
import pandas as pd

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="Life OS",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# Supabase 连接
# ============================================================
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()
today = date.today()
today_str = today.isoformat()

# ============================================================
# 数据库操作函数
# ============================================================

# --- Daily Logs ---
def get_today_log():
    response = supabase.table("daily_logs").select("*").eq("date", today_str).execute()
    return response.data[0] if response.data else None

def get_logs_since(start_date: str):
    """获取从 start_date 开始的所有日志"""
    response = supabase.table("daily_logs").select("*").gte("date", start_date).order("date", desc=True).execute()
    return response.data or []

def save_daily_log(data: dict):
    data["date"] = today_str
    supabase.table("daily_logs").upsert(data).execute()

def auto_save():
    """自动保存当前 session state 到数据库"""
    data = {
        "date": today_str,
        "newsletter_done": st.session_state.get("newsletter_done", False),
        "newsletter_time": st.session_state.get("newsletter_time", 0),
        "newsletter_note": st.session_state.get("newsletter_note", ""),
        "video_done": st.session_state.get("video_done", False),
        "video_time": st.session_state.get("video_time", 0),
        "video_note": st.session_state.get("video_note", ""),
        "wechat_done": st.session_state.get("wechat_done", False),
        "wechat_time": st.session_state.get("wechat_time", 0),
        "gre_vocab_count": st.session_state.get("gre_vocab_count", 0),
        "gre_verbal_count": st.session_state.get("gre_verbal_count", 0),
        "gre_reading_count": st.session_state.get("gre_reading_count", 0),
        "lc_easy_count": st.session_state.get("lc_easy_count", 0),
        "lc_medium_count": st.session_state.get("lc_medium_count", 0),
        "lc_hard_count": st.session_state.get("lc_hard_count", 0),
        "lc_notes": st.session_state.get("lc_notes", ""),
    }
    supabase.table("daily_logs").upsert(data).execute()

def save_leetcode_progress():
    """LeetCode 即时保存回调"""
    # 从 input 组件的 key 同步到 session state
    st.session_state.lc_easy_count = st.session_state.get("lc_easy", 0)
    st.session_state.lc_medium_count = st.session_state.get("lc_medium", 0)
    st.session_state.lc_hard_count = st.session_state.get("lc_hard", 0)
    st.session_state.lc_notes = st.session_state.get("lc_note_input", "")
    auto_save()
    st.toast("Saved!")

# --- Research Projects ---
def get_active_projects():
    response = supabase.table("research_projects").select("*").eq("is_active", True).order("created_at", desc=True).execute()
    return response.data or []

def get_all_projects():
    response = supabase.table("research_projects").select("*").order("created_at", desc=True).execute()
    return response.data or []

def get_archived_projects():
    response = supabase.table("research_projects").select("*").eq("is_active", False).order("created_at", desc=True).execute()
    return response.data or []

def create_project(title: str):
    supabase.table("research_projects").insert({"title": title}).execute()

def archive_project(project_id: str):
    supabase.table("research_projects").update({"is_active": False}).eq("id", project_id).execute()

def delete_project(project_id: str):
    supabase.table("research_projects").delete().eq("id", project_id).execute()

# --- Research Logs ---
def get_latest_log(project_id: str):
    response = supabase.table("research_logs").select("*").eq("project_id", project_id).order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

def get_all_logs(project_id: str):
    response = supabase.table("research_logs").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
    return response.data or []

def get_research_logs_since(start_date: str):
    """获取从 start_date 开始的所有 research logs"""
    response = supabase.table("research_logs").select("*, research_projects(title)").gte("date", start_date).order("date", desc=True).execute()
    return response.data or []

def get_today_research_logs():
    """获取今天的 research logs"""
    response = supabase.table("research_logs").select("*, research_projects(title)").eq("date", today_str).execute()
    return response.data or []

def add_research_log(project_id: str, duration: int, content: str):
    supabase.table("research_logs").insert({
        "project_id": project_id,
        "date": today_str,
        "duration_minutes": duration,
        "content": content
    }).execute()

# --- Ideas ---
def get_all_ideas():
    response = supabase.table("ideas").select("*").order("created_at", desc=True).execute()
    return response.data or []

def get_active_ideas():
    response = supabase.table("ideas").select("*").neq("status", "Done").order("created_at", desc=True).execute()
    return response.data or []

def get_done_ideas():
    response = supabase.table("ideas").select("*").eq("status", "Done").order("updated_at", desc=True).execute()
    return response.data or []

def get_latest_idea_update(idea_id: str):
    response = supabase.table("idea_updates").select("*").eq("idea_id", idea_id).order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

def get_today_idea_updates():
    """获取今天的 idea updates"""
    response = supabase.table("idea_updates").select("*, ideas(title)").gte("created_at", today_str).execute()
    return response.data or []

def create_idea(title: str):
    supabase.table("ideas").insert({"title": title}).execute()

def update_idea_status(idea_id: str, status: str):
    supabase.table("ideas").update({"status": status, "updated_at": datetime.utcnow().isoformat()}).eq("id", idea_id).execute()

def delete_idea(idea_id: str):
    supabase.table("ideas").delete().eq("id", idea_id).execute()

def get_idea_updates(idea_id: str):
    response = supabase.table("idea_updates").select("*").eq("idea_id", idea_id).order("created_at", desc=True).execute()
    return response.data or []

def add_idea_update(idea_id: str, content: str):
    supabase.table("idea_updates").insert({"idea_id": idea_id, "content": content}).execute()

# ============================================================
# 初始化 Session State
# ============================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    log = get_today_log()

    if log:
        st.session_state.newsletter_done = log.get("newsletter_done", False)
        st.session_state.newsletter_time = log.get("newsletter_time", 0)
        st.session_state.newsletter_note = log.get("newsletter_note") or ""
        st.session_state.video_done = log.get("video_done", False)
        st.session_state.video_time = log.get("video_time", 0)
        st.session_state.video_note = log.get("video_note") or ""
        st.session_state.wechat_done = log.get("wechat_done", False)
        st.session_state.wechat_time = log.get("wechat_time", 0)
        st.session_state.gre_vocab_count = log.get("gre_vocab_count", 0)
        st.session_state.gre_verbal_count = log.get("gre_verbal_count", 0)
        st.session_state.gre_reading_count = log.get("gre_reading_count", 0)
        st.session_state.lc_easy_count = log.get("lc_easy_count", 0)
        st.session_state.lc_medium_count = log.get("lc_medium_count", 0)
        st.session_state.lc_hard_count = log.get("lc_hard_count", 0)
        st.session_state.lc_notes = log.get("lc_notes") or ""
    else:
        st.session_state.newsletter_done = False
        st.session_state.newsletter_time = 0
        st.session_state.newsletter_note = ""
        st.session_state.video_done = False
        st.session_state.video_time = 0
        st.session_state.video_note = ""
        st.session_state.wechat_done = False
        st.session_state.wechat_time = 0
        st.session_state.gre_vocab_count = 0
        st.session_state.gre_verbal_count = 0
        st.session_state.gre_reading_count = 0
        st.session_state.lc_easy_count = 0
        st.session_state.lc_medium_count = 0
        st.session_state.lc_hard_count = 0
        st.session_state.lc_notes = ""

    st.session_state.research_mode = False
    st.session_state.research_time = 0

if "idea_mode" not in st.session_state:
    st.session_state.idea_mode = False

# ============================================================
# Sidebar Navigation
# ============================================================
with st.sidebar:
    st.title("🧠 Life OS")
    page = st.radio("Navigation", ["📝 Daily Log", "📊 Summary"], label_visibility="collapsed")

# ============================================================
# 自定义 CSS
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    .stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 📝 Daily Log 页面
# ============================================================
if page == "📝 Daily Log":
    st.title("📝 Daily Log")
    st.caption(f"Today: {today_str}")

    # ----------------------------------------------------------
    # 模块 A: Information Diet
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("📰 Information Diet")

        newsletter_done = st.checkbox("Newsletter", value=st.session_state.newsletter_done, key="cb_nl")
        if newsletter_done:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("−5", key="nl_m", use_container_width=True):
                    st.session_state.newsletter_time = max(0, st.session_state.newsletter_time - 5)
                    auto_save()
                    st.rerun()
            with col2:
                st.markdown(f"<p style='text-align:center;font-size:1.1rem;margin:0.5rem 0;'>{st.session_state.newsletter_time} min</p>", unsafe_allow_html=True)
            with col3:
                if st.button("+5", key="nl_p", use_container_width=True):
                    st.session_state.newsletter_time += 5
                    auto_save()
                    st.rerun()
            newsletter_note = st.text_input("What did you learn?", value=st.session_state.newsletter_note, key="nl_note", label_visibility="collapsed", placeholder="Notes...")
            st.session_state.newsletter_note = newsletter_note
        st.session_state.newsletter_done = newsletter_done

        video_done = st.checkbox("Video / Podcast", value=st.session_state.video_done, key="cb_vid")
        if video_done:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("−5", key="vid_m", use_container_width=True):
                    st.session_state.video_time = max(0, st.session_state.video_time - 5)
                    auto_save()
                    st.rerun()
            with col2:
                st.markdown(f"<p style='text-align:center;font-size:1.1rem;margin:0.5rem 0;'>{st.session_state.video_time} min</p>", unsafe_allow_html=True)
            with col3:
                if st.button("+5", key="vid_p", use_container_width=True):
                    st.session_state.video_time += 5
                    auto_save()
                    st.rerun()
            video_note = st.text_input("What did you learn?", value=st.session_state.video_note, key="vid_note", label_visibility="collapsed", placeholder="Notes...")
            st.session_state.video_note = video_note
        st.session_state.video_done = video_done

        wechat_done = st.checkbox("WeChat / Other", value=st.session_state.wechat_done, key="cb_wc")
        if wechat_done:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("−5", key="wc_m", use_container_width=True):
                    st.session_state.wechat_time = max(0, st.session_state.wechat_time - 5)
                    auto_save()
                    st.rerun()
            with col2:
                st.markdown(f"<p style='text-align:center;font-size:1.1rem;margin:0.5rem 0;'>{st.session_state.wechat_time} min</p>", unsafe_allow_html=True)
            with col3:
                if st.button("+5", key="wc_p", use_container_width=True):
                    st.session_state.wechat_time += 5
                    auto_save()
                    st.rerun()
        st.session_state.wechat_done = wechat_done

    # ----------------------------------------------------------
    # 模块 B: Research & Projects
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("🔬 Research & Projects")

        research_mode = st.checkbox("Work on projects today?", value=st.session_state.research_mode, key="cb_research")
        st.session_state.research_mode = research_mode

        if research_mode:
            with st.expander("➕ Create New Project"):
                new_proj = st.text_input("Project name", key="new_proj", placeholder="e.g., ML Paper Implementation")
                if st.button("Create", key="btn_create_proj", use_container_width=True):
                    if new_proj.strip():
                        create_project(new_proj.strip())
                        st.success(f"Created: {new_proj}")
                        st.rerun()

            active_projects = get_active_projects()

            if active_projects:
                st.markdown("**Active Projects**")

                for proj in active_projects:
                    proj_id = proj["id"]
                    proj_title = proj["title"]

                    with st.expander(f"📂 {proj_title}"):
                        latest_log = get_latest_log(proj_id)
                        if latest_log:
                            content_preview = (latest_log.get('content') or '')[:100]
                            ellipsis = '...' if len(latest_log.get('content') or '') > 100 else ''
                            st.info(f"📝 **Last** ({latest_log['date']}): {content_preview}{ellipsis}")

                        note_content = st.text_area("Today's progress", key=f"note_{proj_id}", placeholder="What did you accomplish?", height=80)

                        if st.button("💾 Save", key=f"btn_save_{proj_id}", use_container_width=True):
                            if note_content.strip():
                                add_research_log(proj_id, 0, note_content.strip())
                                st.success("Saved!")
                                st.rerun()
                            else:
                                st.warning("Write something before saving.")

                        col1, col2 = st.columns(2)
                        with col1:
                            with st.popover("📜 History"):
                                all_logs = get_all_logs(proj_id)
                                if all_logs:
                                    for log in all_logs:
                                        st.markdown(f"**{log['date']}**")
                                        st.markdown(f"> {log['content']}")
                                        st.markdown("---")
                                else:
                                    st.caption("No logs yet.")
                        with col2:
                            with st.popover("⚙️ Manage"):
                                if st.button("📦 Archive", key=f"btn_archive_{proj_id}", use_container_width=True):
                                    archive_project(proj_id)
                                    st.success("Archived!")
                                    st.rerun()
                                st.markdown("---")
                                if st.button("🗑️ Delete", key=f"btn_delete_{proj_id}", type="secondary", use_container_width=True):
                                    delete_project(proj_id)
                                    st.rerun()
            else:
                st.caption("No active projects. Create one above!")

            archived = get_archived_projects()
            if archived:
                with st.expander("🏆 Completed Projects"):
                    for proj in archived:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{proj['title']}**")
                            logs = get_all_logs(proj["id"])
                            st.caption(f"{len(logs)} sessions logged")
                        with col2:
                            if st.button("🗑️", key=f"del_archived_{proj['id']}"):
                                delete_project(proj["id"])
                                st.rerun()

    # ----------------------------------------------------------
    # 模块 C: GRE Grind
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("📚 GRE Grind")

        st.markdown("**Vocabulary**")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("−10", key="gre_v_m", use_container_width=True):
                st.session_state.gre_vocab_count = max(0, st.session_state.gre_vocab_count - 10)
                auto_save()
                st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align:center;margin:0;'>{st.session_state.gre_vocab_count}</h3>", unsafe_allow_html=True)
        with col3:
            if st.button("+10", key="gre_v_p", use_container_width=True):
                st.session_state.gre_vocab_count += 10
                auto_save()
                st.rerun()

        st.markdown("**Verbal Sets**")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("−1", key="gre_vb_m", use_container_width=True):
                st.session_state.gre_verbal_count = max(0, st.session_state.gre_verbal_count - 1)
                auto_save()
                st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align:center;margin:0;'>{st.session_state.gre_verbal_count}</h3>", unsafe_allow_html=True)
        with col3:
            if st.button("+1", key="gre_vb_p", use_container_width=True):
                st.session_state.gre_verbal_count += 1
                auto_save()
                st.rerun()

        st.markdown("**Reading Passages**")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("−1", key="gre_rd_m", use_container_width=True):
                st.session_state.gre_reading_count = max(0, st.session_state.gre_reading_count - 1)
                auto_save()
                st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align:center;margin:0;'>{st.session_state.gre_reading_count}</h3>", unsafe_allow_html=True)
        with col3:
            if st.button("+1", key="gre_rd_p", use_container_width=True):
                st.session_state.gre_reading_count += 1
                auto_save()
                st.rerun()

    # ----------------------------------------------------------
    # 模块 D: LeetCode Grind
    # ----------------------------------------------------------
    lc_total = st.session_state.get("lc_easy", 0) + st.session_state.get("lc_medium", 0) + st.session_state.get("lc_hard", 0)
    with st.container(border=True):
        st.markdown(f"### LeetCode (Total: {lc_total})")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                "Easy",
                min_value=0,
                step=1,
                value=st.session_state.lc_easy_count,
                key="lc_easy",
                on_change=save_leetcode_progress
            )
        with col2:
            st.number_input(
                "Med",
                min_value=0,
                step=1,
                value=st.session_state.lc_medium_count,
                key="lc_medium",
                on_change=save_leetcode_progress
            )
        with col3:
            st.number_input(
                "Hard",
                min_value=0,
                step=1,
                value=st.session_state.lc_hard_count,
                key="lc_hard",
                on_change=save_leetcode_progress
            )

        with st.expander("Notes"):
            st.text_area(
                "Notes",
                value=st.session_state.lc_notes,
                key="lc_note_input",
                placeholder="Today's problem notes...",
                label_visibility="collapsed",
                on_change=save_leetcode_progress
            )

    # ----------------------------------------------------------
    # 模块 E: Idea Incubator
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("💡 Idea Incubator")

        idea_mode = st.checkbox("Any new ideas or progress?", value=st.session_state.idea_mode, key="cb_idea")
        st.session_state.idea_mode = idea_mode

        if idea_mode:
            with st.expander("➕ Create New Idea"):
                new_idea = st.text_input("Idea title", key="new_idea", placeholder="e.g., AI-powered study planner")
                if st.button("Create", key="btn_create_idea", use_container_width=True):
                    if new_idea.strip():
                        create_idea(new_idea.strip())
                        st.success(f"Created: {new_idea}")
                        st.rerun()

            active_ideas = get_active_ideas()

            if active_ideas:
                st.markdown("**Active Ideas**")

                status_config = {
                    "Seed": ("🌱", "Seed"), "Planning": ("📝", "Planning"),
                    "Building": ("🔨", "Building"), "Shelved": ("📦", "Shelved"),
                    "Done": ("✅", "Done"), "Idea": ("🌱", "Seed"), "In Progress": ("🔨", "Building"),
                }

                for idea in active_ideas:
                    idea_id = idea["id"]
                    idea_title = idea["title"]
                    current_status = idea.get("status", "Seed")
                    emoji, badge = status_config.get(current_status, ("🌱", "Seed"))

                    with st.expander(f"{emoji} {idea_title} `[{badge}]`"):
                        latest_update = get_latest_idea_update(idea_id)
                        if latest_update:
                            content_preview = (latest_update.get('content') or '')[:100]
                            ellipsis = '...' if len(latest_update.get('content') or '') > 100 else ''
                            st.info(f"📝 **Last** ({latest_update['created_at'][:10]}): {content_preview}{ellipsis}")

                        note_content = st.text_area("New thought or progress", key=f"idea_note_{idea_id}", placeholder="What's your latest thinking?", height=80)

                        status_options = ["Seed", "Planning", "Building", "Shelved", "Done"]
                        mapped_status = {"Idea": "Seed", "In Progress": "Building"}.get(current_status, current_status)
                        current_idx = status_options.index(mapped_status) if mapped_status in status_options else 0
                        new_status = st.selectbox("Status", status_options, index=current_idx, key=f"status_{idea_id}")

                        if st.button("💾 Save", key=f"btn_save_idea_{idea_id}", use_container_width=True):
                            saved = False
                            if note_content.strip():
                                add_idea_update(idea_id, note_content.strip())
                                saved = True
                            if new_status != current_status and new_status != mapped_status:
                                update_idea_status(idea_id, new_status)
                                saved = True
                            if saved:
                                st.success("Saved!")
                                st.rerun()
                            else:
                                st.warning("Nothing to save.")

                        col1, col2 = st.columns(2)
                        with col1:
                            with st.popover("📜 History"):
                                updates = get_idea_updates(idea_id)
                                if updates:
                                    for u in updates:
                                        st.markdown(f"**{u['created_at'][:10]}**")
                                        st.markdown(f"> {u['content']}")
                                        st.markdown("---")
                                else:
                                    st.caption("No updates yet.")
                        with col2:
                            with st.popover("⚙️ Manage"):
                                if st.button("🗑️ Delete", key=f"del_idea_{idea_id}", use_container_width=True):
                                    delete_idea(idea_id)
                                    st.rerun()
            else:
                st.caption("No active ideas. Create one above!")

            done_ideas = get_done_ideas()
            if done_ideas:
                with st.expander("✅ Completed Ideas"):
                    for idea in done_ideas:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{idea['title']}**")
                            updates = get_idea_updates(idea["id"])
                            st.caption(f"{len(updates)} updates logged")
                        with col2:
                            if st.button("🗑️", key=f"del_done_idea_{idea['id']}"):
                                delete_idea(idea["id"])
                                st.rerun()

    # ----------------------------------------------------------
    # 自动保存提示
    # ----------------------------------------------------------
    st.markdown("")
    st.caption("💾 Auto-save enabled — your data is saved automatically when you click +/- buttons")

# ============================================================
# 📊 Summary 页面
# ============================================================
elif page == "📊 Summary":
    st.title("📊 Summary Report")

    # ----------------------------------------------------------
    # A. 今日概览 (Today's Snapshot)
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("🎯 Today's Snapshot")

        today_log = get_today_log()

        if today_log:
            # 计算总时长
            info_time = (today_log.get("newsletter_time") or 0) + (today_log.get("video_time") or 0) + (today_log.get("wechat_time") or 0)
            vocab_count = today_log.get("gre_vocab_count") or 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Info Diet", f"{info_time} min")
            with col2:
                st.metric("GRE Vocab", vocab_count)
            with col3:
                verbal = today_log.get("gre_verbal_count") or 0
                reading = today_log.get("gre_reading_count") or 0
                st.metric("GRE Practice", f"V:{verbal} R:{reading}")
        else:
            st.info("No data logged today yet.")

        # 今日 Research 活动
        today_research = get_today_research_logs()
        if today_research:
            st.markdown("**Research Today**")
            for log in today_research:
                proj_name = log.get("research_projects", {}).get("title", "Unknown") if log.get("research_projects") else "Unknown"
                content = (log.get("content") or "")[:80]
                st.markdown(f"- **{proj_name}**: {content}...")

        # 今日 Idea 活动
        today_ideas = get_today_idea_updates()
        if today_ideas:
            st.markdown("**Ideas Today**")
            for update in today_ideas:
                idea_name = update.get("ideas", {}).get("title", "Unknown") if update.get("ideas") else "Unknown"
                content = (update.get("content") or "")[:80]
                st.markdown(f"- **{idea_name}**: {content}...")

    # ----------------------------------------------------------
    # B. 过去 3 天回顾 (Past 3 Days Trend)
    # ----------------------------------------------------------
    with st.container(border=True):
        st.subheader("📈 Past 3 Days")

        start_date = (today - timedelta(days=3)).isoformat()
        logs = get_logs_since(start_date)

        if logs:
            # 转换为 DataFrame
            df = pd.DataFrame(logs)

            # 时间分配图
            st.markdown("**Time Allocation**")
            if all(col in df.columns for col in ["date", "newsletter_time", "video_time", "wechat_time"]):
                chart_df = df[["date", "newsletter_time", "video_time", "wechat_time"]].copy()
                chart_df = chart_df.fillna(0)
                chart_df = chart_df.set_index("date")
                chart_df.columns = ["Newsletter", "Video", "WeChat"]
                st.bar_chart(chart_df)
            else:
                st.caption("Insufficient data for chart.")

            # GRE 进度
            st.markdown("**GRE Vocabulary Trend**")
            if "gre_vocab_count" in df.columns:
                vocab_df = df[["date", "gre_vocab_count"]].copy()
                vocab_df = vocab_df.fillna(0)
                vocab_df = vocab_df.set_index("date")
                vocab_df.columns = ["Words"]
                st.line_chart(vocab_df)
        else:
            st.info("No data in the past 3 days.")

        # Research 轨迹
        st.markdown("**Research Timeline**")
        research_logs = get_research_logs_since(start_date)
        if research_logs:
            for log in research_logs:
                proj_name = log.get("research_projects", {}).get("title", "Unknown") if log.get("research_projects") else "Unknown"
                st.markdown(f"**{log['date']}** - {proj_name}")
                st.markdown(f"> {log.get('content', '')[:150]}...")
                st.markdown("---")
        else:
            st.caption("No research logs in the past 3 days.")
