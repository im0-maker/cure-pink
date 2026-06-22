import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client, Client

# 1. Supabaseの接続設定（自分のプロジェクトの情報を入れます）
SUPABASE_URL = "あなたのSUPABASE_URL"
SUPABASE_KEY = "あなたのSUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# アプリのタイトルとデザイン設定
st.set_page_config(page_title="Cure Pink MVP", page_icon="🌸")
st.title("🌸 Cure Pink (キュアピンク)")
st.subheader("大学生向け食習慣化サポートMVP")

# --- 機能1: 朝食時間からの起床時間逆算ロジック ---
st.info("💡 明日のスケジュールから最適な起床時間を逆算します。")

# 翌日の予定開始時間を選択
class_time = st.time_input("明日の1限 or 最初の予定の開始時刻", datetime.strptime("08:50", "%H:%M").time())
# 通学・準備時間（固定90分）
prep_transport_min = 90
# 死守すべき朝食時間（固定25分）
breakfast_min = 25

# 逆算の計算ロジック
total_subtract_min = prep_transport_min + breakfast_min
dummy_date = datetime.combine(datetime.today(), class_time)
calculated_wakeup_time = dummy_date - timedelta(minutes=total_subtract_min)

# 結果の提示
st.metric(
    label="推奨される起床時刻（朝食時間25分を強制確保）", 
    value=calculated_wakeup_time.strftime("%H:%M")
)
st.caption(f"※内訳: 移動準備 {prep_transport_min}分 ＋ 朝食摂取時間 {breakfast_min}分")

st.write("---")

# --- 機能2: 起き抜けワンタップ記録 ＆ Supabase連動 ---
st.subheader("☀️ 朝のミッションチェック")

col1, col2 = st.columns(2)

with col1:
    if st.button("☀️ すっきり起床した！", use_container_width=True):
        # Supabaseへログデータを挿入
        data, count = supabase.table("habit_logs").insert({
            "action_type": "wakeup"
        }).execute()
        st.success("起床ログをSupabaseに保存しました！")

with col2:
    if st.button("🍚 朝ごはんを食べた！", use_container_width=True):
        # Supabaseへログデータを挿入
        data, count = supabase.table("habit_logs").insert({
            "action_type": "breakfast"
        }).execute()
        st.success("朝食ログをSupabaseに保存しました！")

st.write("---")

# --- 機能3: 将来のロボット連携（バーチャルシミュレーター） ---
st.subheader("🤖 将来の卓上ロボットの反応（シミュレーション）")

# Supabaseから最新のログを取得してロボットの表情を変える疑似ロジック
try:
    response = supabase.table("habit_logs").select("*").order("created_at", desc=True).limit(1).execute()
    latest_log = response.data[0] if response.data else None
    
    if latest_log and latest_log["action_type"] == "breakfast":
        st.success("🤖 ロボットの表情: **(* 抜 刻 *)**")
        st.code("「すごーい！あさごはんバッチリだね！今日も1日ハッピー！」")
    elif latest_log and latest_log["action_type"] == "wakeup":
        st.warning("🤖 ロボットの表情: **( •̀ ω •́ )✧**")
        st.code("「おきたね！つぎは25分間、しっかり朝ごはんを食べよう！」")
    else:
        st.error("🤖 ロボットの表情: **( ˘ω˘ )**")
        st.code("「...おきてる？あさごはんの じかんだよ」")
except Exception as e:
    # データベース未接続時のデフォルト表示
    st.error("🤖 ロボットの表情: **( ˘ω˘ )**")
    st.code("「...おきてる？あさごはんの じかんだよ」")