import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("安定値ガチャシミュレーター")

# --- 初期化 ---
if "dataset" not in st.session_state:
    st.session_state.dataset = []

# --- フォーム（追加） ---
with st.form("atk_form", clear_on_submit=False):
    # 1行目: 通常ダメージ
    row1 = st.columns(2)
    normal_min = row1[0].number_input(
        "通常ダメージ下限", min_value=0, value=st.session_state.get("normal_min", 1000), key="normal_min"
    )
    normal_max = row1[1].number_input(
        "通常ダメージ上限", min_value=0, value=st.session_state.get("normal_max", 2000), key="normal_max"
    )

    # 2行目: 会心ダメージ
    row2 = st.columns(2)
    crit_min = row2[0].number_input(
        "会心ダメージ下限", min_value=0, value=st.session_state.get("crit_min", 2000), key="crit_min"
    )
    crit_max = row2[1].number_input(
        "会心ダメージ上限", min_value=0, value=st.session_state.get("crit_max", 4000), key="crit_max"
    )

    # 3行目: 会心確率とヒット数
    row3 = st.columns(2)
    crit_rate = row3[0].number_input(
        "会心確率(%)", min_value=0.0, max_value=100.0, value=st.session_state.get("crit_rate", 50.0), key="crit_rate"
    )
    hits = row3[1].number_input(
        "ヒット数", min_value=1, value=st.session_state.get("hits", 1), step=1, key="hits"
    )

    # 4行目: 追加ボタン（中央配置・横幅いっぱい）
    btn_col1, btn_col2, btn_col3 = st.columns([1,2,1])
    with btn_col2:
        submitted = st.form_submit_button("追加", use_container_width=True)

    if submitted:
        # バリデーション
        if normal_min > normal_max:
            st.error("通常ダメージ下限は上限以下でなければなりません。")
        elif crit_min > crit_max:
            st.error("会心ダメージ下限は上限以下でなければなりません。")
        else:
            entry = {
                "normal_min": int(normal_min),
                "normal_max": int(normal_max),
                "crit_min": int(crit_min),
                "crit_max": int(crit_max),
                "crit_rate": float(crit_rate),
                "hits": int(hits)
            }
            st.session_state.dataset.append(entry)
            st.success("攻撃パターンを追加しました")

# --- 攻撃パターン一覧 ---
st.subheader("攻撃パターン一覧")

if st.session_state.dataset:
    # ヘッダー行
    header_cols = st.columns([0.1, 1, 1, 1, 1, 0.7, 0.7, 0.3])
    headers = ["No.", "通常下限", "通常上限", "会心下限", "会心上限", "会心率(%)", "ヒット数", ""]
    for c, h in zip(header_cols, headers):
        c.markdown(f"<div style='text-align:center;font-weight:bold'>{h}</div>", unsafe_allow_html=True)

    # 各行
    for i, entry in enumerate(st.session_state.dataset):
        cols = st.columns([0.1, 1, 1, 1, 1, 0.7, 0.7, 0.3], gap=None)
        cols[0].markdown(f"<div style='text-align:center'>{i+1}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='text-align:center'>{int(entry['normal_min'])}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='text-align:center'>{int(entry['normal_max'])}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div style='text-align:center'>{int(entry['crit_min'])}</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div style='text-align:center'>{int(entry['crit_max'])}</div>", unsafe_allow_html=True)
        cols[5].markdown(f"<div style='text-align:center'>{entry['crit_rate']:.2f}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"<div style='text-align:center'>{int(entry['hits'])}</div>", unsafe_allow_html=True)
        if cols[7].button("削除", key=f"del_row_{i}"):
            st.session_state.dataset.pop(i)
            st.success(f"行 {i+1} を削除しました。")
            st.rerun()
else:
    st.write("まだ攻撃パターンがありません。")

# --- シミュレーション設定 ---
st.subheader("シミュレーション設定")
target_damage = st.number_input("目標ダメージ", min_value=0, value=7000000)
num_trials = st.number_input("試行回数", min_value=1000, value=100000, step=1000)

# --- シミュレーション実行 ---
if st.button("シミュレーション開始"):
    if not st.session_state.dataset:
        st.warning("攻撃パターンを1件以上追加してください。")
    else:
        progress_bar = st.progress(0)
        result_placeholder = st.empty()
        count_exceed = 0
        batch_size = 1000

        for batch_start in range(0, num_trials, batch_size):
            batch_end = min(batch_start + batch_size, num_trials)
            batch_count = batch_end - batch_start

            for _ in range(batch_count):
                total_damage = 0
                for atk in st.session_state.dataset:
                    crit_prob = atk["crit_rate"] / 100
                    for _ in range(int(atk["hits"])):
                        is_crit = np.random.rand() < crit_prob
                        if is_crit:
                            dmg = np.random.uniform(atk["crit_min"], atk["crit_max"])
                        else:
                            dmg = np.random.uniform(atk["normal_min"], atk["normal_max"])
                        total_damage += dmg

                if total_damage > target_damage:
                    count_exceed += 1

            progress_bar.progress(batch_end / num_trials)
            prob_so_far = count_exceed / batch_end
            result_placeholder.write(f"現在の成功確率: {prob_so_far*100:.2f}% （{batch_end}試行）")

        final_prob = count_exceed / num_trials
        st.success(f"最終結果: {final_prob*100:.2f}%")
