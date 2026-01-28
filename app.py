import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pymongo
import bcrypt
import os
import extra_streamlit_components as stx
import time

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="IELTS Momentum",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Cookie Manager Init
# ----------------------------
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# ----------------------------
# Modern CSS
# ----------------------------
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background: #f5f7fa;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    
    /* Global Text Colors */
    .main .stMarkdown, .main .stText, .main h1, .main h2, .main h3, .main p, .main li {
        color: #222222 !important;
    }
    
    /* 1. DEFAULT INPUT STYLE (For Settings & Main App) - DARK TEXT */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        color: #333333 !important;
        background-color: #ffffff !important;
    }
    .stTextInput label, .stNumberInput label, .stDateInput label, .stSlider label, .stSelectbox label {
        color: #333333 !important;
        font-weight: 600;
    }
    
    /* Sidebar Text White */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }

    /* Login Specifics */
    .login-header { font-size: 2.5rem; font-weight: 700; color: #333333 !important; margin-bottom: 0.5rem; }
    .login-sub { font-size: 1rem; color: #666666 !important; }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.4);
        margin-bottom: 20px;
        color: #222222 !important;
    }

    /* Settings Page Header Card */
    .settings-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 16px;
        color: white !important;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
    }
    .settings-header h1 { color: white !important; margin: 0; }
    .settings-header p { color: rgba(255,255,255,0.8) !important; margin: 5px 0 0 0; }
    
    /* --- IMPROVED ADMIN STYLING --- */
    .admin-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-top: 5px solid #FF512F;
        text-align: center;
        border-left: 1px solid #eee;
        border-right: 1px solid #eee;
        border-bottom: 1px solid #eee;
    }
    .admin-metric-label {
        font-size: 0.85rem;
        color: #4a5568 !important; /* Dark Slate Grey - Sharp Contrast */
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .admin-metric-val {
        font-size: 3rem;
        font-weight: 800;
        color: #1a202c !important; /* Almost Black */
        margin: 0;
    }
    .activity-item {
        background: white;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 8px;
        color: #2d3748 !important;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Student Dashboard Styling */
    .metric-value {
        font-size: 32px; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-label { color: #64748b !important; font-size: 14px; font-weight: 600; text-transform: uppercase; }
    .challenge-box {
        background: white; border-left: 5px solid #667eea; padding: 20px;
        border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); color: #222222 !important;
    }
    
    /* Status Pills */
    .status-pill { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .pill-easy { background: #d1fae5; color: #065f46 !important; }
    .pill-medium { background: #fef3c7; color: #92400e !important; }
    .pill-hard { background: #fee2e2; color: #991b1b !important; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Mongo Connection
# ----------------------------
@st.cache_resource
def get_db():
    try:
        if "mongo" not in st.secrets:
            st.error("❌ 'mongo' section missing in secrets.toml")
            st.stop()
        uri = st.secrets["mongo"]["uri"]
        db_name = st.secrets["mongo"]["db_name"]
        client = pymongo.MongoClient(uri)
        return client[db_name]
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

db = get_db()
users_col = db["users"]
challenges_col = db["challenges"]
activity_col = db["activity"]
scores_col = db["scores"]

# ----------------------------
# Logic Helpers
# ----------------------------
def now_utc(): return datetime.utcnow()
def today_str(): return datetime.utcnow().strftime("%Y-%m-%d")

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())

def check_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed)

def create_user(username, password, name, role="student"):
    if users_col.find_one({"username": username}):
        return False, "Username already exists"
    
    users_col.insert_one({
        "username": username,
        "password_hash": hash_password(password),
        "name": name,
        "role": role,
        "target_score": 7.5,
        "created_at": now_utc(),
        "settings": {"learning_time": "Evening", "difficulty": "Medium"}
    })
    return True, "User created successfully"

def ensure_dummy_data():
    demo_users = [
        ("admin", "leap123", "Super Admin", "admin"),
        ("demo", "demo123", "Alex Student", "student")
    ]
    for u, p, name, role in demo_users:
        if not users_col.find_one({"username": u}):
            create_user(u, p, name, role)

def get_or_create_today_challenges(username: str):
    d = today_str()
    docs = list(challenges_col.find({"username": username, "date": d}).sort("id", 1))
    if docs: return docs

    # FIXED XP VALUES: Easy=10, Medium=20, Hard=30
    seed = [
        {"id": 1, "type": "Listening", "difficulty": "Easy", "duration": "5 min", "xp": 10},
        {"id": 2, "type": "Reading", "difficulty": "Medium", "duration": "8 min", "xp": 20},
        {"id": 3, "type": "Writing", "difficulty": "Hard", "duration": "12 min", "xp": 30},
    ]
    new_docs = []
    for c in seed:
        doc = {**c, "username": username, "date": d, "completed": False, "created_at": now_utc()}
        challenges_col.insert_one(doc)
        new_docs.append(doc)
    return new_docs

def mark_challenge_completed(username: str, challenge_id: int):
    d = today_str()
    res = challenges_col.update_one(
        {"username": username, "date": d, "id": challenge_id, "completed": False},
        {"$set": {"completed": True, "completed_at": now_utc()}}
    )
    if res.modified_count == 1:
        activity_col.insert_one({
            "username": username, "date": d, "event": "challenge_completed",
            "challenge_id": challenge_id, "ts": now_utc()
        })
        st.balloons()

def get_level(xp): return int(1 + (xp / 100))

# ----------------------------
# Init
# ----------------------------
ensure_dummy_data()

# Check Cookie for persistence
cookie_user = cookie_manager.get(cookie="logged_in_user")

if "authenticated" not in st.session_state:
    if cookie_user:
        # Verify user still exists in DB
        u_data = users_col.find_one({"username": cookie_user})
        if u_data:
            st.session_state.authenticated = True
            st.session_state.username = cookie_user
            st.session_state.role = u_data.get("role", "student")
        else:
            st.session_state.authenticated = False
            st.session_state.username = None
    else:
        st.session_state.authenticated = False
        st.session_state.username = None

# ----------------------------
# Login / Sign Up Screen
# ----------------------------
if not st.session_state.authenticated:
    # 2. LOGIN PAGE SPECIFIC OVERRIDES (White Text)
    # This block is INSIDE the if condition so it only applies here
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-attachment: fixed; }
        .login-container { background: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 400px; margin: 80px auto 0 auto; }
        
        /* OVERRIDE INPUTS JUST FOR LOGIN PAGE */
        .stTextInput input { 
            color: #ffffff !important; 
            -webkit-text-fill-color: #ffffff !important; 
            background-color: rgba(0,0,0,0.6) !important; 
            caret-color: #ffffff !important; 
            border-radius: 8px; 
        }
        .stTextInput label { color: #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 1, 1])
    
    with col2:
        if "auth_mode" not in st.session_state: st.session_state.auth_mode = "Login"
        
        st.markdown(f"""
        <div class="login-container">
            <h1 class="login-header">🚀 IELTS Momentum</h1>
            <p class="login-sub">{st.session_state.auth_mode}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 20px 40px; border-radius: 0 0 20px 20px; max-width: 400px; margin: -20px auto 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "Login":
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In ➔", use_container_width=True):
                    user = users_col.find_one({"username": u.strip()})
                    if user and check_password(p, user["password_hash"]):
                        st.session_state.authenticated = True
                        st.session_state.username = user["username"]
                        st.session_state.role = user.get("role", "student")
                        
                        # SET COOKIE (Expires in 7 days)
                        cookie_manager.set("logged_in_user", user["username"], expires_at=datetime.now() + timedelta(days=7))
                        
                        st.rerun()
                    else: st.error("Invalid credentials")
            if st.button("New here? Create Account", use_container_width=True):
                st.session_state.auth_mode = "Sign Up"; st.rerun()

        else: # Sign Up Mode
            with st.form("signup"):
                new_u = st.text_input("Choose Username")
                new_p = st.text_input("Choose Password", type="password")
                new_name = st.text_input("Your Full Name")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if len(new_p) < 4: st.error("Password too short")
                    elif not new_u or not new_name: st.error("All fields required")
                    else:
                        success, msg = create_user(new_u.strip(), new_p, new_name, "student")
                        if success: st.success("Account created! Please log in."); st.session_state.auth_mode = "Login"; st.rerun()
                        else: st.error(msg)
            if st.button("Back to Login", use_container_width=True):
                st.session_state.auth_mode = "Login"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------------------
# Sidebar (Logged In)
# ----------------------------
st.markdown("""<style>.stApp {background: linear-gradient(to right, #c3cfe2, #f5f7fa);}</style>""", unsafe_allow_html=True)

user_role = st.session_state.role
username = st.session_state.username
user_profile = users_col.find_one({"username": username})

st.sidebar.markdown(f"""
<div style="text-align: center; padding: 20px 0;">
    <div style="width: 80px; height: 80px; background: #e2e8f0; border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 30px;">
        {'👑' if user_role=='admin' else '👤'}
    </div>
    <h3 style="margin:0; color: #ffffff !important;">{user_profile.get('name', username)}</h3>
    <p style="color: #dddddd !important; font-size: 14px;">{user_role.title()}</p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Logout", use_container_width=True):
    cookie_manager.delete("logged_in_user")
    st.session_state.authenticated = False
    st.rerun()
st.sidebar.markdown("---")

# ----------------------------
# ADMIN VIEW
# ----------------------------
if user_role == "admin":
    page = st.sidebar.radio("Admin Menu", ["📊 Global Dashboard", "👥 User Manager", "⚙️ Content Editor"])
    
    if page == "📊 Global Dashboard":
        st.title("📊 Admin Dashboard")
        st.markdown("Overview of platform performance and engagement.")
        total_students = users_col.count_documents({"role": "student"})
        total_admins = users_col.count_documents({"role": "admin"})
        active_today = len(activity_col.distinct("username", {"date": today_str()}))
        total_actions = activity_col.count_documents({})
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="admin-card"><div class="admin-metric-label">Total Students</div><div class="admin-metric-val">{total_students}</div></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="admin-card"><div class="admin-metric-label">Admins</div><div class="admin-metric-val">{total_admins}</div></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="admin-card"><div class="admin-metric-label">Active Today</div><div class="admin-metric-val">{active_today}</div></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="admin-card"><div class="admin-metric-label">Total Actions</div><div class="admin-metric-val">{total_actions}</div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_chart, col_recent = st.columns([2, 1])
        with col_chart:
            st.subheader("📈 Platform Activity")
            pipeline = [{"$group": {"_id": "$date", "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
            data = list(activity_col.aggregate(pipeline))
            if data:
                df = pd.DataFrame(data)
                fig = px.bar(df, x="_id", y="count", labels={'_id': 'Date', 'count': 'Actions'})
                fig.update_traces(marker_color='#FF512F')
                fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#333"))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("No activity data.")

        with col_recent:
            st.subheader("🕒 Recent Logins")
            recent = list(activity_col.find().sort("ts", -1).limit(5))
            if recent:
                for act in recent:
                    # New Activity Item Style
                    st.markdown(f"""
                    <div class="activity-item">
                        <div><b>{act['username']}</b></div>
                        <div style="font-size:12px;color:#666;">{act.get('date', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.caption("No recent activity.")

    elif page == "👥 User Manager":
        st.title("👥 User Management")
        tab1, tab2 = st.tabs(["📋 All Users", "➕ Create User"])
        with tab1:
            all_users = list(users_col.find({}, {"password_hash": 0, "_id": 0}))
            if all_users:
                df = pd.DataFrame(all_users)
                search = st.text_input("🔍 Search User", placeholder="Type username...")
                if search: df = df[df['username'].str.contains(search, case=False)]
                st.dataframe(df, column_config={"username": "Username", "name": "Name", "role": "Role"}, use_container_width=True, hide_index=True)
                
                st.markdown("### 🛠 User Actions")
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: u_select = st.selectbox("Select User", df['username'].tolist())
                with c2: act_type = st.selectbox("Action", ["Delete User", "Promote to Admin", "Demote to Student"])
                with c3:
                    st.write(""); st.write("")
                    if st.button("Apply", type="primary"):
                        if u_select == username: st.error("Cannot modify self.")
                        else:
                            if "Delete" in act_type: users_col.delete_one({"username": u_select}); st.success("Deleted!")
                            elif "Admin" in act_type: users_col.update_one({"username": u_select}, {"$set": {"role": "admin"}}); st.success("Promoted!")
                            elif "Student" in act_type: users_col.update_one({"username": u_select}, {"$set": {"role": "student"}}); st.success("Demoted!")
                            st.rerun()

        with tab2:
            st.subheader("Create New Account")
            with st.form("create_user_admin"):
                c1, c2 = st.columns(2)
                with c1: n_u = st.text_input("Username"); n_r = st.selectbox("Role", ["student", "admin"])
                with c2: n_p = st.text_input("Password", type="password"); n_n = st.text_input("Name")
                if st.form_submit_button("Create"):
                    success, msg = create_user(n_u, n_p, n_n, n_r)
                    if success: st.success(msg)
                    else: st.error(msg)

    elif page == "⚙️ Content Editor":
        st.title("⚙️ Content Manager")
        with st.expander("➕ Add New Daily Challenge", expanded=True):
            with st.form("new_challenge"):
                c1, c2 = st.columns(2)
                with c1: 
                    c_type = st.selectbox("Skill", ["Listening", "Reading", "Writing", "Speaking"])
                    c_diff = st.selectbox("Diff", ["Easy", "Medium", "Hard"])
                with c2: 
                    c_dur = st.text_input("Duration (e.g. 10 min)")
                    # Auto-assign XP based on difficulty, disabled user input for consistency
                    xp_map = {"Easy": 10, "Medium": 20, "Hard": 30}
                    c_xp = st.number_input("XP (Fixed)", value=xp_map[c_diff], disabled=True)
                
                if st.form_submit_button("Publish"):
                    # Logic to add to DB (Simplified for now)
                    # In real app: insert into challenges_col
                    st.success(f"Published {c_diff} challenge worth {xp_map[c_diff]} XP!")

# ----------------------------
# STUDENT VIEW
# ----------------------------
else:
    page = st.sidebar.radio("Menu", ["📊 My Dashboard", "🎮 Practice Zone", "🏆 Leaderboard", "⚙️ Settings"])
    
    if page == "📊 My Dashboard":
        st.markdown(f"## 👋 Hi, {user_profile.get('name', 'Alex')}")
        total_xp = sum(c.get('xp', 0) for c in challenges_col.find({"username": username, "completed": True}))
        level = get_level(total_xp)
        streak = len(activity_col.distinct("date", {"username": username}))
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="glass-card"><div class="metric-label">Level</div><div class="metric-value">{level}</div></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="glass-card"><div class="metric-label">XP</div><div class="metric-value">{total_xp}</div></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="glass-card"><div class="metric-label">Streak</div><div class="metric-value">{streak} 🔥</div></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="glass-card"><div class="metric-label">Target</div><div class="metric-value">{user_profile.get('target_score', 7.5)}</div></div>""", unsafe_allow_html=True)

        left, right = st.columns([2, 1])
        with left:
            st.markdown("### 📅 Score History")
            scores = list(scores_col.find({"username": username}))
            if scores:
                df = pd.DataFrame(scores).sort_values("date")
                fig = px.area(df, x="date", y=["Listening", "Reading", "Writing", "Speaking"], color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300, font=dict(color="#333"), margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("No scores yet.")
        with right:
            st.markdown("### 🎯 Next Up")
            todays = get_or_create_today_challenges(username)
            next_c = next((c for c in todays if not c["completed"]), None)
            if next_c:
                st.markdown(f"""<div class="challenge-box"><span class="status-pill pill-{next_c['difficulty'].lower()}">{next_c['difficulty']}</span><h3 style="margin:10px 0;">{next_c['type']}</h3><p style="color:#666 !important;">⏱️ {next_c['duration']} • ⭐ {next_c['xp']} XP</p></div>""", unsafe_allow_html=True)
                if st.button("Start →", key="start_main", use_container_width=True):
                    mark_challenge_completed(username, next_c["id"]); st.rerun()
            else: st.success("All done! 🎉")

    elif page == "🎮 Practice Zone":
        st.title("Today's Tasks")
        todays = get_or_create_today_challenges(username)
        completed = sum(1 for c in todays if c['completed'])
        
        # Display progress bar only if there are tasks
        if todays:
            st.progress(completed / len(todays))
        else:
            st.info("No tasks scheduled for today yet.")
        
        for c in todays:
            done = c['completed']
            
            # FIXED: Correct color mapping for all 3 levels
            if c['difficulty'] == "Easy":
                color = "pill-easy"
            elif c['difficulty'] == "Medium":
                color = "pill-medium"
            else:
                color = "pill-hard"
            
            with st.container():
                c1, c2 = st.columns([4, 1])
                # Added opacity to fade out completed tasks
                with c1: 
                    st.markdown(f"""
                    <div class="challenge-box" style="opacity:{0.6 if done else 1}; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <b>{c['type']}</b>
                            <p style="margin:0;color:#666 !important; font-size:0.9rem;">{c['duration']} • {c['xp']} XP</p>
                        </div>
                        <span class="status-pill {color}">{c['difficulty']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c2:
                    st.write(""); st.write("") # Spacers for alignment
                    if not done:
                        # Unique key is crucial for buttons inside loops
                        if st.button("Done", key=f"btn_{c['id']}"): 
                            mark_challenge_completed(username, c['id'])
                            st.rerun()
                    else: 
                        st.markdown("<div style='text-align:center; font-size:1.5rem;'>✅</div>", unsafe_allow_html=True)

    elif page == "🏆 Leaderboard":
        st.title("🏆 Leaderboard")
        pipeline = [{"$match": {"completed": True}}, {"$group": {"_id": "$username", "total_xp": {"$sum": "$xp"}}}, {"$sort": {"total_xp": -1}}, {"$limit": 5}]
        leaders = list(challenges_col.aggregate(pipeline))
        for i, l in enumerate(leaders):
            u_name = users_col.find_one({"username": l['_id']}).get('name', l['_id'])
            medal = ["🥇","🥈","🥉"][i] if i<3 else f"{i+1}."
            st.markdown(f"""<div class="glass-card" style="display:flex;align-items:center;padding:15px;"><div style="font-size:24px;margin-right:20px;">{medal}</div><div style="flex-grow:1;"><h3 style="margin:0;">{u_name}</h3><p style="margin:0;color:#666 !important;">Level {get_level(l['total_xp'])}</p></div><div class="metric-value" style="font-size:24px;">{l['total_xp']} XP</div></div>""", unsafe_allow_html=True)

    elif page == "⚙️ Settings":
        # New Styled Header for Settings
        st.markdown(f"""
        <div class="settings-header">
            <h1>⚙️ Profile Settings</h1>
            <p>Manage your account, update targets, and track your progress.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("👤 Personal Details")
        with st.form("prof"):
            c1, c2 = st.columns(2)
            with c1: new_n = st.text_input("Full Name", user_profile.get('name'))
            with c2: new_t = st.slider("Target Band Score", 5.0, 9.0, float(user_profile.get('target_score', 7.5)))
            
            if st.form_submit_button("Update Profile", type="primary"):
                users_col.update_one({"username": username}, {"$set": {"name": new_n, "target_score": new_t}})
                st.success("Profile updated successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📝 Add Mock Test Score")
        
        # Helper function for IELTS rounding logic
        def calculate_overall(l, r, w, s):
            avg = (l + r + w + s) / 4
            decimal = avg - int(avg)
            if decimal < 0.25: return int(avg)
            elif decimal < 0.75: return int(avg) + 0.5
            else: return int(avg) + 1.0

        with st.form("add_s"):
            d_date = st.date_input("Test Date")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: l_score = st.number_input("Listening", 0.0, 9.0, 6.0, step=0.5)
            with c2: r_score = st.number_input("Reading", 0.0, 9.0, 6.0, step=0.5)
            with c3: w_score = st.number_input("Writing", 0.0, 9.0, 6.0, step=0.5)
            with c4: s_score = st.number_input("Speaking", 0.0, 9.0, 6.0, step=0.5)
            
            if st.form_submit_button("Save Score", type="primary"):
                final_overall = calculate_overall(l_score, r_score, w_score, s_score)
                scores_col.insert_one({
                    "username": username,
                    "date": d_date.strftime("%Y-%m-%d"),
                    "Listening": l_score, "Reading": r_score, "Writing": w_score, "Speaking": s_score,
                    "Overall": final_overall
                })
                st.success(f"Score Saved! Your Calculated Band: {final_overall}")
                st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
