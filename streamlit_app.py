import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 페이지 설정
st.set_page_config(
    page_title="오피스 상권 카페 창업 전략",
    page_icon="☕",
    layout="wide"
)

# 스타일링 (Premium Dark)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .main-title { font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg, #FFB74D, #FF8A65); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-card { background-color: #1E2227; padding: 1.2rem; border-radius: 12px; border: 1px solid #30363D; text-align: center; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_master_data_v12():
    # v12: 사용자 정의 6대 지표(Opportunity Score, 저가 점유율, 피크 시간, 주중 매출, 경쟁 강도, 상권 변화) 반영
    path = 'dashboard_master_v12.parquet'
    if os.path.exists(path):
        df = pd.read_parquet(path)
        return df
    return pd.DataFrame()

df = load_master_data_v12()
total_dongs = len(df)

if df.empty:
    st.error("데이터(v12)를 찾을 수 없습니다. 파일 경로를 확인해주세요: dashboard_master_v12.parquet")
    st.stop()

# 사이드바
with st.sidebar:
    st.header("🔍 필터링 설정")
    # 평일 매출 비중 필터
    min_weekday_ratio = st.slider(
        "최소 평일 매출 비중 (%)",
        min_value=0,
        max_value=100,
        value=70,  # 기본값 70% (오피스 타겟)
        help="전체 매출 중 평일(월~금) 매출이 차지하는 최소 비중입니다. (Top 10 목록에만 적용)"
    ) / 100.0

    st.markdown("---")
    st.header("🏢 상권 선택")
    
    # 전체 행정동 목록 (필터 무관)
    all_dong_list = sorted(df['표준_행정동_명'].unique())
    target_dong = st.selectbox("분석 대상 행정동 (전체 검색 가능)", all_dong_list)
    
    st.markdown("---")
    st.subheader(f"🏆 타겟팅 Top 10 (평일 {min_weekday_ratio:.0%}+)")
    
    # Top 10은 필터링된 데이터로 표시
    filtered_df = df[df['평일_매출_비중'] >= min_weekday_ratio]
    display_top10 = filtered_df.nsmallest(10, '전체_순위')[['전체_순위', '표준_행정동_명']] if not filtered_df.empty else pd.DataFrame()
    
    if not display_top10.empty:
        for _, row in display_top10.iterrows():
            st.write(f"**{row['전체_순위']}위** : {row['표준_행정동_명']}")
    else:
        st.write("해당 조건의 상권이 없습니다.")

st.markdown('<div class="main-title">☕ 저가카페 창업 스카우터 v12</div>', unsafe_allow_html=True)
st.markdown(f'<div style="color: #9E9E9E; margin-bottom: 20px;">서울시 {total_dongs}개 행정동 분석 기반 (사용자 정의 6대 핵심 지표 반영)</div>', unsafe_allow_html=True)

# 데이터 필터링 (정확한 매칭 확인)
selected_df = df[df['표준_행정동_명'] == target_dong]
if selected_df.empty:
    st.warning(f"'{target_dong}'에 대한 매칭 데이터를 찾을 수 없습니다.")
    st.stop()
selected_row = selected_df.iloc[0]

# 오피스 상권 적합 여부 (80% 기준)
is_office_optimal = selected_row['주중_매출_비율'] >= 0.80
office_badge = "✅ 오피스 최적 상권 (주중 80%+)" if is_office_optimal else "⚠️ 주중 매출 비중 80% 미만"
badge_color = "#81C784" if is_office_optimal else "#E57373"

st.markdown(f'<div style="background-color: {badge_color}22; padding: 10px; border-radius: 8px; border: 1px solid {badge_color}; color: {badge_color}; text-align: center; margin-bottom: 20px; font-weight: bold;">{office_badge}</div>', unsafe_allow_html=True)

# KPI
c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
with c1: st.markdown(f'<div class="metric-card"><small>종합 순위</small><br><b style="font-size:1.6rem; color:#FFB74D;">{selected_row["전체_순위"]}위</b><br><small>/{total_dongs}</small></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><small>Opp. Score</small><br><b style="font-size:1.6rem; color:#FFD54F;">{selected_row["Opportunity_Score_v12"]:.1f}</b></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card"><small>저가 점유율</small><br><b style="font-size:1.6rem; color:#81C784;">{selected_row["저가_점유율_v12"]:.1%}</b></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card"><small>피크 시간</small><br><b style="font-size:1.6rem; color:#64B5F6;">{selected_row["피크_시간_매출_비율_v12"]:.1%}</b></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="metric-card"><small>주중 매출</small><br><b style="font-size:1.6rem;">{selected_row["주중_매출_비율_v12"]:.1%}</b></div>', unsafe_allow_html=True)
with c6: st.markdown(f'<div class="metric-card"><small>경쟁 강도</small><br><b style="font-size:1.6rem; color:#BA68C8;">{selected_row["경쟁_강도_v12"]:.2f}</b></div>', unsafe_allow_html=True)
with c7: st.markdown(f'<div class="metric-card"><small>상권 점수</small><br><b style="font-size:1.6rem; color:#FB8C00;">{selected_row["상권변화_점수_v12"]:.0f}점</b></div>', unsafe_allow_html=True)
with c8: st.markdown(f'<div class="metric-card"><small>저가 침투율</small><br><b style="font-size:1.6rem;">{selected_row["저가_침투율"]:.1%}</b></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 메인 콘텐츠
tab_v9, tab1, tab2, tab3, tab4, tab5 = st.tabs(["⭐ 6대 핵심 지표 분석", "🚀 상권 리듬 분석", "📊 지수 산출 근거", "🔵 수요/공급 매트릭스", "📈 상권 인사이트", "📜 Top 10 리스트"])

with tab_v9:
    st.subheader("🎯 v12 사용자 정의 6대 지표 분석")
    st.markdown(f"**{target_dong}**의 전략적 창업 기회를 6가지 핵심 산식으로 정밀 평가합니다.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("**1. 수요 대비 공급 기회**")
        st.metric("Opportunity Score", f"{selected_row['Opportunity_Score_v12']:.1f}")
        st.caption("종사자 수 ÷ 저가카페 매장 수 (높을수록 좋음)")
        
        st.metric("저가카페 프랜차이즈 점유율", f"{selected_row['저가_점유율_v12']:.1%}")
        st.caption("저가카페 수 ÷ 전체 카페 수 (낮을수록 블루오션)")

    with col_b:
        st.info("**2. 오피스 타겟 집중도**")
        st.metric("피크(수혈) 시간 매출 비율", f"{selected_row['피크_시간_매출_비율_v12']:.1%}")
        st.caption("06-14시 매출 비중 (오피스타겟 중요 지표)")
        
        st.metric("주중 매출 비율", f"{selected_row['주중_매출_비율_v12']:.1%}")
        st.caption("주중 매출 ÷ (주중 + 주말)")

    with col_c:
        st.info("**3. 경쟁 환경 및 성장성**")
        st.metric("경쟁 강도 (지리적 보정)", f"{selected_row['경쟁_강도_v12']:.2f}")
        st.caption("지리적 밀집도를 반영한 경쟁 수준 (낮을수록 유리)")
        
        score_val = selected_row['상권변화_점수_v12']
        score_name = ['worst', '축소(1)', '정체(2)', '확장(3)', '다이나믹(4)'][int(score_val)]
        st.metric("상권 변화 지표 점수", score_name)
        st.caption("성장성: 다이나믹(4) -> 축소(1)")

with tab1:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("⏰ 시간대별 매출 리듬")
        time_labels = ['00-06시', '06-11시', '11-14시', '14-17시', '17-21시', '21-24시']
        time_mapping = ['00~06', '06~11', '11~14', '14~17', '17~21', '21~24']
        time_values = [selected_row.get(f'시간대_{m}_매출_금액', 0) for m in time_mapping]
        fig_time = px.line(x=time_labels, y=time_values, markers=True, line_shape='spline')
        fig_time.update_traces(line_color='#FFB74D', line_width=4)
        fig_time.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_time, use_container_width=True)
    with col_t2:
        st.subheader("📅 요일별 수요 집중도")
        day_labels = ['월', '화', '수', '목', '금', '토', '일']
        day_values = [selected_row.get(f'{d}요일_매출_금액', 0) for d in day_labels]
        fig_day = px.bar(x=day_labels, y=day_values, color=day_values, color_continuous_scale='Oranges')
        fig_day.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_day, use_container_width=True)

with tab2:
    st.subheader("🎯 기회 지수(Opportunity Index) 상세 분석")
    st.caption("기회 지수는 아래 4가지 핵심 요소의 서울시 내 상대적 위치(백분위)를 종합하여 산출됩니다.")
    
    # 레이더 차트 데이터 (v12 사용자 정의 핵심 5요소)
    categories = ['Opp. Score', '저가 점유율(낮음)', '피크 시간', '주중 매출', '상권 점수']
    
    values = [
        selected_row.get('Opportunity_Score_v12', 0.5) / df['Opportunity_Score_v12'].max() * 100,
        (1 - selected_row.get('저가_점유율_v12', 0.5)) * 100, # 낮을수록 좋음
        selected_row.get('피크_시간_매출_비율_v12', 0.5) * 100,
        selected_row.get('주중_매출_비율_v12', 0.5) * 100,
        (selected_row.get('상권변화_점수_v12', 2) / 4) * 100
    ]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(255, 183, 77, 0.3)',
        line_color='#FFB74D',
        name=target_dong
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='#9E9E9E'),
            bgcolor='rgba(0,0,0,0)',
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        height=500
    )
    
    c_r1, c_r2 = st.columns([1.5, 1])
    with c_r1:
        st.plotly_chart(fig_radar, use_container_width=True)
    with c_r2:
        st.markdown(f"""
        ### 🔍 {target_dong} v12 분석 리포트
        - **Opportunity Score**: {selected_row['Opportunity_Score_v12']:.1f}
        - **저가카페 점유율**: {selected_row['저가_점유율_v12']:.1%}
        - **피크 시간 매출**: {selected_row['피크_시간_매출_비율_v12']:.1%}
        - **주중 매출 비중**: {selected_row['주중_매출_비율_v12']:.1%}
        - **경쟁 강도 점수**: {selected_row['경쟁_강도_v12']:.2f}
        - **상권 활력도**: {score_name}
        
        ---
        ### 📐 지표별 계산식
        1. **Opp. Score**: `종사자수 ÷ 저가카페 매장수`
        2. **저가 점유율**: `저가카페수 ÷ 전체카페수`
        3. **피크 시간**: `(06~14시 매출) ÷ 월 전체 매출`
        4. **주중 매출**: `주중 매출 ÷ (주중 + 주말 매출)`
        5. **경쟁 강도**: `전체 카페 수 ÷ 총 종사자 수`
        6. **상권 점수**: `다이나믹(4) / 확장(3) / 정체(2) / 축소(1)`

        ---
        **[v12 종합 지수 가중치]**
        `Opp(30%) + 피크(20%) + 주중(20%) + 상권(10%) + 저가비율(10%) + 경쟁(10%)`
        """)

with tab3:
    st.subheader("🔵 블로오션 진단 (수요 vs 공급)")
    fig_scatter = px.scatter(df, x='카페_수', y='총_종사자수', size='창업_기회_지수', color='창업_기회_지수', 
                             hover_name='표준_행정동_명', color_continuous_scale='Viridis')
    fig_scatter.add_trace(go.Scatter(x=[selected_row['카페_수']], y=[selected_row['총_종사자수']],
                                     mode='markers+text', text=[f"★ {target_dong}"], 
                                     textposition="top center", marker=dict(color='red', size=15)))
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', font_color='#E0E0E0',
                              xaxis_title="지역 내 전체 카페 수 (공급)", yaxis_title="지역 내 총 종사자 수 (수요)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.subheader("📊 유동인구 및 상권 안정성 상세 분석")
    col_v8_1, col_v8_2 = st.columns(2)
    
    with col_v8_1:
        st.write("👥 **연령대별 유동인구 분포**")
        age_labels = ['10대', '20대', '30대', '40대', '50대', '60대+']
        age_values = [selected_row.get(f'연령대_{i}_유동인구_수', 0) for i in ['10', '20', '30', '40', '50', '60_이상']]
        fig_age = px.pie(names=age_labels, values=age_values, hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_age.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0', height=350)
        st.plotly_chart(fig_age, use_container_width=True)
        
        gender_labels = ['남성', '여성']
        gender_values = [selected_row.get('남성_유동인구_수', 0), selected_row.get('여성_유동인구_수', 0)]
        fig_gender = px.bar(x=gender_labels, y=gender_values, color=gender_labels, title="성별 유동인구")
        fig_gender.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0', height=250)
        st.plotly_chart(fig_gender, use_container_width=True)

    with col_v8_2:
        st.write("🛡️ **상권 안정성 (영업 개월 수)**")
        months_labels = ['상권 평균 운영 개월', '상권 평균 폐업 개월']
        months_values = [selected_row.get('서울_운영_영업_개월_평균', 0), selected_row.get('서울_폐업_영업_개월_평균', 0)]
        fig_months = px.bar(x=months_labels, y=months_values, color=months_labels, color_discrete_sequence=['#81C784', '#E57373'])
        fig_months.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0', height=350)
        st.plotly_chart(fig_months, use_container_width=True)
        
        st.markdown(f"""
        **추가 핵심 지표:**
        - **점포 개업률**: {selected_row.get('개업_율', 0)}%
        - **점포 폐업률**: {selected_row.get('폐업_률', 0)}%
        - **프랜차이즈 비중**: {selected_row.get('프랜차이즈_점포_수', 0) / selected_row.get('점포_수', 1):.1%}
        """)
        st.caption("※ 상권분석서비스 2024년 최신 필터링 데이터 기준")

with tab5:
    st.subheader("📜 오피스 상권 유망 지역 Top 10")
    top10_full = df.nsmallest(10, '전체_순위')[['전체_순위', '표준_행정동_명', '창업_기회_지수', 'Opportunity_Score_Raw', '주중_매출_비율', '상권_변화_지표_명']]
    top10_full.columns = ['순위', '행정동', '기회 지수', 'Opp. Score', '주중 매출 비율', '상권 상태']
    st.dataframe(top10_full.style.format({'기회 지수': '{:.1f}', 'Opp. Score': '{:.1f}', '주중 매출 비율': '{:.1%}'}).background_gradient(subset=['기회 지수'], cmap='Oranges'), use_container_width=True)

st.markdown("---")
st.info(f"💡 **분석 결과**: **{target_dong}**은 서울시 {total_dongs}개 상권 중 기회 지수 **{selected_row['전체_순위']}위**를 기록한 핵심 요지입니다.")
