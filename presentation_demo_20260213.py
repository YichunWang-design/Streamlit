import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import plotly.express as px


# --- 1. サンプルデータの生成関数 ---
@st.cache_data
def generate_sample_data():
    categories = {
        "家具": ["椅子", "テーブル", "収納家具", "照明"],
        "事務用品": ["紙", "筆記具", "バインダー", "封筒"],
        "家電": ["スマホ", "ノートPC", "周辺機器", "電話機"]
    }
    
    products = ["製品A", "製品B", "製品C", "製品D", "製品E"]
    data = []
    start_date = datetime.date(2024, 1, 1)
    
    for _ in range(500):
        current_date = start_date + datetime.timedelta(days=random.randint(0, 730))
        cat = random.choice(list(categories.keys()))
        sub_cat = random.choice(categories[cat])
        prod = f"{sub_cat} - {random.choice(products)}"
        
        # 売上の計算
        base_price = {"家具": 50000, "事務用品": 1000, "家電": 80000}
        sales = base_price[cat] * random.uniform(0.5, 1.5)
        
        data.append({
            "オーダー日": current_date,
            "年月": f"{current_date.year}/{current_date.month}",
            "年": current_date.year,
            "月": current_date.month,
            "カテゴリ": cat,
            "サブカテゴリ": sub_cat,
            "商品": prod,
            "売上": round(sales, 0)
        })
    
    df = pd.DataFrame(data).sort_values("オーダー日").reset_index(drop=True)
    return df


# --- 2. グラフ描画・イベント取得用の関数 ---
def draw_line_chart(df, interactive_mode, use_expander):
    """折れ線グラフを描画し、選択イベントを返す"""
    
    trend_df = df.groupby(["年", "月", "年月"])["売上"].sum().reset_index().sort_values(["年", "月"])
    
    fig = px.line(
        trend_df,
        x="年月",
        y="売上",
        markers=True,
        labels={"売上": "売上 (円)"},
        template="plotly_white"
    )
    fig.update_traces(
        hovertemplate="<b>年月:</b> %{x}<br><b>売上:</b> %{y:,.0f} 円"
    )
    fig.update_layout(
        yaxis=dict(tickformat=",.0f"),
        xaxis=dict(type='category', tickangle=-90),
        height=300,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    # レイアウトの工夫がONならexpanderを使う
    if use_expander:
        container = st.expander("折れ線グラフを表示/非表示", expanded=True)
    else:
        container = st.container()
        
    with container:
        if not interactive_mode:
            # インタラクティブOFFなら静的描画して終了
            st.plotly_chart(
                fig,
                key="line_chart_static_" + str(st.session_state.get("key_chart_count", 0)),
                use_container_width=True
            )
            return None
        
        else:
            # 返り値としてイベントデータを取得
            selection = st.plotly_chart(
                fig,
                on_select="rerun",
                selection_mode="points",
                key="line_chart_interactive_" + str(st.session_state.get("key_chart_count", 0)),
                use_container_width=True
            )
            if not selection or not selection.get("selection") or not selection["selection"].get("points"):
                line_selected = None
            else:
                line_selected = selection["selection"]["points"][0]["x"]
    
            return line_selected


def draw_bar_chart(df, interactive_mode, use_expander):
    """棒グラフを描画し、選択イベントを返す"""
    
    cat_sum_df = df.groupby("カテゴリ")["売上"].sum().reset_index()
    
    fig = px.bar(
        cat_sum_df,
        x="カテゴリ",
        y="売上",
        color="売上",
        color_continuous_scale="Blues",
        labels={"売上": "売上 (円)"},
        template="plotly_white"
    )
    fig.update_traces(
        hovertemplate="<b>カテゴリ:</b> %{x}<br><b>売上:</b> %{y:,.0f} 円",
        texttemplate="%{y:,.0f}",
        textposition="inside",
        textfont_size=16
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(tickformat=",.0f"),
        height=300,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    if use_expander:
        container = st.expander("棒グラフを表示/非表示", expanded=True)
    else:
        container = st.container()
        
    with container:
        if not interactive_mode:
            st.plotly_chart(
                fig, 
                key="bar_chart_static_" + str(st.session_state.get("key_chart_count", 0)),
                use_container_width=True
            )
            return None
        else:
            selection = st.plotly_chart(
                fig, 
                on_select="rerun", 
                selection_mode="points",
                key="bar_chart_interactive_" + str(st.session_state.get("key_chart_count", 0)),
                use_container_width=True
            )
            if not selection or not selection.get("selection") or not selection["selection"].get("points"):
                bar_selected = None
            else:
                bar_selected = selection["selection"]["points"][0]["x"]
            
            return bar_selected


# --- 3. メイン画面の構築 ---
def main():
    st.set_page_config(page_title="Streamlit Sales Dashboard", layout="wide")
    
    # データの読み込み
    df = generate_sample_data()

    # --- サイドバー (フィルター機能) ---
    st.sidebar.header("🔍 フィルター設定")
    
    all_categories = sorted(df["カテゴリ"].unique())
    all_sub_categories = sorted(df["サブカテゴリ"].unique())

    # セッションステートの初期化
    if "cat_sel" not in st.session_state:
        st.session_state["cat_sel"] = all_categories
    if "sub_sel" not in st.session_state:
        st.session_state["sub_sel"] = all_sub_categories
    if "key_chart_count" not in st.session_state:
        st.session_state["key_chart_count"] = 0

    def reset_filters():
        st.session_state["cat_sel"] = all_categories
        st.session_state["sub_sel"] = all_sub_categories
        st.session_state["key_chart_count"] += 1  # グラフのキーを変えて強制再描画・選択解除
        
    st.sidebar.button("フィルターをリセット", on_click=reset_filters)

    selected_cat_sidebar = st.sidebar.multiselect("カテゴリ", options=all_categories, key="cat_sel")

    if selected_cat_sidebar:
        available_sub_cats = sorted(df[df["カテゴリ"].isin(selected_cat_sidebar)]["サブカテゴリ"].unique())
    else:
        available_sub_cats = []

    valid_sub_sel = [s for s in st.session_state["sub_sel"] if s in available_sub_cats]
    if len(valid_sub_sel) != len(st.session_state["sub_sel"]):
        st.session_state["sub_sel"] = valid_sub_sel

    selected_sub_cat_sidebar = st.sidebar.multiselect("サブカテゴリ", options=available_sub_cats, key="sub_sel")

    # --- 工夫ポイント設定 (サイドバー下部) ---
    st.sidebar.divider()
    st.sidebar.subheader("💡 工夫ポイント")
    feat_layout = st.sidebar.checkbox("① レイアウトの工夫")
    feat_aesthetics = st.sidebar.checkbox("② 見た目の工夫")
    feat_interactive = st.sidebar.checkbox("③ インタラクティブ性の工夫")

    # --- スタイリング適用 ---
    if feat_aesthetics:
        st.markdown("""
            <style>
            .main-title {
                text-align: center;
                background-color: #e3f2fd;
                color: #0e1117;
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 35px;
                font-family: 'Urbanist', 'Noto Sans JP', sans-serif;
                border: none;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            [data-testid="stMetric"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #ffffff 0%, #f1f8ff 100%);
                border: none !important;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(26, 115, 232, 0.08);
                padding: 25px !important;
                transition: all 0.3s ease;
            }
            [data-testid="stMetric"]:hover {
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(26, 115, 232, 0.15);
            }
            [data-testid="stMetricLabel"] {
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                color: #5f6368 !important;
                margin-bottom: 10px !important;
            }
            [data-testid="stMetricValue"] {
                font-size: 2.3rem !important;
                font-weight: 800 !important;
                color: #1a73e8 !important;
            }
            </style>
        """, unsafe_allow_html=True)

    # --- タイトル描画 ---
    title_placeholder = st.empty()
    if feat_aesthetics:
        title_placeholder.markdown('<h1 class="main-title">売上分析ダッシュボード</h1>', unsafe_allow_html=True)
    else:
        title_placeholder.title("売上分析ダッシュボード")

    # --- データフィルタリング準備 ---
    # サイドバーによる基礎フィルタ
    base_filtered_df = df[df["カテゴリ"].isin(selected_cat_sidebar) & df["サブカテゴリ"].isin(selected_sub_cat_sidebar)]

    # --- メインコンテンツの描画 ---
    
    # 指標を後から書き込むためのコンテナを先に確保
    text_container = st.container()
    st.divider()
    
    # コンテナ設定
    main_container = st.container(height=720 if feat_layout else "content", border=False)

    line_selected = None
    bar_selected = None
    
    # ここから順次フィルタリングしていく
    final_filtered_df = base_filtered_df.copy()

    with main_container:
        # グラフエリア
        left_col, right_col = st.columns([2, 1], gap="large")

        with left_col:
            st.subheader("📈 月別売上推移")
            if not base_filtered_df.empty:
                # 戻り値でイベント取得
                line_selected = draw_line_chart(base_filtered_df, feat_interactive, feat_layout)
                
                # 折れ線グラフの選択を反映
                if line_selected:
                    final_filtered_df = final_filtered_df[final_filtered_df["年月"] == line_selected]
            else:
                st.info("データがありません。")

        with right_col:
            st.subheader("📊 カテゴリ別売上")
            if not final_filtered_df.empty:
                # 折れ線で絞り込まれたデータを渡して描画
                bar_selected = draw_bar_chart(final_filtered_df, feat_interactive, feat_layout)
                
                # 棒グラフの選択をさらに反映
                if bar_selected:
                    final_filtered_df = final_filtered_df[final_filtered_df["カテゴリ"] == bar_selected]
            else:
                st.info("データがありません。")
                
        # --- 指標表示 ---
        # グラフ描画後に、全て絞り込まれた(final_filtered_df)状態の数値を上部のコンテナに出力
        with text_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("**総売上**", f"{final_filtered_df['売上'].sum():,.0f} 円")
            with col2:
                st.metric("**オーダー数**", f"{len(final_filtered_df):,.0f} 件")
            with col3:
                avg_val = final_filtered_df['売上'].mean() if not final_filtered_df.empty else 0
                st.metric("**平均単価**", f"{avg_val:,.0f} 円")

        # --- フィルタ通知と詳細表 ---
        if feat_interactive and (line_selected or bar_selected):
            msgs = []
            if line_selected:
                msgs.append(f"年月({line_selected})")
            if bar_selected:
                msgs.append(f"カテゴリ({bar_selected})")
                
            st.toast(f"フィルタ適用中: " + " / ".join(msgs))
            st.info(f"💡 {' と '.join(msgs)} のデータがグラフ選択により絞り込まれています。解除するには選択データを再度クリックしてください。")

        st.subheader("📋 詳細表")
        display_df = final_filtered_df[["オーダー日", "カテゴリ", "サブカテゴリ", "商品", "売上"]].copy()
        # styled_df = display_df.style.background_gradient(cmap='Blues', subset=['売上']).format({'売上': '{:,.0f} 円'})
        
        st.dataframe(display_df, hide_index=True, height=600)
        
        # 下部の余白
        st.html("<div style='height:1000px;'></div>")


if __name__ == "__main__":
    main()
