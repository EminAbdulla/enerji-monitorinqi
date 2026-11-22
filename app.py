import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# SƏHİFƏ TƏNZİMLƏMƏLƏRİ
# ==========================================
st.set_page_config(
    page_title="Yaşıl Enerji Analitikası | Azərbaycan & Region",
    page_icon=":material/bolt:",
    layout="wide",
)

st.title(":material/bolt: Rəqəmsal Enerji Monitorinqi: Cənubi Qafqaz və Region")
st.markdown(
    "Açıq data (*Our World in Data*) əsasında elektrik istehsalında bərpa olunan enerjinin payı, "
    "Azərbaycanın yaşıl enerji xəritəsi, **Energetika Naziri simulyatoru** və **şəxsi karbon kalkulyatoru**."
)


# ==========================================
# AÇIQ DATANI YÜKLƏMƏK
# ==========================================
@st.cache_data
def load_data():
    url = (
        "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
    )
    df = pd.read_csv(url)
    target_countries = [
        "Azerbaijan",
        "Georgia",
        "Turkey",
        "Armenia",
        "Kazakhstan",
        "European Union (27)",
    ]
    df = df[(df["country"].isin(target_countries)) & (df["year"] >= 2000)]
    return df


with st.spinner("Açıq data bazası (Our World in Data) yüklənir..."):
    df = load_data()

# ==========================================
# YAN PANEL (FİLTRLƏR)
# ==========================================
st.sidebar.header(":material/tune: Analiz Parametrləri")

available_countries = [
    "Azerbaijan",
    "Georgia",
    "Turkey",
    "Armenia",
    "Kazakhstan",
    "European Union (27)",
]
selected_countries = st.sidebar.multiselect(
    "Müqayisə ediləcək ölkələr/regionlar:",
    options=available_countries,
    default=["Azerbaijan", "Georgia", "Turkey", "European Union (27)"],
)

if not selected_countries:
    st.warning(
        "Zəhmət olmasa yan paneldən ən azı bir ölkə seçin.", icon=":material/warning:"
    )
    st.stop()

max_year = int(df["year"].max())
year_range = st.sidebar.slider("İllər aralığı:", 2000, max_year, (2005, max_year))

filtered_df = df[
    (df["country"].isin(selected_countries))
    & (df["year"].between(year_range[0], year_range[1]))
]

# ==========================================
# ÜST KPI KARTLARI (AZƏRBAYCAN ÜZRƏ)
# ==========================================
az_df = (
    df[df["country"] == "Azerbaijan"]
    .dropna(subset=["renewables_share_elec"])
    .sort_values("year")
)
ge_df = (
    df[df["country"] == "Georgia"]
    .dropna(subset=["carbon_intensity_elec"])
    .sort_values("year")
)

az_latest_ci = 440.0
ge_latest_ci = 110.0

if len(az_df) >= 2:
    latest_az = az_df.iloc[-1]
    prev_az = az_df.iloc[-2]

    st.subheader(
        f":material/analytics: Azərbaycan: Əsas Göstəricilər ({int(latest_az['year'])})"
    )
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        ":material/eco: Bərpa Olunan Enerji Payı",
        f"{latest_az['renewables_share_elec']:.2f}%",
        f"{latest_az['renewables_share_elec'] - prev_az['renewables_share_elec']:+.2f}% (illik)",
    )
    col2.metric(
        ":material/local_fire_department: Fosil Yanacaq Payı",
        f"{latest_az['fossil_share_elec']:.2f}%",
        f"{latest_az['fossil_share_elec'] - prev_az['fossil_share_elec']:+.2f}%",
        delta_color="inverse",
    )
    solar_wind = (latest_az.get("solar_share_elec", 0) or 0) + (
        latest_az.get("wind_share_elec", 0) or 0
    )
    prev_sw = (prev_az.get("solar_share_elec", 0) or 0) + (
        prev_az.get("wind_share_elec", 0) or 0
    )
    col3.metric(
        ":material/solar_power: Günəş + Külək Payı",
        f"{solar_wind:.2f}%",
        f"{solar_wind - prev_sw:+.2f}%",
    )

    ci_val = latest_az.get("carbon_intensity_elec", np.nan)
    prev_ci = prev_az.get("carbon_intensity_elec", np.nan)
    if pd.notna(ci_val):
        az_latest_ci = float(ci_val)
    if pd.notna(ci_val) and pd.notna(prev_ci):
        col4.metric(
            ":material/co2: Karbon İntensivliyi",
            f"{ci_val:.0f} qCO₂/kVts",
            f"{ci_val - prev_ci:+.0f} qCO₂",
            delta_color="inverse",
        )

if len(ge_df) >= 1 and pd.notna(ge_df.iloc[-1]["carbon_intensity_elec"]):
    ge_latest_ci = float(ge_df.iloc[-1]["carbon_intensity_elec"])

st.divider()

# ==========================================
# TABLAR (6 İNTERAKTİV BÖLMƏ)
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        ":material/trending_up: Dinamika & Struktur",
        ":material/map: Yaşıl Enerji Xəritəsi",
        ":material/account_balance: Nazir Simulyatoru (2030)",
        ":material/calculate: İşıq Pulu Kalkulyatoru",
        ":material/public: Ekoloji Təsir (CO₂)",
        ":material/database: Açıq Data (CSV)",
    ]
)

# ------------------------------------------
# TAB 1: DİNAMİKA VƏ STRUKTUR
# ------------------------------------------
with tab1:
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown(
            "#### :material/show_chart: Zamanla Dəyişmə: Bərpa Olunan Enerji Payı (%)"
        )
        fig_line = px.line(
            filtered_df,
            x="year",
            y="renewables_share_elec",
            color="country",
            markers=True,
            labels={
                "year": "İl",
                "renewables_share_elec": "Pay (%)",
                "country": "Ölkə",
            },
        )
        fig_line.update_layout(hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        latest_valid_year = int(
            filtered_df.dropna(subset=["renewables_share_elec"])["year"].max()
        )
        latest_slice = filtered_df[filtered_df["year"] == latest_valid_year]

        st.markdown(
            f"#### :material/bar_chart: {latest_valid_year}-ci il: Enerji Mənbələri (%)"
        )
        mix_cols = [
            "fossil_share_elec",
            "hydro_share_elec",
            "solar_share_elec",
            "wind_share_elec",
        ]
        melted = latest_slice.melt(
            id_vars="country",
            value_vars=mix_cols,
            var_name="Mənbə",
            value_name="Pay (%)",
        )
        melted["Mənbə"] = melted["Mənbə"].replace(
            {
                "fossil_share_elec": "Fosil (Qaz/Neft/Kömür)",
                "hydro_share_elec": "Su (Hidro)",
                "solar_share_elec": "Günəş",
                "wind_share_elec": "Külək",
            }
        )
        fig_bar = px.bar(
            melted, x="country", y="Pay (%)", color="Mənbə", barmode="stack"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------
# TAB 2: AZƏRBAYCANIN YAŞIL ENERJİ XƏRİTƏSİ
# ------------------------------------------
with tab2:
    st.markdown("#### :material/map: Azərbaycanın İnteraktiv Yaşıl Enerji Xəritəsi")
    st.caption(
        "Qlobal bazalarda (OWID) ölkədaxili bölgü görünmədiyi üçün əsas yaşıl enerji layihələri "
        "AR Energetika Nazirliyi və AREA-nın açıq məlumatlarına əsasən xəritələşdirilib."
    )

    projects_data = pd.DataFrame(
        [
            {
                "Layihə": "Qaradağ GES",
                "Növ": "Günəş",
                "Güc (MVt)": 230,
                "İnvestor": "Masdar (BƏƏ)",
                "Status": "İstismarda",
                "lat": 40.23,
                "lon": 49.55,
            },
            {
                "Layihə": "Xızı-Abşeron KES",
                "Növ": "Külək",
                "Güc (MVt)": 240,
                "İnvestor": "ACWA Power (S. Ərəbistanı)",
                "Status": "Tikinti / İstismara hazırlıq",
                "lat": 40.78,
                "lon": 49.38,
            },
            {
                "Layihə": "Biləsuvar GES",
                "Növ": "Günəş",
                "Güc (MVt)": 445,
                "İnvestor": "Masdar (BƏƏ)",
                "Status": "Tikinti / İnvestisiya",
                "lat": 39.46,
                "lon": 48.55,
            },
            {
                "Layihə": "Neftçala GES",
                "Növ": "Günəş",
                "Güc (MVt)": 315,
                "İnvestor": "Masdar (BƏƏ)",
                "Status": "Tikinti / İnvestisiya",
                "lat": 39.37,
                "lon": 49.24,
            },
            {
                "Layihə": "Şəfəq GES (Cəbrayıl)",
                "Növ": "Günəş",
                "Güc (MVt)": 240,
                "İnvestor": "bp / SOCAR / AİŞ",
                "Status": "Tikinti / İnvestisiya",
                "lat": 39.40,
                "lon": 47.02,
            },
            {
                "Layihə": "Qarabağ & Şərqi Zəngəzur Kiçik SES-lər",
                "Növ": "Su (Hidro)",
                "Güc (MVt)": 270,
                "İnvestor": "Azərenerji ASC",
                "Status": "İstismarda (Yaşıl Zona)",
                "lat": 39.75,
                "lon": 46.55,
            },
            {
                "Layihə": "Mingəçevir SES",
                "Növ": "Su (Hidro)",
                "Güc (MVt)": 424,
                "İnvestor": "Azərenerji ASC",
                "Status": "İstismarda (Əsas SES)",
                "lat": 40.79,
                "lon": 47.03,
            },
            {
                "Layihə": "Naxçıvan GES-lər",
                "Növ": "Günəş",
                "Güc (MVt)": 39,
                "İnvestor": "Dövlət / Beynəlxalq",
                "Status": "İstismarda",
                "lat": 39.21,
                "lon": 45.41,
            },
        ]
    )

    selected_types = st.multiselect(
        "Xəritədə göstəriləcək enerji növləri:",
        options=["Günəş", "Külək", "Su (Hidro)"],
        default=["Günəş", "Külək", "Su (Hidro)"],
    )
    map_df = projects_data[projects_data["Növ"].isin(selected_types)]

    fig_map = px.scatter_map(
        map_df,
        lat="lat",
        lon="lon",
        size="Güc (MVt)",
        color="Növ",
        hover_name="Layihə",
        hover_data={"İnvestor": True, "Status": True, "Güc (MVt)": True, "lat": False, "lon": False},
        color_discrete_map={"Günəş": "#F59E0B", "Külək": "#10B981", "Su (Hidro)": "#0EA5E9"},
        size_max=28,
        zoom=6.1,
        center={"lat": 40.15, "lon": 47.65},
        map_style="open-street-map",
        height=480
    )
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.dataframe(
        map_df[["Layihə", "Növ", "Güc (MVt)", "İnvestor", "Status"]],
        use_container_width=True,
        hide_index=True,
    )

# ------------------------------------------
# TAB 3: "SƏN ENERGETİKA NAZİRİSƏN!" (2030 SİMULYATORU)
# ------------------------------------------
with tab3:
    st.markdown(
        "#### :material/account_balance: Sən Energetika Nazirisən! — 2030 Strategiya Simulyatoru"
    )
    st.write(
        "Qarşınızda **4.0 Milyard USD** yaşıl enerji investisiya büdcəsi var. "
        "Büdcəni **Günəş**, **Külək** və **Kiçik SES-lər** arasında elə bölün ki, "
        "Azərbaycan 2030-cu ildə **30% bərpa olunan enerji** hədəfinə çatsın!"
    )

    TOTAL_BUDGET = 4000  # Milyon USD
    BASE_DEMAND_2030_GWH = 30000.0  # 30 TWh təxmini 2030 elektrik istehsalı
    BASE_REN_GWH = 1950.0  # Mövcud bərpa olunan istehsal (~6.5%)

    g_col1, g_col2 = st.columns([1, 1.35])

    with g_col1:
        st.markdown("##### :material/payments: Büdcə Bölgüsü (Milyon USD)")
        inv_solar = st.slider(
            ":material/wb_sunny: Günəş stansiyaları (Qaradağ/Biləsuvar/Naxçıvan)",
            0,
            3000,
            1400,
            step=100,
        )
        inv_wind = st.slider(
            ":material/air: Külək stansiyaları (Xızı/Abşeron/Xəzər)",
            0,
            3000,
            1600,
            step=100,
        )
        inv_hydro = st.slider(
            ":material/water_drop: Kiçik SES-lər (Qarabağ/Şərqi Zəngəzur)",
            0,
            2000,
            600,
            step=100,
        )

        spent = inv_solar + inv_wind + inv_hydro
        remaining = TOTAL_BUDGET - spent

        if remaining < 0:
            st.error(
                f"Büdcəni **{abs(remaining)} mln USD** aşdınız! Zəhmət olmasa xərcləri azaldın.",
                icon=":material/warning:",
            )
        else:
            st.info(
                f"Xərclənən: **{spent} mln USD** | Qalan büdcə: **{remaining} mln USD**",
                icon=":material/account_balance_wallet:",
            )

        # Texniki-iqtisadi model (orta qlobal/regional göstəricilər)
        mw_solar = inv_solar / 0.85
        mw_wind = inv_wind / 1.25
        mw_hydro = inv_hydro / 1.80

        gwh_solar = mw_solar * 1.75
        gwh_wind = mw_wind * 2.80
        gwh_hydro = mw_hydro * 3.94

        added_gwh = gwh_solar + gwh_wind + gwh_hydro
        total_ren_2030 = BASE_REN_GWH + added_gwh
        share_2030 = min(100.0, (total_ren_2030 / BASE_DEMAND_2030_GWH) * 100.0)

        # Ekoloji təsir və real həyat analogiyaları
        co2_saved_tons = added_gwh * 420.0
        cars_removed = co2_saved_tons / 4.6
        trees_planted_mln = (co2_saved_tons / 0.022) / 1_000_000

        st.markdown("---")
        if remaining >= 0 and share_2030 >= 30.0:
            st.success(
                f"Təbriklər, cənab Nazir! 2030-da **{share_2030:.1f}%**-ə çatdınız (Hədəf yerinə yetirildi!).",
                icon=":material/check_circle:",
            )
        elif remaining < 0:
            st.warning(
                f"Büdcə aşılıb, lakin bu layihələrlə pay **{share_2030:.1f}%** olardı.",
                icon=":material/warning:",
            )
        else:
            st.error(
                f"2030-da pay yalnız **{share_2030:.1f}%** oldu. 30%-ə çatmaq üçün büdcəni daha səmərəli bölün!",
                icon=":material/cancel:",
            )

    with g_col2:
        last_yr = int(az_df["year"].max())
        last_val = float(
            az_df[az_df["year"] == last_yr]["renewables_share_elec"].values[0]
        )
        fut_yrs = list(range(last_yr, 2031))
        step_yr = (share_2030 - last_val) / (2030 - last_yr)
        proj_vals = [last_val + step_yr * (y - last_yr) for y in fut_yrs]

        fig_game = go.Figure()
        fig_game.add_trace(
            go.Scatter(
                x=az_df["year"],
                y=az_df["renewables_share_elec"],
                mode="lines+markers",
                name="Tarixi Göstərici (Real Data)",
                line=dict(color="#0F172A", width=3),
            )
        )
        fig_game.add_trace(
            go.Scatter(
                x=fut_yrs,
                y=proj_vals,
                mode="lines+markers",
                name="Sizin Strategiyanız (2030)",
                line=dict(
                    color="#10B981" if share_2030 >= 30 else "#F59E0B",
                    width=3.5,
                    dash="dash",
                ),
            )
        )
        fig_game.add_hline(
            y=30,
            line_dash="dot",
            line_color="#EF4444",
            annotation_text="2030 Rəsmi Hədəf (30%)",
            annotation_position="top left",
        )
        fig_game.update_layout(
            title="Azərbaycan: Tarixi Dinamika və Sizin 2030 Strategiyanız",
            xaxis_title="İl",
            yaxis_title="Bərpa Olunan Enerji Payı (%)",
            yaxis=dict(range=[0, max(38, share_2030 + 6)]),
            hovermode="x unified",
            height=340,
        )
        st.plotly_chart(fig_game, use_container_width=True)

        st.markdown(
            "##### :material/eco: Sizin Qərarınızın Real Həyatda Təsiri (İllik)"
        )
        m1, m2, m3 = st.columns(3)
        m1.metric(
            ":material/co2: Azalan CO₂", f"{co2_saved_tons/1_000_000:.2f} mln ton"
        )
        m2.metric(
            ":material/directions_car: Yollardan çıxan maşın",
            f"~{int(cars_removed):,} ədəd".replace(",", " "),
        )
        m3.metric(
            ":material/park: Ağac ekvivalenti", f"~{trees_planted_mln:.1f} mln ağac"
        )

# ------------------------------------------
# TAB 4: ŞƏXSİ İŞIQ PULU VƏ KARBON KALKULYATORU
# ------------------------------------------
with tab4:
    st.markdown("#### :material/calculate: Aylıq İşıq Pulun Nə Qədər Karbon Yaradır?")
    st.write(
        "Evinizin aylıq orta elektrik ödənişini daxil edin — sistem Azərbaycanın real karbon intensivliyi "
        f"(**{az_latest_ci:.0f} qCO₂/kVts**) əsasında illik ekoloji izinizi hesablasın."
    )

    k_col1, k_col2 = st.columns([1, 1.5])

    with k_col1:
        monthly_azn = st.number_input(
            "Aylıq orta işıq pulu (AZN):",
            min_value=5.0,
            max_value=500.0,
            value=35.0,
            step=5.0,
        )
        if monthly_azn <= 16.0:
            monthly_kwh = monthly_azn / 0.08
        elif monthly_azn <= 25.0:
            monthly_kwh = 200.0 + (monthly_azn - 16.0) / 0.09
        else:
            monthly_kwh = 300.0 + (monthly_azn - 25.0) / 0.13

        annual_kwh = monthly_kwh * 12.0
        az_co2_kg = (annual_kwh * az_latest_ci) / 1000.0
        ge_co2_kg = (annual_kwh * ge_latest_ci) / 1000.0
        az_2030_co2_kg = az_co2_kg * 0.75
        trees_needed = az_co2_kg / 22.0

        st.metric(
            ":material/electric_bolt: İllik elektrik sərfiyyatınız",
            f"{annual_kwh:,.0f} kVts".replace(",", " "),
        )
        st.metric(
            ":material/co2: İllik karbon iziniz (Azərbaycan)",
            f"{az_co2_kg:,.0f} kq CO₂".replace(",", " "),
        )
        st.metric(
            ":material/park: Təmizləmək üçün lazım olan ağac",
            f"{int(np.ceil(trees_needed))} ədəd ağac",
        )

    with k_col2:
        comp_df = pd.DataFrame(
            {
                "Ssenari": [
                    "Azərbaycan (İndi)",
                    "Azərbaycan (2030 Hədəfi)",
                    "Gürcüstan (Eyni ev)",
                ],
                "İllik CO₂ (kq)": [az_co2_kg, az_2030_co2_kg, ge_co2_kg],
            }
        )

        fig_pers = px.bar(
            comp_df,
            x="Ssenari",
            y="İllik CO₂ (kq)",
            color="Ssenari",
            color_discrete_sequence=["#EF4444", "#F59E0B", "#10B981"],
            text_auto=".0f",
            title="Eyni evin 1 illik elektrik istehlakının karbon izi müqayisəsi",
        )
        fig_pers.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig_pers, use_container_width=True)

        ratio = az_co2_kg / max(ge_co2_kg, 1.0)
        st.info(
            f"Sizin eviniz eyni işıq sərfiyyatı ilə Gürcüstanda olsaydı, karbon iziniz təxminən "
            f"**{ratio:.1f} dəfə az** olardı. Azərbaycan 2030 hədəfinə çatdıqda isə evinizin karbon izi "
            f"ildə **{az_co2_kg - az_2030_co2_kg:.0f} kq CO₂** azalacaq.",
            icon=":material/info:",
        )

# ------------------------------------------
# TAB 5: EKOLOJİ TƏSİR (CO2)
# ------------------------------------------
with tab5:
    st.markdown(
        "#### :material/public: Bərpa Olunan Enerji vs. Elektrik İstehsalının Karbon İzi"
    )
    st.caption(
        "Hər kVt-saat elektrik istehsalı zamanı atmosferə atılan CO₂ miqdarı (qramla). Nə qədər aşağıdırsa, enerji bir o qədər təmizdir."
    )

    co2_df = filtered_df.dropna(
        subset=["carbon_intensity_elec", "renewables_share_elec"]
    )
    fig_scatter = px.scatter(
        co2_df,
        x="renewables_share_elec",
        y="carbon_intensity_elec",
        color="country",
        size="year",
        hover_data=["year"],
        labels={
            "renewables_share_elec": "Bərpa Olunan Enerji Payı (%)",
            "carbon_intensity_elec": "Karbon İntensivliyi (qCO₂/kVts)",
            "country": "Ölkə",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# TAB 6: AÇIQ DATA VƏ YÜKLƏMƏ
# ------------------------------------------
with tab6:
    st.markdown("#### :material/table_chart: Filtrlənmiş Açıq Data Cədvəli")
    cols_to_show = [
        "country",
        "year",
        "renewables_share_elec",
        "fossil_share_elec",
        "hydro_share_elec",
        "solar_share_elec",
        "wind_share_elec",
        "carbon_intensity_elec",
    ]
    display_df = filtered_df[cols_to_show].sort_values(
        ["country", "year"], ascending=[True, False]
    )
    st.dataframe(display_df, use_container_width=True)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=":material/download: Filtrlənmiş Datanı CSV kimi yüklə",
        data=csv,
        file_name="enerji_analizi_data.csv",
        mime="text/csv",
    )
