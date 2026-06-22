import streamlit as st
from datetime import datetime, timedelta
import pandas as pd  # 📊 グラフ用のライブラリ
from supabase import create_client, Client

SUPABASE_URL = "https://egvybngkywdppayoakop.supabase.co"
SUPABASE_KEY = "sb_publishable_xza6vSsmnhJoqD3x8jVflg_Z5B5sqoR"

# データベースに接続を試みる
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    db_connected = True
except Exception as e:
    db_connected = False

# アプリのタイトルとデザイン設定
st.set_page_config(page_title="Cure Pink MVP", page_icon="🌸")
st.title("🌸 Cure Pink (キュアピンク)")
st.subheader("大学生向け食習慣化サポートMVP")

if not db_connected:
    st.error("⚠️ Supabaseへの接続に失敗しました。")

st.write("---")

# --- 機能1: 朝食時間からの起床時間逆算ロジック ---
st.markdown("### ⏰ 1. スケジュールから起床時間を逆算")

class_time = st.time_input(
    "明日の講義や最初の予定の開始時刻", 
    datetime.strptime("08:50", "%H:%M").time(),
    step=600
)

st.write("👇 あなたの予定に合わせて時間を調整してください")
prep_transport_min = st.slider("🏠 移動・準備にかかる時間（分）", min_value=10, max_value=180, value=90, step=5)
breakfast_min = st.slider("🍚 朝食をしっかり食べる時間（分）", min_value=10, max_value=60, value=25, step=5)

total_subtract_min = prep_transport_min + breakfast_min
dummy_date = datetime.combine(datetime.today(), class_time)
calculated_wakeup_time = dummy_date - timedelta(minutes=total_subtract_min)

st.metric(
    label=f"推奨される起床時刻（朝食時間 {breakfast_min} 分を自動で強制確保！）", 
    value=calculated_wakeup_time.strftime("%H:%M")
)
st.caption(f"（内訳：移動・準備 {prep_transport_min} 分 ＋ 朝食摂取時間 {breakfast_min} 分 ＝ 計 {total_subtract_min} 分逆算）")

st.write("---")

# --- 機能2: 朝のミッションチェック ＆ Supabase連動 ---
st.markdown("### ☀️ 2. 朝のミッションチェック")
st.caption("ボタンを押すと、クラウドデータベースにリアルタイムでデータが保存されます。")

col1, col2 = st.columns(2)

with col1:
    if st.button("❌ 朝ごはんを食べられなかった…", use_container_width=True):
        if db_connected:
            try:
                supabase.table("habit-logs").insert({"action_type": "skip"}).execute()
                st.warning(" 😭 記録を保存しました。次は食べられるように応援するね！")
                st.rerun()  # 📊 グラフを即座に更新するため
            except Exception as e:
                st.error(f"保存エラー: {e}")

with col2:
    if st.button("🍚 朝ごはんを食べた！", use_container_width=True):
        if db_connected:
            try:
                supabase.table("habit-logs").insert({"action_type": "breakfast"}).execute()
                st.success(f"🎉 朝食ログ（目標時間: {breakfast_min}分）をSupabaseに保存しました！")
                st.rerun()  # 📊 グラフを即座に更新するため
            except Exception as e:
                st.error(f"保存エラー: {e}")

st.write("---")

# --- 機能3: 将来のロボット連携（バーチャルシミュレーター） ---
st.markdown("### 🤖 3. 将来の卓上ロボットの反応")

latest_log = None
if db_connected:
    try:
        response = supabase.table("habit-logs").select("*").order("created_at", desc=True).limit(1).execute()
        latest_log = response.data[0] if response.data else None
        
        if latest_log and latest_log["action_type"] == "breakfast":
            st.success("🤖 ロボットの表情: **( ≧ ▽ ≦ )ノ✨**")
            st.code("「すごーい！あさごはんバッチリだね！今日も1日ハッピー！」")
        elif latest_log and latest_log["action_type"] == "skip":
            st.error("🤖 ロボットの表情: **( ； ω ； )**")
            st.code("「え〜ん、あさごはん食べられなかったの？エネルギー不足でバテないように気をつけてね…！」")
        else:
            st.error("🤖 ロボット: **( ˘ω˘ )**")
            st.code("「...おきてる？あさごはんの じかんだよ」")
    except Exception as e:
        st.error("🤖 ロボット: 「データがうまくよめないみたい…」")

st.write("---")

st.markdown("### 📊 4. 今週の習慣化記録（1週間のデータ）")
st.caption("Supabaseからデータを読み込んで、「食べた回数」と「食べられなかった回数」を自動で集計します。")

if db_connected:
    try:
        # 🛠️ 日付の形式エラーを回避するために、全件取得してからPython側で安全に集計する形に直しました！
        logs_response = supabase.table("habit-logs").select("action_type").execute()
        all_logs = logs_response.data
        
        # ログがある場合だけグラフを描く
        if all_logs:
            breakfast_count = sum(1 for log in all_logs if log["action_type"] == "breakfast")
            skip_count = sum(1 for log in all_logs if log["action_type"] == "skip")
            
            # グラフ用のデータ作成
            chart_data = pd.DataFrame({
                "状態": ["🍚 朝ごはんを食べた", "❌ 食べられなかった"],
                "回数": [breakfast_count, skip_count]
            })
            
            # 棒グラフを表示
            st.bar_chart(data=chart_data, x="状態", y="回数")
            
            # メッセージ提示
            st.info(f"✨ これまでに **{breakfast_count} 回** 朝ごはんを食べることができました！この調子で習慣化していこう！")
        else:
            st.info("💡 まだ記録がありません。上のボタンを押して最初の記録をスタートしよう！")
            
    except Exception as e:
        st.error(f"⚠️ グラフの集計中にエラーが発生しました: {e}")