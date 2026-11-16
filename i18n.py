"""All human-readable text in uk, en, de, fr, zh: UI strings, domain labels, country names."""

import pandas as pd
import pycountry
from babel import Locale

LANGUAGES: dict[str, str] = {
    "uk": "Українська",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "zh": "中文",
}
DEFAULT_LANG = "uk"
LANG_INDEX: dict[str, int] = {lang: i for i, lang in enumerate(LANGUAGES)}

# Every entry holds one translation per language, in LANGUAGES order.
TEXTS: dict[str, tuple[str, str, str, str, str]] = {
    "page_title": ("Підбір країни", "Country Matcher", "Länderfinder", "Choix du pays", "国家匹配"),
    "subtitle": (
        "Бал 0–100 показує, наскільки країна близька до вашого ідеалу. Налаштуйте пріоритети на бічній панелі.",
        "A 0–100 score shows how close each country is to your ideal. Set your priorities in the sidebar.",
        "Die Punktzahl 0–100 zeigt, wie nah ein Land Ihrem Ideal kommt. Legen Sie Ihre Prioritäten in der "
        "Seitenleiste fest.",
        "Le score de 0 à 100 indique à quel point chaque pays est proche de votre idéal. Réglez vos priorités "
        "dans le panneau latéral.",
        "0–100分表示每个国家与您理想的接近程度。请在侧边栏设置您的优先事项。",
    ),
    "language": ("Мова", "Language", "Sprache", "Langue", "语言"),
    "mode": ("Режим", "Mode", "Modus", "Mode", "模式"),
    "mode.best": ("Найкраща", "Best overall", "Insgesamt am besten", "Meilleur global", "综合最佳"),
    "mode.ideal": ("Мій ідеал", "My ideal", "Mein Ideal", "Mon idéal", "我的理想"),
    "mode.similar": (
        "Схожі на країну", "Similar to a country", "Ähnlich wie ein Land",
        "Semblable à un pays", "与某国相似",
    ),
    "presets": ("Готові профілі", "Ready-made profiles", "Fertige Profile", "Profils prédéfinis", "预设方案"),
    "weights": (
        "Важливість категорій", "Category importance", "Wichtigkeit der Kategorien",
        "Importance des catégories", "类别重要性",
    ),
    "uniform_note": (
        "У цьому режимі всі показники мають рівну вагу.",
        "In this mode all indicators have equal weight.",
        "In diesem Modus sind alle Indikatoren gleich gewichtet.",
        "Dans ce mode, tous les indicateurs ont le même poids.",
        "此模式下所有指标权重相同。",
    ),
    "desired": ("Бажаний рівень", "Desired level", "Gewünschtes Niveau", "Niveau souhaité", "期望水平"),
    "ref_country": ("Країна-зразок", "Reference country", "Referenzland", "Pays de référence", "参照国家"),
    "fine_tune": (
        "Тонке налаштування показників", "Fine-tune indicators", "Indikatoren feinjustieren",
        "Réglage fin des indicateurs", "指标微调",
    ),
    "fine_tune_note": (
        "Множник ваги показника всередині його категорії.",
        "Weight multiplier for an indicator within its category.",
        "Gewichtungsfaktor eines Indikators innerhalb seiner Kategorie.",
        "Multiplicateur de poids d'un indicateur au sein de sa catégorie.",
        "指标在其类别内的权重系数。",
    ),
    "filters": ("Фільтри", "Filters", "Filter", "Filtres", "筛选"),
    "regions": ("Регіони", "Regions", "Regionen", "Régions", "地区"),
    "all_regions": ("Усі регіони", "All regions", "Alle Regionen", "Toutes les régions", "所有地区"),
    "complete_only": (
        "Лише країни з повними даними", "Only countries with complete data",
        "Nur Länder mit vollständigen Daten", "Uniquement les pays aux données complètes",
        "仅显示数据完整的国家",
    ),
    "refresh": (
        "Оновити дані зі Світового банку", "Refresh World Bank data",
        "Weltbank-Daten aktualisieren", "Actualiser les données de la Banque mondiale",
        "从世界银行更新数据",
    ),
    "refresh_error": (
        "Не вдалося завантажити дані зі Світового банку. Перевірте з'єднання з інтернетом.",
        "Could not download World Bank data. Check your internet connection.",
        "Die Weltbank-Daten konnten nicht geladen werden. Prüfen Sie Ihre Internetverbindung.",
        "Impossible de télécharger les données de la Banque mondiale. Vérifiez votre connexion internet.",
        "无法下载世界银行数据，请检查网络连接。",
    ),
    "demo_data": (
        "Демо-дані: натисніть «Оновити дані зі Світового банку», щоб отримати реальні.",
        "Demo data: click “Refresh World Bank data” to load real figures.",
        "Demodaten: Klicken Sie auf „Weltbank-Daten aktualisieren“, um echte Werte zu laden.",
        "Données de démonstration : cliquez sur « Actualiser les données de la Banque mondiale » "
        "pour charger les vraies valeurs.",
        "演示数据：点击“从世界银行更新数据”以加载真实数据。",
    ),
    "no_results": (
        "Немає результатів: задайте ненульову вагу хоча б одній категорії або розширте фільтр регіонів.",
        "No results: give at least one category a non-zero weight or widen the region filter.",
        "Keine Ergebnisse: Geben Sie mindestens einer Kategorie ein Gewicht über null "
        "oder erweitern Sie den Regionenfilter.",
        "Aucun résultat : donnez un poids non nul à au moins une catégorie ou élargissez le filtre "
        "des régions.",
        "没有结果：请至少为一个类别设置非零权重，或放宽地区筛选。",
    ),
    "weakest": (
        "Найбільше відстає: {reasons}", "Weakest areas: {reasons}", "Größte Schwächen: {reasons}",
        "Points les plus faibles : {reasons}", "最薄弱的方面：{reasons}",
    ),
    "tab.rank": ("Рейтинг", "Ranking", "Rangliste", "Classement", "排名"),
    "tab.compare": ("Порівняння", "Comparison", "Vergleich", "Comparaison", "比较"),
    "tab.map": ("Карта", "Map", "Karte", "Carte", "地图"),
    "col.country": ("Країна", "Country", "Land", "Pays", "国家"),
    "col.region": ("Регіон", "Region", "Region", "Région", "地区"),
    "col.score": ("Бал", "Score", "Punktzahl", "Score", "得分"),
    "col.indicator": ("Показник", "Indicator", "Indikator", "Indicateur", "指标"),
    "col.leader": ("Лідер", "Leader", "Spitzenreiter", "Leader", "第一名"),
    "col.gap": ("Різниця", "Gap", "Differenz", "Écart", "差距"),
    "compare_pick": (
        "Країни для порівняння (до 3)", "Countries to compare (up to 3)",
        "Länder zum Vergleich (bis zu 3)", "Pays à comparer (jusqu'à 3)", "要比较的国家（最多3个）",
    ),
    "compare_limit": (
        "Можна порівняти не більше 3 країн — показано перші три.",
        "You can compare up to 3 countries — showing the first three.",
        "Es lassen sich höchstens 3 Länder vergleichen – die ersten drei werden angezeigt.",
        "Vous pouvez comparer 3 pays au maximum — les trois premiers sont affichés.",
        "最多可比较3个国家，仅显示前三个。",
    ),
    "choose": ("Оберіть…", "Choose…", "Auswählen…", "Choisir…", "请选择…"),
    "why_not.title": (
        "Чому не X, а {winner}?", "Why {winner} and not X?", "Warum {winner} und nicht X?",
        "Pourquoi {winner} et pas X ?", "为什么是{winner}而不是X？",
    ),
    "why_not.pick": ("Країна X", "Country X", "Land X", "Pays X", "国家X"),
    "why_not.summary": (
        "**{other}** — {other_score}, **{winner}** — {winner_score}. Праворуч показники, де {other} "
        "втрачає більше балів, ліворуч — де менше.",
        "**{other}** scores {other_score}, **{winner}** {winner_score}. Bars to the right show where "
        "{other} loses more points, bars to the left where it loses fewer.",
        "**{other}** erreicht {other_score}, **{winner}** {winner_score}. Balken nach rechts zeigen, wo "
        "{other} mehr Punkte verliert, Balken nach links, wo weniger.",
        "**{other}** obtient {other_score}, **{winner}** {winner_score}. Les barres à droite montrent où "
        "{other} perd plus de points, celles à gauche où il en perd moins.",
        "**{other}**得{other_score}分，**{winner}**得{winner_score}分。向右的条形表示{other}失分更多的指标，"
        "向左的表示失分更少的指标。",
    ),
    "why_not.details": ("Дані таблицею", "Show as table", "Als Tabelle anzeigen", "Afficher le tableau", "以表格显示"),
    "chart.points_lost": (
        "Втрачено балів до ідеалу", "Points lost vs. the ideal", "Verlorene Punkte zum Ideal",
        "Points perdus par rapport à l'idéal", "与理想相比失去的分数",
    ),
    "chart.gap_axis": (
        "Різниця втрачених балів: {other} − {winner}", "Difference in points lost: {other} − {winner}",
        "Differenz der verlorenen Punkte: {other} − {winner}", "Écart de points perdus : {other} − {winner}",
        "失分差：{other} − {winner}",
    ),
    "chart.ideal": ("Ідеал", "Ideal", "Ideal", "Idéal", "理想"),
    # Categories
    "cat.safety": ("Безпека", "Safety", "Sicherheit", "Sécurité", "安全"),
    "cat.economy": ("Економіка", "Economy", "Wirtschaft", "Économie", "经济"),
    "cat.health": ("Здоров'я", "Health", "Gesundheit", "Santé", "健康"),
    "cat.environment": ("Довкілля", "Environment", "Umwelt", "Environnement", "环境"),
    "cat.governance": ("Врядування", "Governance", "Regierungsführung", "Gouvernance", "治理"),
    "cat.digital": ("Цифровізація", "Digital", "Digitalisierung", "Numérique", "数字化"),
    # Indicators (keyed by config.INDICATORS codes)
    "ind.WB_WDI_VC_IHR_PSRC_P5": (
        "Умисні вбивства на 100 тис.", "Intentional homicides per 100k",
        "Vorsätzliche Tötungen je 100.000", "Homicides volontaires pour 100 000", "每10万人故意杀人数",
    ),
    "ind.WB_WGI_PV_EST": (
        "Політична стабільність", "Political stability", "Politische Stabilität",
        "Stabilité politique", "政治稳定",
    ),
    "ind.WB_WDI_NY_GDP_PCAP_PP_CD": (
        "ВВП на душу (ПКС, $)", "GDP per capita (PPP, $)", "BIP pro Kopf (KKP, $)",
        "PIB par habitant (PPA, $)", "人均GDP（购买力平价，美元）",
    ),
    "ind.WB_WDI_SL_UEM_TOTL_ZS": ("Безробіття, %", "Unemployment, %", "Arbeitslosigkeit, %", "Chômage, %", "失业率，%"),
    "ind.WB_WDI_FP_CPI_TOTL_ZG": ("Інфляція, %", "Inflation, %", "Inflation, %", "Inflation, %", "通货膨胀率，%"),
    "ind.WB_WDI_SP_DYN_LE00_IN": (
        "Очікувана тривалість життя", "Life expectancy", "Lebenserwartung", "Espérance de vie", "预期寿命",
    ),
    "ind.WB_WDI_SH_XPD_CHEX_PC_CD": (
        "Витрати на охорону здоров'я на душу, $", "Health spending per capita, $",
        "Gesundheitsausgaben pro Kopf, $", "Dépenses de santé par habitant, $", "人均卫生支出，美元",
    ),
    "ind.WB_WDI_EN_ATM_PM25_MC_M3": (
        "Забруднення повітря PM2.5", "Air pollution (PM2.5)", "Luftverschmutzung (PM2,5)",
        "Pollution de l'air (PM2,5)", "空气污染（PM2.5）",
    ),
    "ind.WB_WGI_CC_EST": (
        "Контроль корупції", "Control of corruption", "Korruptionskontrolle",
        "Maîtrise de la corruption", "腐败控制",
    ),
    "ind.WB_WDI_IT_NET_USER_ZS": (
        "Користувачі інтернету, %", "Internet users, %", "Internetnutzer, %", "Internautes, %", "互联网用户，%",
    ),
    # Presets (keyed by their id in presets.py)
    "preset.student": ("Студент", "Student", "Student", "Étudiant", "学生"),
    "preset.remote": (
        "Віддалений працівник", "Remote worker", "Remote-Beschäftigte", "Télétravailleur", "远程工作者",
    ),
    "preset.family": (
        "Сім'я з дітьми", "Family with children", "Familie mit Kindern", "Famille avec enfants",
        "有孩子的家庭",
    ),
    # World Bank regions (keyed by their English name in the dataset)
    "region.East Asia & Pacific": (
        "Східна Азія і Тихоокеанський регіон", "East Asia & Pacific", "Ostasien und Pazifik",
        "Asie de l'Est et Pacifique", "东亚与太平洋",
    ),
    "region.Europe & Central Asia": (
        "Європа і Центральна Азія", "Europe & Central Asia", "Europa und Zentralasien",
        "Europe et Asie centrale", "欧洲与中亚",
    ),
    "region.Latin America & Caribbean": (
        "Латинська Америка і Карибський басейн", "Latin America & Caribbean",
        "Lateinamerika und Karibik", "Amérique latine et Caraïbes", "拉丁美洲和加勒比",
    ),
    "region.Middle East, North Africa, Afghanistan & Pakistan": (
        "Близький Схід, Північна Африка, Афганістан і Пакистан",
        "Middle East, North Africa, Afghanistan & Pakistan",
        "Naher Osten, Nordafrika, Afghanistan und Pakistan",
        "Moyen-Orient, Afrique du Nord, Afghanistan et Pakistan", "中东、北非、阿富汗和巴基斯坦",
    ),
    "region.Middle East & North Africa": (
        "Близький Схід і Північна Африка", "Middle East & North Africa", "Naher Osten und Nordafrika",
        "Moyen-Orient et Afrique du Nord", "中东和北非",
    ),
    "region.North America": ("Північна Америка", "North America", "Nordamerika", "Amérique du Nord", "北美"),
    "region.South Asia": ("Південна Азія", "South Asia", "Südasien", "Asie du Sud", "南亚"),
    "region.Sub-Saharan Africa": (
        "Африка на південь від Сахари", "Sub-Saharan Africa", "Subsahara-Afrika",
        "Afrique subsaharienne", "撒哈拉以南非洲",
    ),
    # Economies without an ISO 3166 / CLDR entry
    "country.CHI": ("Нормандські острови", "Channel Islands", "Kanalinseln", "Îles Anglo-Normandes", "海峡群岛"),
}

ALPHA2_OVERRIDES: dict[str, str] = {"XKX": "XK"}  # World Bank code -> CLDR territory


def t(key: str, lang: str, **fmt: object) -> str:
    """Translated text for `key`, with `{placeholders}` filled from `fmt`."""
    text = TEXTS[key][LANG_INDEX[lang]]
    return text.format(**fmt) if fmt else text


def label(prefix: str, name: str, lang: str) -> str:
    """Translated name of a category/indicator/preset/region; unknown regions stay as-is."""
    key = f"{prefix}.{name}"
    return t(key, lang) if key in TEXTS else name


def _alpha2(iso3: str) -> str | None:
    """ISO alpha-2 code used by CLDR for a World Bank iso3 code."""
    if iso3 in ALPHA2_OVERRIDES:
        return ALPHA2_OVERRIDES[iso3]
    country = pycountry.countries.get(alpha_3=iso3)
    return country.alpha_2 if country else None


def country_names(fallback: pd.Series, lang: str) -> pd.Series:
    """Country names in `lang` (CLDR), indexed by iso3; `fallback` covers unknown codes."""
    territories = Locale.parse(lang).territories

    def name(iso3: str) -> str:
        if f"country.{iso3}" in TEXTS:
            return t(f"country.{iso3}", lang)
        return territories.get(_alpha2(iso3) or "", fallback[iso3])

    return pd.Series({iso3: name(iso3) for iso3 in fallback.index}, name="country")
